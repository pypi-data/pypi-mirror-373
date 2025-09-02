#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-rdm (see https://github.com/oarepo/oarepo-rdm).
#
# oarepo-rdm is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Proxies for the RDM extension."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flask import current_app
from werkzeug.local import LocalProxy

if TYPE_CHECKING:
    from oarepo_rdm.ext import OARepoRDM

    current_oarepo_rdm: OARepoRDM


current_oarepo_rdm = LocalProxy(lambda: current_app.extensions["oarepo-rdm"])  # type: ignore[assignment]
