#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-rdm (see https://github.com/oarepo/oarepo-rdm).
#
# oarepo-rdm is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Resource layer."""

from __future__ import annotations

from typing import Any, override

from flask import g
from flask_resources import (
    resource_requestctx,
    response_handler,
    route,
)
from invenio_rdm_records.resources.resources import RDMRecordResource
from invenio_records_resources.resources.records.resource import request_search_args


class OARepoRDMRecordResource(RDMRecordResource):
    """OARepo RDM Record Resource."""

    @override
    def create_url_rules(self) -> Any:
        all_records_route = f"{self.config.routes['all-prefix']}{self.config.url_prefix}"

        rules = super().create_url_rules()
        rules += [
            # Custom route for all records
            route("GET", all_records_route, self.search_all_records),
        ]
        return rules

    @request_search_args
    @response_handler(many=True)
    def search_all_records(self) -> tuple[dict[str, Any], int]:
        """Search all records, regardless if they are published or not."""
        items = self.service.search_all_records(
            g.identity,
            params=resource_requestctx.args,  # type: ignore[attr-defined]
        )
        return items.to_dict(), 200
