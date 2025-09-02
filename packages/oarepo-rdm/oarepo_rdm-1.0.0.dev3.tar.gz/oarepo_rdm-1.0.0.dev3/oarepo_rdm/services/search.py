#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-rdm (see https://github.com/oarepo/oarepo-rdm).
#
# oarepo-rdm is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Multiplexed search options and delegated query parameter."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, override

from deepmerge import always_merger
from invenio_records_resources.services.records.config import SearchOptions
from invenio_records_resources.services.records.params import (
    PaginationParam,
    ParamInterpreter,
    SortParam,
)
from oarepo_runtime import current_runtime
from oarepo_runtime.services.facets.params import GroupedFacetsParam

if TYPE_CHECKING:
    from invenio_access.permissions import Identity
    from invenio_search import RecordsSearchV2


log = logging.getLogger(__name__)


class DelegatedQueryParam(ParamInterpreter):
    """Evaluate the 'json' parameter."""

    @override
    def apply(  # type: ignore[reportIncompatibleMethodOverride]
        self, identity: Identity, search: RecordsSearchV2, params: dict[str, Any]
    ) -> RecordsSearchV2:
        """Evaluate the query str on the search."""
        if "delegated_query" in params:
            queries_list, search_opts = params.pop("delegated_query")

            query, aggs, post_filter, sort = self._merge_queries(queries_list)

            for agg in aggs:
                search.aggs.bucket(agg, aggs[agg])
            search = search.query(query)  # type: ignore[reportCallIssue] # done via proxy, not understood by mypy
            if post_filter != {}:
                search = search.post_filter(post_filter)
            if sort:
                search = search.sort(sort[0])
        return search

    def _merge_queries(
        self,
        queries_list: dict[str, dict],
    ) -> tuple[dict, dict, dict, list]:
        """Merge multiple queries into a single query."""
        shoulds: list[Any] = []
        query = {"bool": {"should": shoulds, "minimum_should_match": 1}}
        aggs = {}
        post_filter = {}
        sort = []

        for pid_type, query_data in queries_list.items():
            schema_query = query_data.get("query", {})
            shoulds.append({"bool": {"must": [{"term": {"$schema": pid_type}}, schema_query]}})

            if "aggs" in query_data:
                aggs.update(query_data["aggs"])
            if "post_filter" in query_data:
                post_filter.update(query_data["post_filter"])
            if "sort" in query_data:
                sort.extend(query_data["sort"])

        return query, aggs, post_filter, sort


class MultiplexedSearchOptions(SearchOptions):
    """Search options."""

    params_interpreters_cls = (
        GroupedFacetsParam,
        PaginationParam,
        SortParam,
        DelegatedQueryParam,
    )

    def __init__(self, config_field: str) -> None:
        """Initialize search options."""
        search_opts = self._search_opts(config_field)

        self.facets = search_opts["facets"]
        self.facet_groups = search_opts["facet_groups"]
        self.sort_options = search_opts["sort_options"]
        self.sort_default = search_opts["sort_default"]
        self.sort_default_no_query = search_opts["sort_default_no_query"]

    def _search_opts_from_search_obj(self, search: Any) -> dict[str, Any]:
        facets: dict[str, Any] = {}
        sort_options = {}

        facets.update(search.facets)
        try:
            sort_options.update(search.sort_options)
        except AttributeError as e:
            log.warning("Error updating sort options: %s", e)
        sort_default = search.sort_default
        sort_default_no_query = search.sort_default_no_query
        facet_groups = getattr(search, "facet_groups", {})
        return {
            "facets": facets,
            "facet_groups": facet_groups,
            "sort_options": sort_options,
            "sort_default": sort_default,
            "sort_default_no_query": sort_default_no_query,
        }

    def _search_opts(self, config_field: str) -> dict:
        """Get search options from the config."""
        ret: dict[str, Any] = {}
        for model in current_runtime.rdm_models:
            if hasattr(model.service.config, config_field):
                ret = always_merger.merge(
                    ret,
                    self._search_opts_from_search_obj(getattr(model.service.config, config_field)),
                )
        return ret
