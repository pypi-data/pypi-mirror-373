#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-rdm (see https://github.com/oarepo/oarepo-rdm).
#
# oarepo-rdm is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""RDM service extension to use specialized records instead of generic RDM records."""

from __future__ import annotations

import copy
from typing import TYPE_CHECKING, Any, Literal, cast, override

from invenio_rdm_records.services.services import RDMRecordService
from invenio_records_resources.services.uow import UnitOfWork, unit_of_work
from oarepo_runtime.proxies import current_runtime
from werkzeug.exceptions import Forbidden

from oarepo_rdm.errors import UndefinedModelError

from .config import MultiplexingLinks, MultiplexingSchema

if TYPE_CHECKING:
    import datetime
    from collections.abc import Callable, Iterable

    from invenio_access.permissions import Identity
    from invenio_records_resources.services.records.results import (
        RecordItem,
    )
    from invenio_records_resources.services.records.service import ServiceSchemaWrapper
    from invenio_search import RecordsSearchV2
    from oarepo_runtime.api import Model


pass_through = {
    "create_search",
    "search_request",
    "check_revision_id",
    "read_many",
    "read_all",
    "delete",
    "permission_policy",
    "check_permission",
    "require_permission",
    "run_components",
    "result_item",
    "result_list",
    "record_to_index",
    "scan_expired_embargos",
    "exists",
    "cleanup_record",
    "search_revisions",
    "read_revision",
    "create_or_update_many",
    "result_bulk_item",
    "result_bulk_list",
    # out of place
    "set_user_quota",
    "search",
    "search_drafts",
    "scan",
}


def check_fully_overridden(
    pass_through: Iterable[str], base_class: type
) -> Callable[[type[OARepoRDMService]], type[OARepoRDMService]]:
    """Check that all methods are fully overridden in the subclass."""

    def wrapper(cls: type) -> type:
        # go through base classes and check if methods defined on them
        # are either in the list of exceptions, or are overriden in the class
        for name, value in base_class.__dict__.items():
            if not callable(value) or name.startswith("_") or name in pass_through:
                continue

            this_class_value = cls.__dict__.get(name, None)
            if this_class_value is value:
                raise TypeError(f"Method with name {value.__qualname__} is not overridden in OARepoRDMService.")
        return cls

    return wrapper


def pass_to_specialized_service(
    method_names: Iterable[str],
) -> Callable[[type[OARepoRDMService]], type[OARepoRDMService]]:
    """Pass the call to the specialized service.

    The service is selected by converting the id to pid type and resolving
    the service by pid type.
    """

    def make_delegate(method_name: str) -> Callable[..., Any]:
        def delegate(self: OARepoRDMService, *args: Any, **kwargs: Any) -> Any:
            # might be called with positional arguments (almost always)
            # or with keyword arguments (lift embargoes are called this way)
            if "id_" in kwargs:
                id_ = kwargs["id_"]
            elif "_id" in kwargs:
                # lift_embargo is the only one having it this way
                id_ = kwargs["_id"]
            else:
                # called as (identity, id_)
                id_ = args[1]

            specialized_service = self._get_specialized_service(id_)
            method = getattr(specialized_service, method_name)
            return method(*args, **kwargs)

        return delegate

    def wrapper(cls: type[OARepoRDMService]) -> type[OARepoRDMService]:
        overriden_methods = {}
        for name in method_names:
            if not hasattr(cls, name):
                raise TypeError(f"Method {name} is not implemented in {cls.__name__}")
            overriden_methods[name] = make_delegate(name)
        return type(cls.__name__, (cls,), overriden_methods)

    return wrapper


