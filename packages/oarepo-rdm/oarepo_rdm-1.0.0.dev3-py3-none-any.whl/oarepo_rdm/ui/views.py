#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-rdm (see https://github.com/oarepo/oarepo-rdm).
#
# oarepo-rdm is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""UI blueprints for invenio-app-rdm."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from flask import Blueprint, Flask
from invenio_access.permissions import system_identity
from invenio_app_rdm.records_ui.views.decorators import (
    pass_include_deleted,
)
from invenio_app_rdm.views import create_url_rule
from invenio_records_resources.proxies import current_service_registry
from werkzeug.utils import redirect

if TYPE_CHECKING:
    from werkzeug import Response


def create_records_blueprint(app: Flask) -> Blueprint:
    """Create the UI blueprint for the RDM records."""
    blueprint = Blueprint("invenio_app_rdm_records", __name__)
    routes: dict[str, Any] = cast("dict[str, Any]", app.config.get("APP_RDM_ROUTES"))
    blueprint.add_url_rule(
        **create_url_rule(
            routes["record_detail"],
            default_view_func=record_detail,
        )
    )
    return blueprint


@pass_include_deleted
def record_detail(pid_value: str, include_deleted: bool = False) -> Response:
    """Redirect to the record detail page."""
    service = current_service_registry.get("records")  # type: ignore[attr-defined]
    rec = service.read(system_identity, pid_value, include_deleted=include_deleted)
    data = rec.to_dict()
    self_html = data["links"]["self_html"]
    return redirect(self_html)
