#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-rdm (see https://github.com/oarepo/oarepo-rdm).
#
# oarepo-rdm is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""UI serializer for RDM records."""

from __future__ import annotations

from typing import ClassVar

from invenio_rdm_records.resources.config import RDMRecordResourceConfig


class OARepoRDMRecordResourceConfig(RDMRecordResourceConfig):
    """OARepo extension to RDM record resource configuration."""

    routes: ClassVar[dict[str, str]] = {
        **RDMRecordResourceConfig.routes,
        "all-prefix": "/all",  # /api/all/records
    }
