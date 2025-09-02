#
# Copyright (C) 2025 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""invenio-oaiserver config extensions."""

from __future__ import annotations

from collections import defaultdict
from functools import cached_property
from typing import TYPE_CHECKING, Any, override

from oarepo_runtime import current_runtime

from .serializer import multiplexing_oai_serializer

if TYPE_CHECKING:
    Dict = dict
else:
    Dict = object


class OAIServerMetadataFormats(Dict):
    """Metadata formats for the OAI server.

    InvenioRDM uses a static dict of formats, we need to get it from the specialized
    models. We also can not use LazyProxy here because it would have been evaluated
    too early.
    """

    @override
    def __contains__(self, key: Any) -> bool:
        return key in self._metadata_formats

    @override
    def __getitem__(self, key: Any) -> Any:
        return self._metadata_formats[key]

    @override
    def items(self) -> Any:
        return self._metadata_formats.items()

    @override
    def keys(self) -> Any:
        return self._metadata_formats.keys()

    @override
    def values(self) -> Any:
        return self._metadata_formats.values()

    @override
    def __len__(self):
        return len(self._metadata_formats)

    @cached_property
    def _metadata_formats(self) -> dict:
        """Return a dictionary of metadata formats.

        The dict has the same structure as in invenio_rdm_records.config:OAISERVER_METADATA_FORMATS

        ```
        OAISERVER_METADATA_FORMATS = {
            "marcxml": {
                "serializer": "invenio_rdm_records.oai:marcxml_etree",
                "schema": "https://www.loc.gov/standards/marcxml/schema/MARC21slim.xsd",
                "namespace": "https://www.loc.gov/standards/marcxml/",
            },
        ```
        """
        infos = defaultdict[str, list](list)
        for model in current_runtime.rdm_models:
            for export in model.exports:
                if not export.oai_metadata_prefix:
                    continue
                infos[export.oai_metadata_prefix].append(
                    {
                        "namespace": export.oai_namespace,
                        "schema": export.oai_schema,
                        "model_schema": model.record_cls.schema.value,  # type: ignore[reportAttributeAccessIssue]
                        "serializer": export.serializer,
                    }
                )

        # now if there are multiple entries for a single metadata prefix,
        # check that the namespace and schema are the same. Then create a single
        # entry with a multiplexing serializer
        ret = {}
        for key, serialization_infos in infos.items():
            if len(serialization_infos) == 1:
                serialization_infos[0].pop("model_schema")
                ret[key] = serialization_infos[0]
                continue
            if len({x["namespace"] for x in serialization_infos}) != 1:
                raise ValueError(
                    f"Multiple different namespaces for OAI metadata prefix {key}: "
                    f"{[x['namespace'] for x in serialization_infos]}"
                )
            if len({x["schema"] for x in serialization_infos}) != 1:
                raise ValueError(
                    f"Multiple different schemas for OAI metadata prefix {key}: "
                    f"{[x['schema'] for x in serialization_infos]}"
                )
            ret[key] = {
                "namespace": serialization_infos[0]["namespace"],
                "schema": serialization_infos[0]["schema"],
                "serializer": (
                    multiplexing_oai_serializer,
                    {"model_serializers": {x["model_schema"]: x["serializer"] for x in serialization_infos}},
                ),
            }
        return ret
