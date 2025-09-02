#
# Copyright (C) 2025 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""oarepo oaiserver serializer functions."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from lxml import etree
from oarepo_runtime import current_runtime

if TYPE_CHECKING:
    from flask_resources.serializers import BaseSerializer


def multiplexing_oai_serializer(
    pid: Any,  # noqa: ARG001 # invenio callback api needs this
    record: dict[str, Any],
    model_serializers: dict[str, BaseSerializer],
    **serializer_kwargs: Any,  # noqa: ARG001 # invenio callback api needs this
) -> etree._Element:
    """Multiplexing OAI serializer that dispatches to the correct model serializer.

    :param pid: The PID of the record.
    :param record: The opensearch serialization of the record, [_source] is the record data.
    :param model_serializers: A mapping of JSON schema identifiers to their corresponding serializers.
    :param serializer_kwargs: Additional keyword arguments for the serializer, not used.
    """
    source = record["_source"]
    json_schema = source.get("$schema")
    if not json_schema:
        raise ValueError(f"Missing JSON schema on record {record}")
    model = current_runtime.models_by_schema[json_schema]
    loaded_record = model.record_cls.loads(source)
    resp = cast("str", model_serializers[json_schema].serialize_object(loaded_record))
    return etree.fromstring(resp.encode("utf-8"))
