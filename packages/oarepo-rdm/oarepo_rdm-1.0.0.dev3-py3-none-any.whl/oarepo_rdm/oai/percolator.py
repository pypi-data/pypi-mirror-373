#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-rdm (see https://github.com/oarepo/oarepo-rdm).
#
# oarepo-rdm is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""percolators extensions.

InvenioRDM contains partial support for multiple percolators, that is not
working in some places. We work around it by:

1. Declaring a single alias, `OAISERVER_RECORD_INDEX`, that is present on all records
2. During `invenio search init`, we create a single percolator index called
   `{OAISERVER_RECORD_INDEX}-percolator` and merge mappings from all the models
   into this single percolator index. This means that all models must have consistent
   mappings for shared properties.
3. If you do not have consistent models, add OAREPO_PERCOLATOR_MAPPING to your config.
   This should be a function receiving a list of models and returning a json mapping
   with non-conflicting parts only.
4. Invenio then continues as normal, using the merged percolator index for search
   queries.
"""

from __future__ import annotations

from typing import Any

from deepmerge import always_merger
from flask import current_app
from invenio_search import current_search_client
from invenio_search.utils import build_index_name


def init_percolators() -> None:
    """Initialize OAI percolators.

    This call will fetch all known indices from the opensearch, select the ones
    that should be merged into the percolated index. It will also add prefixes
    to the `oaisource` aliases.
    """
    oaiserver_record_index = str(current_app.config["OAISERVER_RECORD_INDEX"])
    prefixed_oaiserver_record_index = build_index_name(oaiserver_record_index, suffix="", app=current_app)

    percolated_mappings = _get_percolated_mappings(oaiserver_record_index, prefixed_oaiserver_record_index)
    if not percolated_mappings:
        return

    _generate_percolator_index(percolated_mappings)

    # add the local alias to all indices that had the oaiserver alias
    # we can not do it when the model is generated as we do not have
    # the app yet and the app defines the opensearch prefix.
    # that is why it is deferred here.
    #
    # TODO: one could use __SEARCH_INDEX_PREFIX__ but this one works
    # only for templates, not for actual indices. We might suggest
    # a change to invenio to start supporting this.
    for index_name, mapping in percolated_mappings.items():
        if prefixed_oaiserver_record_index not in mapping["aliases"]:
            current_search_client.indices.put_alias(  # type: ignore[attr-defined]
                index_name, prefixed_oaiserver_record_index
            )


def _generate_percolator_index(percolated_mappings: dict[str, dict]) -> None:
    mapping = current_app.config.get("OAREPO_PERCOLATOR_MAPPING", _create_default_percolator_mapping)(
        percolated_mappings
    )

    mapping["mappings"]["properties"]["query"] = {"type": "percolator"}

    record_index = str(current_app.config["OAISERVER_RECORD_INDEX"])
    percolator_index = build_index_name(record_index + "-percolators", suffix="", app=current_app)

    # remove the previous percolator index and build it again
    if current_search_client.indices.exists(percolator_index):  # type: ignore[attr-defined]
        current_search_client.indices.delete(percolator_index)  # type: ignore[attr-defined]

    current_search_client.indices.create(index=percolator_index, body=mapping)  # type: ignore[attr-defined]


def _get_percolated_mappings(oaiserver_record_index: str, prefixed_oaiserver_record_index: str) -> dict[str, dict]:
    indices = current_search_client.indices.get("*")  # type: ignore[attr-defined]

    return {
        index_name: index
        for index_name, index in indices.items()
        if (oaiserver_record_index in index["aliases"] or prefixed_oaiserver_record_index in index["aliases"])
    }


def _create_default_percolator_mapping(mappings: dict[str, dict]) -> dict:
    """Merge all mappings into a single one."""
    # for each models, get the mapping
    percolator_mapping: dict = {}

    for settings in mappings.values():
        if not percolator_mapping:
            percolator_mapping = settings["mappings"]
        else:
            percolator_mapping = always_merger.merge(percolator_mapping, settings["mappings"])

    # dynamic_templates
    if "dynamic_templates" in percolator_mapping:
        percolator_mapping["dynamic_templates"] = _merge_dynamic_templates(percolator_mapping["dynamic_templates"])

    # TODO: analyzers and so on
    return {"mappings": percolator_mapping}


def _merge_dynamic_templates(dynamic_templates: list[dict]) -> list[dict[str, Any]]:
    """Merge dynamic templates into the percolator mapping.

    Dynamic templates define, for example, mapping of pid fields. It is a list
    of dictionaries of type {"single_key": {definition}}, each describing a mapping
    for a specific field.

    We merge them by applying always_merger for each of the fields.
    """
    output: dict[str, Any] = {}
    for template in dynamic_templates:
        output = always_merger.merge(output, template)
    # split the output dict to individual templates
    return [{key: definition} for key, definition in output.items()]
