#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-rdm (see https://github.com/oarepo/oarepo-rdm).
#
# oarepo-rdm is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""OARepo extensions for invenio-rdm-records and invenio-app-rdm."""

from __future__ import annotations

from .model.presets import rdm_preset

__version__ = "1.0.0dev3"
"""Version of the library."""

__all__ = ("__version__", "rdm_preset")
