#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-rdm (see https://github.com/oarepo/oarepo-rdm).
#
# oarepo-rdm is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""PID context for specialized RDM records."""

from __future__ import annotations

from typing import TYPE_CHECKING, override

from invenio_records_resources.records.systemfields.pid import PIDFieldContext
from oarepo_runtime import current_runtime

if TYPE_CHECKING:
    from invenio_records_resources.records.api import Record


class OARepoPIDFieldContext(PIDFieldContext):
    """PIDField context.

    Unlike normal pid context, this one returns specialized records by pid type.
    """

    @override
    def resolve(self, pid_value: str, registered_only: bool = False, with_deleted: bool = False) -> Record:
        """Resolve identifier."""
        record_cls = current_runtime.record_class_by_pid_type[current_runtime.find_pid_type_from_pid(pid_value)]
        return record_cls.pid.resolve(  # type: ignore[no-any-return, attr-defined]
            pid_value, registered_only=registered_only, with_deleted=with_deleted
        )


class OARepoDraftPIDFieldContext(OARepoPIDFieldContext):
    """PIDField context for draft records.

    Unlike normal pid context, this one returns specialized records by pid type.
    """

    @override
    def resolve(self, pid_value: str, registered_only: bool = False, with_deleted: bool = False) -> Record:
        """Resolve identifier."""
        record_cls = current_runtime.draft_class_by_pid_type[current_runtime.find_pid_type_from_pid(pid_value)]
        return record_cls.pid.resolve(  # type: ignore[no-any-return, attr-defined]
            pid_value, registered_only=registered_only, with_deleted=with_deleted
        )
