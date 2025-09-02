#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-rdm (see https://github.com/oarepo/oarepo-rdm).
#
# oarepo-rdm is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Presets for enabling OAI endpoint on the model."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, override

from oarepo_model.customizations import Customization, PatchJSONFile
from oarepo_model.presets import Preset

if TYPE_CHECKING:
    from collections.abc import Generator

    from oarepo_model.builder import InvenioModelBuilder
    from oarepo_model.model import InvenioModel


class OAIMappingAliasPreset(Preset):
    """Add oaisource alias to record mapping."""

    modifies = ("record-mapping",)

    @override
    def apply(
        self,
        builder: InvenioModelBuilder,
        model: InvenioModel,
        dependencies: dict[str, Any],
    ) -> Generator[Customization]:
        yield PatchJSONFile(
            "record-mapping",
            {
                "aliases": {"oaisource": {}},
            },
        )


class OAIDraftMappingAliasPreset(Preset):
    """Remove oaisource alias from draft mapping.

    We need to do this as draft mapping is a copy of record mapping
    and will thus contain the oaisource from the preset above. Drafts
    should not be harvestable, so need to remove that.
    """

    modifies = ("draft-mapping",)
    only_if = ("draft-mapping",)

    @override
    def apply(
        self,
        builder: InvenioModelBuilder,
        model: InvenioModel,
        dependencies: dict[str, Any],
    ) -> Generator[Customization]:
        def remove_oaisource(mapping: dict[str, Any]) -> dict[str, Any]:
            mapping.get("aliases", {}).pop("oaisource", None)
            return mapping

        yield PatchJSONFile(
            "draft-mapping",
            remove_oaisource,
        )


oai_preset = [OAIMappingAliasPreset, OAIDraftMappingAliasPreset]