@check_fully_overridden(pass_through, RDMRecordService)
@pass_to_specialized_service(
    [
        "read",
        "read_draft",
        "read_latest",
        "scan_versions",
        "search_versions",
        "update",
        "update_draft",
        "validate_draft",
        "edit",
        "new_version",
        "import_files",
        "delete_record",
        "delete_draft",
        "update_tombstone",
        "publish",
        "set_quota",
        "mark_record_for_purge",
        "purge_record",
        "restore_record",
        "unmark_record_for_purge",
        "lift_embargo",
    ]
)
class OARepoRDMService(RDMRecordService):
    """RDM service replacement that delegates calls to a specialized services.

    For methods that accept record id, it does so by looking up the persistent identifier
    type and delegating to the service that handles that PID type.

    For create method, it looks at the jsonschema declaration in the data ("$schema" top-level
    property), looks up the service by this schema and calls it.

    Searches have specific handling - a query is run against all the indices and
    then the results are converted to appropripate result classes.
    """

    def _get_specialized_service(self, pid_value: str) -> RDMRecordService:
        """Get a specialized service based on the pid_value of the record."""
        pid_type = current_runtime.find_pid_type_from_pid(pid_value)
        return cast("RDMRecordService", current_runtime.model_by_pid_type[pid_type].service)

    @property
    def links_item_tpl(self) -> MultiplexingLinks:
        """Item links template."""
        return MultiplexingLinks()

    @property
    def schema(self) -> ServiceSchemaWrapper:
        """Schema for the service."""
        return MultiplexingSchema(self, None)

    @unit_of_work()
    @override
    def create(  # pyright: reportIncompatibleMethodOverride=False # type: ignore[override]
        self,
        identity: Identity,
        data: dict[str, Any],
        uow: UnitOfWork | None = None,
        expand: bool = False,
        schema: str | None = None,
        **kwargs: Any,
    ) -> RecordItem:
        """Create a draft for a new record.

        It does NOT eagerly create the associated record.
        """
        model = self._get_model_from_record_data(data, schema=schema)
        return cast(
            "RecordItem",
            model.service.create(identity=identity, data=data, uow=uow, expand=expand, **kwargs),
        )

    def _get_model_from_record_data(self, data: dict[str, Any], schema: str | None = None) -> Model:
        """Get the model from the record data."""
        if "$schema" in data:
            schema = data["$schema"]

        if schema is None:
            if len(current_runtime.rdm_models_by_schema) > 1:
                raise UndefinedModelError(
                    "Cannot create a draft without specifying its type. Please add top-level $schema property."
                )
            return next(iter(current_runtime.rdm_models_by_schema.values()))
        if schema in current_runtime.rdm_models_by_schema:
            return current_runtime.rdm_models_by_schema[schema]
        raise UndefinedModelError(f"Model for schema {schema} does not exist.")

    @override
    def _search(
        self,
        action: str,
        identity: Identity,
        params: dict[str, Any],
        search_preference: str | None,
        record_cls: type[RecordItem] | None = None,
        search_opts: Any | None = None,
        extra_filter: Any | None = None,
        permission_action: str = "read",
        versioning: bool = True,
        **kwargs: Any,
    ) -> RecordsSearchV2:
        """Create the search engine DSL."""
        params.update(kwargs)
        # get services that can handle the search request [pid_type -> service]
        services = self._search_eligible_services(identity, permission_action, **kwargs)
        if not services:
            raise Forbidden

        queries_list: dict[str, dict] = {}

        for jsonschema, service in services.items():
            search = service._search(  # noqa: SLF001 # calling the same method on delegated
                action=action,
                identity=identity,
                params=copy.deepcopy(params),
                search_preference=search_preference,
                record_cls=record_cls,
                search_opts=self._search_options(service, search_opts),
                extra_filter=extra_filter,
                permission_action=permission_action,
                versioning=versioning,
                **kwargs,
            )
            queries_list[jsonschema] = search.to_dict()

        params["delegated_query"] = [queries_list, search_opts or self.config.search]

        return super()._search(
            action=action,
            identity=identity,
            params=params,
            search_preference=search_preference,
            record_cls=record_cls,
            search_opts=search_opts,
            extra_filter=extra_filter,
            permission_action=permission_action,
            versioning=versioning,
            **kwargs,
        )

    def _search_options(self, service: RDMRecordService, search_opts: Any) -> Any:
        if search_opts is self.config.search:
            return service.config.search
        if search_opts is self.config.search_drafts:
            return service.config.search_drafts
        if search_opts is self.config.search_versions:
            return service.config.search_versions
        return search_opts

    def _search_eligible_services(
        self, identity: Identity, permission_action: str, **kwargs: Any
    ) -> dict[str, RDMRecordService]:
        """Get a list of eligible RDM record services."""
        return {
            model.record_json_schema: cast("RDMRecordService", model.service)
            for model in current_runtime.rdm_models
            if model.service.check_permission(identity, permission_action, **kwargs)
        }

    @override
    def oai_result_item(self, identity: Identity, oai_record_source: dict[str, Any]) -> RecordItem:
        """Serialize an oai record source to a record item."""
        model = self._get_model_from_record_data(oai_record_source)
        service: RDMRecordService = cast("RDMRecordService", model.service)
        return cast("RecordItem", service.oai_result_item(identity, oai_record_source))

    @override
    def rebuild_index(self, identity: Identity, uow: UnitOfWork | None = None) -> Literal[True]:
        """Rebuild the search index for all records."""
        for model in current_runtime.rdm_models:
            if hasattr(model.service, "rebuild_index"):
                model.service.rebuild_index(identity, uow=uow)
            else:
                raise NotImplementedError(f"Model {model} does not support rebuilding index.")
        return True

    @unit_of_work()
    @override
    def cleanup_drafts(
        self,
        timedelta: datetime.timedelta,
        uow: UnitOfWork | None = None,
        search_gc_deletes: int = 60,
    ) -> None:
        for model in current_runtime.rdm_models:
            cleanup_drafts = getattr(model.service, "cleanup_drafts", None)
            if cleanup_drafts:
                cleanup_drafts(timedelta, uow=uow, search_gc_deletes=search_gc_deletes)
            else:
                raise NotImplementedError(f"Model {model} does not support cleaning up drafts.")

    @unit_of_work()
    @override
    def reindex_latest_first(
        self,
        identity: Identity,
        search_preference: str | None = None,
        extra_filter: Any | None = None,
        uow: UnitOfWork | None = None,
        **kwargs: Any,
    ) -> Literal[True]:
        for model in current_runtime.rdm_models:
            reindex_latest_first = getattr(model.service, "reindex_latest_first", None)
            if reindex_latest_first:
                reindex_latest_first(
                    identity,
                    search_preference=search_preference,
                    extra_filter=extra_filter,
                    uow=uow,
                    **kwargs,
                )
            else:
                raise NotImplementedError(f"Model {model} does not support rebuilding index.")

        return True

    @override
    def reindex(
        self,
        identity: Identity,
        params: dict[str, tuple[str, ...]] | None = None,
        search_preference: str | None = None,
        search_query: str | None = None,
        extra_filter: Any | None = None,
        **kwargs: Any,
    ) -> Literal[True]:
        for model in current_runtime.rdm_models:
            if hasattr(model.service, "reindex"):
                model.service.reindex(
                    identity,
                    params=params,
                    search_preference=search_preference,
                    search_query=search_query,
                    extra_filter=extra_filter,
                    **kwargs,
                )
            else:
                raise NotImplementedError(f"Model {model} does not support rebuilding index.")
        return True

    @override
    def on_relation_update(
        self,
        identity: Identity,
        record_type: str,
        records_info: Any,
        notif_time: datetime.datetime,
        limit: int = 100,
    ) -> Literal[True]:
        for model in current_runtime.rdm_models:
            if hasattr(model.service, "on_relation_update"):
                model.service.on_relation_update(  # type: ignore[no-any-return]
                    identity,
                    record_type,
                    records_info,
                    notif_time,
                    limit=limit,
                )
            raise NotImplementedError(f"Model {model} does not support relation updates.")
        return True
