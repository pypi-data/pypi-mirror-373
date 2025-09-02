#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-rdm (see https://github.com/oarepo/oarepo-rdm).
#
# oarepo-rdm is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Initial configuration which replaces RDM service with oarepo extensions."""

from __future__ import annotations

from typing import Any

from flask import current_app
from invenio_app_rdm import config as rdm_config  # noqa
from werkzeug.local import LocalProxy

from oarepo_rdm.oai.config import OAIServerMetadataFormats

# TODO: Why not to add other RDM routes here?
APP_RDM_ROUTES = {
    "record_detail": "/records/<pid_value>",
    "record_file_download": "/records/<pid_value>/files/<path:filename>",
}


RDM_RECORDS_SERVICE_CONFIG_CLASS = "oarepo_rdm.services.config:OARepoRDMServiceConfig"
"""Service config class."""

RDM_RECORDS_SERVICE_CLASS = "oarepo_rdm.services.service:OARepoRDMService"
"""Replacement for the plain RDM service class."""

RDM_RECORDS_RESOURCE_CONFIG_CLASS = "oarepo_rdm.resources.records.config:OARepoRDMRecordResourceConfig"
"""Resource config class."""

RDM_RECORDS_RESOURCE_CLASS = "oarepo_rdm.resources.records.resource:OARepoRDMRecordResource"
"""Replacement for the plain RDM resource class."""


# OAI-PMH
# =======
# See https://github.com/inveniosoftware/invenio-oaiserver/blob/master/invenio_oaiserver/config.py
# (Using GitHub because documentation site out-of-sync at time of writing)


def _site_name(site_url: str) -> str:
    """Get the site name from the URL."""
    # get just the host from the url
    return site_url.split("//")[-1].split("/")[0]


OAISERVER_ID_PREFIX = LocalProxy(lambda: _site_name(current_app.config["SITE_UI_URL"]))
"""The prefix that will be applied to the generated OAI-PMH ids."""

OAISERVER_SEARCH_CLS = "invenio_rdm_records.oai:OAIRecordSearch"
"""Class for record search."""

OAISERVER_ID_FETCHER = "invenio_rdm_records.oai:oaiid_fetcher"
"""OAI ID fetcher function."""

OAISERVER_METADATA_FORMATS = OAIServerMetadataFormats()

OAISERVER_LAST_UPDATE_KEY = "updated"
"""Record update key."""

OAISERVER_CREATED_KEY = "created"
"""Record created key."""

OAISERVER_RECORD_CLS = "invenio_rdm_records.records.api:RDMRecord"
"""Record retrieval class."""

OAISERVER_RECORD_SETS_FETCHER = "invenio_oaiserver.percolator:find_sets_for_record"
"""Record's OAI sets function."""

OAISERVER_RECORD_INDEX = "oaisource"
"""oaisource is a mapping alias for records that can be sent over OAI-PMH.

To mark your model as oaisource, add `oarepo_rdm.oai.oai_presets` to your model's presets."""

# TODO: oarepo extension, maybe not needed
OAISERVER_RECORD_LIST_SETS_FETCHER = "invenio_oaiserver.percolator:sets_search_all"

"""Specify a search index with records that should be exposed via OAI-PMH."""

OAISERVER_GETRECORD_FETCHER = "invenio_rdm_records.oai:getrecord_fetcher"
"""Record data fetcher for serialization."""

# extra oarepo extensions - TODO: maybe not needed
OAISERVER_NEW_PERCOLATOR_FUNCTION = "invenio_oaiserver.percolator:_new_percolator"
# TODO: maybe not needed
OAISERVER_DELETE_PERCOLATOR_FUNCTION = "invenio_oaiserver.percolator:_delete_percolator"

# cleared rest endpoints
RECORDS_REST_ENDPOINTS: list[Any] = []
