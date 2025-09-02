#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-rdm (see https://github.com/oarepo/oarepo-rdm).
#
# oarepo-rdm is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Multiplexing result list."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from invenio_rdm_records.services.results import RDMRecordList
from oarepo_runtime import current_runtime

if TYPE_CHECKING:
    from collections.abc import Generator


class MultiplexingResultList(RDMRecordList):
    """Multiplexing result list for the RDM service."""

    @property
    def hits(self) -> Generator[dict[str, Any]]:
        """Iterator over the hits."""
        for hit in self._results:
            # Load dump
            record_dict = hit.to_dict()

            schema = hit["$schema"]
            publication_status = hit.get("publication_status", "published")

            delegated_model = current_runtime.rdm_models_by_schema[schema]
            delegated_service = delegated_model.service

            if publication_status == "draft":
                record = delegated_service.draft_cls.loads(record_dict)  # type: ignore[reportAttributeAccessIssue]
            else:
                record = delegated_service.record_cls.loads(record_dict)

            # Project the record
            projection = delegated_service.schema.dump(
                record,
                context={
                    "identity": self._identity,
                    "record": record,
                    "meta": hit.meta,
                },
            )
            if self._links_item_tpl:
                projection["links"] = delegated_service.links_item_tpl.expand(self._identity, record)

            yield projection
