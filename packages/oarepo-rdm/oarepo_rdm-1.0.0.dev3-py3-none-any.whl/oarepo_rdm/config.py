#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-rdm (see https://github.com/oarepo/oarepo-rdm).
#
# oarepo-rdm is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Configuration for OAI persistent identifiers."""

from __future__ import annotations

from invenio_i18n import lazy_gettext as _
from invenio_rdm_records.services.pids import providers

RDM_PERSISTENT_IDENTIFIER_PROVIDERS = [
    providers.OAIPIDProvider(
        "oai",
        label=_("OAI ID"),
    ),
]

RDM_PERSISTENT_IDENTIFIERS = {
    "oai": {
        "providers": ["oai"],
        "required": True,
        "label": _("OAI"),
        "is_enabled": providers.OAIPIDProvider.is_enabled,
    },
}
