"""
Query Builder - Generic query building functionality for MongoDB aggregation pipelines
"""

import re
import time
from copy import deepcopy
from typing import List, Dict, Any, Optional, Union
from fastapi import HTTPException, status
from pprint import pprint

# Import core utilities
from ..core.parsing import (
    parse_params_to_dict,
    normalize_field_path,
    validate_field_path,
    build_aggregation_field_expression,
)


class QueryBuilder:
    """
    Generic query builder for MongoDB aggregation pipelines.
    Can be used standalone or inherited by CRUD classes.
    """

    def __init__(self, collection_prefix: str = "", relations: List = None):
        """
        Initialize the QueryBuilder

        Args:
            collection_prefix: Prefix for collection names
            relations: List of relations for lookup operations
        """
        self.collection_prefix = collection_prefix
        self.relations = relations or []

    def read_query(
        self,
        db_collection,
        params: Union[Dict[str, str], Any] = None,
        query: Optional[Dict[str, Any]] = None,
        pipeline: Optional[List[Dict[str, Any]]] = None,
        pipeline_count: Optional[List[Dict[str, Any]]] = None,
        use_cache: bool = False,
        cache_client=None,
        cache_key_prefix: str = "",
        clear_cache: bool = False,
        debug: bool = False,
    ) -> Dict[str, Any]:
        """
        Complete query method that handles parameter parsing and query execution.

        Args:
            db_collection: MongoDB collection object
            params: Raw query parameters (will be parsed if provided)
            query: Pre-parsed query dictionary (used if params not provided)
            pipeline: Optional custom pipeline for data
            pipeline_count: Optional custom pipeline for count
            use_cache: Whether to use caching
            cache_client: Cache client (Redis)
            cache_key_prefix: Prefix for cache keys
            clear_cache: Whether to clear cache before query
            debug: Whether to enable debug output
        """
        # Start timing
        start_time = time.time()

        if debug:
            print("🔵 [DEBUG] Parámetros de entrada:")
            pprint(
                {
                    "params": params if params is not None else "None",
                    "query": query if query is not None else "None",
                    "use_cache": use_cache,
                    "cache_key_prefix": cache_key_prefix,
                    "clear_cache": clear_cache,
                }
            )

        # Parse params if provided, otherwise use query directly
        parsing_start_time = time.time()
        if params is not None:
            parsed_query = parse_params_to_dict(params)
        elif query is not None:
            parsed_query = query
        else:
            raise ValueError("Either 'params' or 'query' must be provided")

        # Handle clear_cache from parsed query
        if "clear_cache" in parsed_query:
            clear_cache = parsed_query.pop("clear_cache", False)

        parsing_time = time.time() - parsing_start_time

        if debug:
            print("🔵 [DEBUG] Query parseada:")
            pprint(parsed_query)
            print(f"🔵 [DEBUG] Tiempo de parsing: {parsing_time:.3f}s")

        return self.get_query_response(
            db_collection,
            parsed_query,
            pipeline,
            pipeline_count,
            cache_client=cache_client,
            cache_key_prefix=cache_key_prefix,
            use_cache=use_cache,
            clear_cache=clear_cache,
            debug=debug,
            start_time=start_time,
            parsing_time=parsing_time,
        )

    def build_filter_pipeline(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build a filter pipeline from query filters.
        Supports various operators including text search, comparison, and logical operators.
        """

        def get_value_type_and_string(value):
            """Determine value type and return appropriate string representation"""
            if value is None:
                return "null", ""
            elif isinstance(value, bool):
                return "boolean", str(value).lower()
            elif isinstance(value, (int, float)):
                return "number", str(value)
            elif isinstance(value, str):
                return "string", value
            else:
                # For dates, ObjectId, etc.
                return "other", str(value)

        def is_numeric_string(s):
            """Check if string represents a number"""
            try:
                float(s)
                return True
            except ValueError:
                return False

        def expand_text_search_condition(field_name, operator, str_value):
            """Expand a single text search condition into multiple conditions for different field types"""
            expanded_conditions = []
            escaped_value = re.escape(str_value)

            # Condition 1: For string fields - use regex
            match operator:
                case "$containsi":
                    expanded_conditions.append(
                        {field_name: {"$regex": escaped_value, "$options": "i"}}
                    )
                case "$contains":
                    expanded_conditions.append({field_name: {"$regex": escaped_value}})
                case "$notContainsi":
                    expanded_conditions.append(
                        {
                            field_name: {
                                "$not": {"$regex": escaped_value, "$options": "i"}
                            }
                        }
                    )
                case "$notContains":
                    expanded_conditions.append(
                        {field_name: {"$not": {"$regex": escaped_value}}}
                    )
                case "$startsWith":
                    expanded_conditions.append(
                        {field_name: {"$regex": f"^{escaped_value}"}}
                    )
                case "$startsWithi":
                    expanded_conditions.append(
                        {field_name: {"$regex": f"^{escaped_value}", "$options": "i"}}
                    )
                case "$endsWith":
                    expanded_conditions.append(
                        {field_name: {"$regex": f"{escaped_value}$"}}
                    )
                case "$endsWithi":
                    expanded_conditions.append(
                        {field_name: {"$regex": f"{escaped_value}$", "$options": "i"}}
                    )
                case "$eqi":
                    expanded_conditions.append(
                        {field_name: {"$regex": f"^{escaped_value}$", "$options": "i"}}
                    )
                case "$nei":
                    expanded_conditions.append(
                        {
                            field_name: {
                                "$not": {
                                    "$regex": f"^{escaped_value}$",
                                    "$options": "i",
                                }
                            }
                        }
                    )

            # Condition 2: For numeric fields - if the search value looks like a number
            if is_numeric_string(str_value):
                try:
                    # Convert to number for direct numeric comparison
                    if "." in str_value:
                        numeric_value = float(str_value)
                    else:
                        numeric_value = int(str_value)

                    match operator:
                        case "$containsi" | "$contains":
                            # Exact numeric match
                            expanded_conditions.append({field_name: numeric_value})

                            # For integer searches, also check decimal equivalents
                            if str_value == str(
                                int(float(str_value))
                            ):  # It's a whole number like "10"
                                int_val = int(float(str_value))
                                # Add the float version too
                                expanded_conditions.append({field_name: float(int_val)})

                                # For single digit or small numbers, add range searches
                                # to catch things like 10 in 10.5, 100, etc.
                                if len(str_value) <= 2 and int_val >= 0:
                                    # Range for numbers like 10.x (10.0 to 10.999...)
                                    expanded_conditions.append(
                                        {
                                            field_name: {
                                                "$gte": int_val,
                                                "$lt": int_val + 1,
                                            }
                                        }
                                    )

                                    # Range for numbers like x10 (10, 110, 210, etc.)
                                    if int_val > 0:
                                        # Numbers that start with this digit
                                        range_start = int_val * (
                                            10 ** (len(str(int_val)))
                                        )
                                        range_end = (
                                            range_start
                                            + (10 ** (len(str(int_val))))
                                            - 1
                                        )
                                        if range_start != int_val:  # Avoid duplicate
                                            expanded_conditions.append(
                                                {
                                                    field_name: {
                                                        "$gte": range_start,
                                                        "$lte": range_end,
                                                    }
                                                }
                                            )

                        case "$eqi":
                            expanded_conditions.append({field_name: numeric_value})
                            if isinstance(numeric_value, int):
                                expanded_conditions.append(
                                    {field_name: float(numeric_value)}
                                )

                        case "$nei":
                            expanded_conditions.append(
                                {field_name: {"$ne": numeric_value}}
                            )
                            if isinstance(numeric_value, int):
                                expanded_conditions.append(
                                    {field_name: {"$ne": float(numeric_value)}}
                                )

                        case "$startsWith" | "$startsWithi":
                            # Exact match
                            expanded_conditions.append({field_name: numeric_value})
                            # Range match for numbers starting with this value
                            if str_value == str(int(float(str_value))):
                                int_val = int(float(str_value))
                                range_start = int_val * (10 ** (len(str(int_val))))
                                range_end = (
                                    range_start + (10 ** (len(str(int_val)))) - 1
                                )
                                if range_start != int_val:
                                    expanded_conditions.append(
                                        {
                                            field_name: {
                                                "$gte": range_start,
                                                "$lte": range_end,
                                            }
                                        }
                                    )

                        case "$endsWith" | "$endsWithi":
                            # For ends with, just exact match for now
                            expanded_conditions.append({field_name: numeric_value})

                except ValueError:
                    pass

            return expanded_conditions

        def build_sub_pipeline(conditions, field_name=None):
            sub_pipeline = {}
            for operator, value in conditions.items():
                value_type, str_value = get_value_type_and_string(value)

                # Text search operators that need special handling for mixed types
                text_search_ops = [
                    "$contains",
                    "$notContains",
                    "$containsi",
                    "$notContainsi",
                    "$startsWith",
                    "$startsWithi",
                    "$endsWith",
                    "$endsWithi",
                    "$eqi",
                    "$nei",
                ]

                if operator in text_search_ops:
                    # For simple field conditions (not in $or), use basic approach
                    escaped_value = re.escape(str_value)

                    if is_numeric_string(str_value):
                        try:
                            if "." in str_value:
                                numeric_value = float(str_value)
                            else:
                                numeric_value = int(str_value)

                            # For exact match operators, prefer numeric
                            if operator in ["$eqi", "$eq"]:
                                sub_pipeline = numeric_value
                            elif operator in ["$nei", "$ne"]:
                                sub_pipeline = {"$ne": numeric_value}
                            else:
                                # For contains operations, try numeric first
                                sub_pipeline = numeric_value
                        except ValueError:
                            # Fall back to regex
                            if operator == "$containsi":
                                sub_pipeline = {
                                    "$regex": escaped_value,
                                    "$options": "i",
                                }
                            elif operator == "$contains":
                                sub_pipeline = {"$regex": escaped_value}
                            else:
                                sub_pipeline = {
                                    "$regex": escaped_value,
                                    "$options": "i",
                                }
                    else:
                        # Non-numeric search, use regex
                        if operator == "$containsi":
                            sub_pipeline = {"$regex": escaped_value, "$options": "i"}
                        elif operator == "$contains":
                            sub_pipeline = {"$regex": escaped_value}
                        elif operator == "$startsWith":
                            sub_pipeline = {"$regex": f"^{escaped_value}"}
                        elif operator == "$startsWithi":
                            sub_pipeline = {
                                "$regex": f"^{escaped_value}",
                                "$options": "i",
                            }
                        elif operator == "$endsWith":
                            sub_pipeline = {"$regex": f"{escaped_value}$"}
                        elif operator == "$endsWithi":
                            sub_pipeline = {
                                "$regex": f"{escaped_value}$",
                                "$options": "i",
                            }
                        elif operator == "$eqi":
                            sub_pipeline = {
                                "$regex": f"^{escaped_value}$",
                                "$options": "i",
                            }
                        elif operator == "$nei":
                            sub_pipeline = {
                                "$not": {
                                    "$regex": f"^{escaped_value}$",
                                    "$options": "i",
                                }
                            }
                        else:
                            sub_pipeline = {"$regex": escaped_value, "$options": "i"}
                else:
                    # Handle non-text operators normally
                    match operator:
                        case "$eq":
                            sub_pipeline = value
                        case "$ne":
                            sub_pipeline = {"$ne": value}
                        case "$lt":
                            sub_pipeline = {"$lt": value}
                        case "$lte":
                            sub_pipeline = {"$lte": value}
                        case "$gt":
                            sub_pipeline = {"$gt": value}
                        case "$gte":
                            sub_pipeline = {"$gte": value}
                        case "$in":
                            if not isinstance(value, list):
                                value = [value]
                            sub_pipeline = {"$in": value}
                        case "$notIn":
                            if not isinstance(value, list):
                                value = [value]
                            sub_pipeline = {"$nin": value}
                        case "$listContains":
                            sub_pipeline = value
                        case "$listNotContains":
                            sub_pipeline = {"$ne": value}
                        case "$null":
                            sub_pipeline = {"$in": [None, ""]}
                        case "$notNull":
                            sub_pipeline = {"$nin": [None, ""]}
                        case "$exists":
                            sub_pipeline = {"$exists": value}
                        case "$notExists":
                            sub_pipeline = {"$not": {"$exists": value}}
                        case "$between":
                            if not isinstance(value, list) or len(value) != 2:
                                raise ValueError(
                                    f"$between operator requires an array with exactly 2 elements, got: {value}"
                                )
                            sub_pipeline = {"$gte": value[0], "$lte": value[1]}
                        case _:
                            if isinstance(value, dict):
                                sub_pipeline = {
                                    "_field": operator,
                                    "_conditions": build_sub_pipeline(
                                        value, field_name
                                    ),
                                }
                            else:
                                # If it's not a recognized operator, treat as equality
                                sub_pipeline = {operator: value}
            return sub_pipeline

        pipeline = {}

        for field, conditions in filters.items():
            match field:
                case "$or":
                    or_conditions = []
                    for condition in conditions:
                        # Check if this condition contains text search operators
                        field_name = list(condition.keys())[0]
                        field_conditions = condition[field_name]

                        # Normalize field name for dot notation support
                        normalized_field_name = normalize_field_path(field_name)

                        if isinstance(field_conditions, dict):
                            operator = list(field_conditions.keys())[0]
                            value = field_conditions[operator]

                            # Text search operators that need expansion
                            text_search_ops = [
                                "$contains",
                                "$notContains",
                                "$containsi",
                                "$notContainsi",
                                "$startsWith",
                                "$startsWithi",
                                "$endsWith",
                                "$endsWithi",
                                "$eqi",
                                "$nei",
                            ]

                            if operator in text_search_ops:
                                # Expand this condition into multiple alternatives
                                value_type, str_value = get_value_type_and_string(value)
                                expanded_conditions = expand_text_search_condition(
                                    normalized_field_name, operator, str_value
                                )

                                # Add all expanded conditions to the $or
                                or_conditions.extend(expanded_conditions)
                            else:
                                # Regular condition, process normally with normalized field
                                normalized_condition = {
                                    normalized_field_name: field_conditions
                                }
                                sub_pipeline = self.build_filter_pipeline(
                                    normalized_condition
                                )
                                or_conditions.append(sub_pipeline)
                        else:
                            # Regular condition, process normally with normalized field
                            normalized_condition = {
                                normalized_field_name: field_conditions
                            }
                            sub_pipeline = self.build_filter_pipeline(
                                normalized_condition
                            )
                            or_conditions.append(sub_pipeline)

                    pipeline["$or"] = or_conditions
                case "$and":
                    and_conditions = []
                    for condition in conditions:
                        # Normalize field names in condition for dot notation support
                        normalized_condition = {}
                        for field_name, field_conditions in condition.items():
                            normalized_field_name = normalize_field_path(field_name)
                            normalized_condition[normalized_field_name] = (
                                field_conditions
                            )

                        sub_pipeline = self.build_filter_pipeline(normalized_condition)
                        and_conditions.append(sub_pipeline)
                    pipeline["$and"] = and_conditions
                case _:
                    try:
                        # Normalize field path for dot notation and array notation support
                        normalized_field = normalize_field_path(field)

                        # Validate the field path
                        if not validate_field_path(normalized_field):
                            print(
                                f"Warning: Invalid field path '{field}', skipping filter condition"
                            )
                            continue

                        sub_pipeline = build_sub_pipeline(conditions, normalized_field)

                        if isinstance(sub_pipeline, dict):
                            if "_field" in sub_pipeline:
                                new_field = (
                                    f"{normalized_field}.{sub_pipeline['_field']}"
                                )
                                pipeline[new_field] = sub_pipeline["_conditions"]
                                continue

                        pipeline[normalized_field] = sub_pipeline
                    except (ValueError, TypeError) as e:
                        # Log the error and skip this filter condition
                        print(f"Error processing filter for field '{field}': {e}")
                        continue

        return pipeline

    def build_sort_pipeline(self, sort_params: List[str]) -> Dict[str, Any]:
        """
        Build sort pipeline from sort parameters with support for dot notation and array notation.
        """
        sort_pipeline = {}
        for item in sort_params:
            try:
                field, order = item.split(":")
                normalized_field = normalize_field_path(field)

                if validate_field_path(normalized_field):
                    sort_pipeline[normalized_field] = 1 if order == "asc" else -1
                else:
                    print(f"Warning: Invalid field path '{field}', skipping in sort")
            except ValueError as e:
                print(
                    f"Warning: Invalid sort parameter '{item}', expected format 'field:order': {e}"
                )
            except Exception as e:
                print(f"Warning: Error processing sort parameter '{item}': {e}")

        return {"$sort": sort_pipeline}

    def build_fields_pipeline(
        self, fields_params: List[str], populate_params: Optional[List] = None
    ) -> Dict[str, Any]:
        """
        Build fields projection pipeline with support for dot notation and array notation.
        """
        fields_pipeline = {}

        # Process fields_params with normalization
        for field in fields_params:
            try:
                normalized_field = normalize_field_path(field)
                if validate_field_path(normalized_field):
                    fields_pipeline[normalized_field] = 1
                else:
                    print(
                        f"Warning: Invalid field path '{field}', skipping in projection"
                    )
            except Exception as e:
                print(f"Warning: Error processing field '{field}' in projection: {e}")

        # Process populate_params if provided
        if populate_params:
            for field in populate_params:
                try:
                    normalized_field = normalize_field_path(field)
                    if validate_field_path(normalized_field):
                        fields_pipeline[normalized_field] = 1
                    else:
                        print(
                            f"Warning: Invalid populate field path '{field}', skipping in projection"
                        )
                except Exception as e:
                    print(
                        f"Warning: Error processing populate field '{field}' in projection: {e}"
                    )

        return {"$project": fields_pipeline}

    def build_distinct_pipeline(
        self,
        distinct_params: List[str],
        include_project: bool = True,
        pipeline: Optional[List] = None,
    ) -> List[Dict[str, Any]]:
        """
        Build distinct pipeline with support for dot notation and array notation.
        """
        try:
            # Build group_id with proper field expressions
            group_id = {}
            project_fields = {}

            for field in distinct_params:
                try:
                    # Use utility function to build proper aggregation expression
                    field_expression = build_aggregation_field_expression(field)

                    print(f"🔵 [DEBUG] Field: {field}")
                    print(f"🔵 [DEBUG] Field expression: {field_expression}")

                    # For MongoDB $group stage, we need to use a safe key name (no dots)
                    # We'll use the original field name as key, but replace dots with underscores for the group
                    safe_key = (
                        field.replace(".", "_").replace("[", "_").replace("]", "_")
                    )
                    group_id[safe_key] = field_expression

                    print(f"🔵 [DEBUG] Safe key: {safe_key}")
                    print(f"🔵 [DEBUG] Group ID entry: {safe_key} = {field_expression}")

                    # Build nested structure for the projection to maintain original field structure
                    parts = field.split(".")
                    current = project_fields
                    for i, part in enumerate(parts[:-1]):
                        if part not in current:
                            current[part] = {}
                        current = current[part]

                    # Set the final value
                    current[parts[-1]] = f"$_id.{safe_key}"

                    print(
                        f"🔵 [DEBUG] Project fields after processing {field}: {project_fields}"
                    )

                    # Debug: Check if field exists in pipeline before distinct
                    print(
                        f"🔵 [DEBUG] Pipeline before distinct contains establishment_type lookup: {any('establishment_type' in str(stage) for stage in pipeline) if pipeline else 'No pipeline provided'}"
                    )
                    print(
                        f"🔵 [DEBUG] Available relations: {[rel[1] for rel in self.relations]}"
                    )

                except ValueError as e:
                    # Log error and skip invalid field
                    print(f"Warning: Skipping invalid field '{field}' in distinct: {e}")
                    continue

            if not group_id:
                raise ValueError("No valid fields provided for distinct operation")

            group_stage = {"$group": {"_id": group_id}}

            if include_project:
                # Use $project to create the nested structure
                project_stage = {"$project": project_fields}
                return [group_stage, project_stage]
            else:
                return [group_stage]

        except Exception as e:
            # Fallback to original behavior for backwards compatibility
            print(
                f"Warning: Error in enhanced distinct pipeline, falling back to original: {e}"
            )
            group_id = {field: f"${field}" for field in distinct_params}
            group_stage = {"$group": {"_id": group_id}}
            if include_project:
                replace_root_stage = {"$replaceRoot": {"newRoot": "$_id"}}
                return [group_stage, replace_root_stage]
            else:
                return [group_stage]

    def build_pagination_pipeline(
        self, pagination_params: Dict[str, Any], pipeline: Optional[List] = None
    ) -> List[Dict[str, Any]]:
        """Build pagination pipeline"""
        pageSize = pagination_params.get("pageSize", 10)
        page = pagination_params.get("page", 1)
        skip = (int(page) - 1) * int(pageSize)

        pipeline_copy = deepcopy(pipeline) if pipeline else []

        has_skip = any("$skip" in stage for stage in pipeline_copy)
        has_limit = any("$limit" in stage for stage in pipeline_copy)

        if not has_skip:
            pipeline_copy.append({"$skip": skip})
        else:
            for stage in pipeline_copy:
                if "$skip" in stage:
                    stage["$skip"] = skip

        if not has_limit:
            pipeline_copy.append({"$limit": pageSize})
        else:
            for stage in pipeline_copy:
                if "$limit" in stage:
                    stage["$limit"] = pageSize

        return pipeline_copy

    def sanitize_result(
        self, query: Dict[str, Any], data_result: Any, meta_result: Any
    ) -> Dict[str, Any]:
        """Sanitize query results"""
        if "distinct" in query:
            if (
                isinstance(data_result, list)
                and len(data_result) == 1
                and all(v is None for v in data_result[0].values())
            ):
                data_result = []
                meta_result = {"totalCount": 0}

        if isinstance(meta_result, list):
            if meta_result:
                meta_result = meta_result[0]
            else:
                meta_result = {"totalCount": 0}

        if not meta_result or "totalCount" not in meta_result:
            meta_result = {"totalCount": 0}

        return {"data": data_result, "meta": meta_result}

    def get_lookup_relation(self, relation_field: List[str]) -> tuple:
        """Get lookup relation configuration for a specific relation field"""
        _prefix = self.collection_prefix + "_"
        if len(relation_field) > 2 and relation_field[2]:
            _prefix = relation_field[2] + "_"

        if len(relation_field) > 2 and not relation_field[2]:
            _prefix = ""

        relation_field_name = relation_field[1]

        if "_id" in relation_field_name:
            match_stage = {"$match": {"$expr": {"$eq": ["$_id", "$$lid"]}}}
            collection_name_relation = relation_field_name.replace("_id", "")
        if "_ids" in relation_field_name:
            match_stage = {"$match": {"$expr": {"$in": ["$_id", "$$lid"]}}}
            collection_name_relation = relation_field_name.replace("_ids", "")

        if len(relation_field) > 3 and relation_field[3]:
            collection_name_relation = relation_field[3].replace("_id", "")

        _as = collection_name_relation
        if len(relation_field) > 4 and relation_field[4]:
            _as = relation_field[4]

        if relation_field[0] == "Users":
            lookup_relation = [
                {
                    "$lookup": {
                        "from": "users",
                        "let": {"usersId": "$person"},
                        "pipeline": [
                            {
                                "$match": {
                                    "$expr": {
                                        "$eq": [
                                            "$_id",
                                            {"$toObjectId": "$$usersId"},
                                        ]
                                    }
                                }
                            },
                            {
                                "$project": {
                                    "role": 0,
                                    "hashed_password": 0,
                                    "id": 0,
                                    "avatar": 0,
                                    "active_directory": 0,
                                    "privacy_policy": 0,
                                    "terms_condition": 0,
                                    "privacy_policy_date": 0,
                                    "terms_condition_date": 0,
                                    "disabled": 0,
                                    "username": 0,
                                    "establishment_asignation_ids": 0,
                                    "establishment_type_ids": 0,
                                    "permission_by_establishment": 0,
                                    "permission_by_establishment_type": 0,
                                    "terms_condition_date": 0,
                                    "establishment_ids": 0,
                                    "establishment_active_id": 0,
                                }
                            },
                            {"$addFields": {"_id": {"$toString": "$_id"}}},
                        ],
                        "as": "person",
                    }
                },
                {
                    "$unwind": {
                        "path": "$person",
                        "preserveNullAndEmptyArrays": True,
                    }
                },
            ]
        else:
            lookup_relation = [
                {
                    "$lookup": {
                        "from": f"{_prefix}{collection_name_relation}",
                        "let": {"lid": f"${relation_field_name}"},
                        "pipeline": [
                            {"$addFields": {"_id": {"$toString": "$_id"}}},
                            match_stage,
                            {
                                "$project": {
                                    "creation_user": 0,
                                    "creation_date": 0,
                                    "disable": 0,
                                }
                            },
                        ],
                        "as": _as,
                    },
                },
                {"$unwind": {"path": f"${_as}", "preserveNullAndEmptyArrays": True}},
            ]

        if not "_ids" in relation_field_name:
            lookup_relation.append(
                {
                    "$unwind": {
                        "path": f"${collection_name_relation}",
                        "preserveNullAndEmptyArrays": True,
                    }
                }
            )

        return lookup_relation, collection_name_relation

    def get_query_lookup_relations(self, query_relations):
        """Get lookup relations for query population"""
        query_lookup_relations = []

        if isinstance(query_relations, list):
            for query_relation in query_relations:
                for relation in self.relations:
                    relation_name = relation[1]
                    if re.search(r"_ids$", relation_name):
                        relation_name = relation_name[:-4]

                    if re.search(r"_id$", relation_name):
                        relation_name = relation_name[:-3]

                    if relation_name == query_relation:
                        lookup_relation = self.get_lookup_relation(relation)
                        query_lookup_relations = [
                            *query_lookup_relations,
                            *lookup_relation[0],
                        ]
        if isinstance(query_relations, dict):
            for query_relation in query_relations.keys():
                for relation in self.relations:
                    relation_name = relation[1]
                    if re.search(r"_ids$", relation_name):
                        relation_name = relation_name[:-4]

                    if re.search(r"_id$", relation_name):
                        relation_name = relation_name[:-3]

                    if relation_name == query_relation:
                        if query_relations[query_relation] == True:
                            lookup_relation = self.get_lookup_relation(relation)
                            query_lookup_relations = [
                                *query_lookup_relations,
                                *lookup_relation[0],
                            ]

                        if isinstance(query_relations[query_relation], dict):
                            lookup_relation = self.get_lookup_relation(
                                relation, query_relations[query_relation]
                            )
                            query_lookup_relations = [
                                *query_lookup_relations,
                                *lookup_relation[0],
                            ]
        return query_lookup_relations

    def get_count_lookup_relation(self, relation_field: List[str]) -> tuple:
        """Get count lookup relation for a specific relation field"""
        _prefix = self.collection_prefix + "_"
        if len(relation_field) > 2 and relation_field[2]:
            _prefix = relation_field[2] + "_"

        if len(relation_field) > 2 and not relation_field[2]:
            _prefix = ""

        relation_field_name = relation_field[1]

        if "_id" in relation_field_name:
            match_stage = {"$match": {"$expr": {"$eq": ["$_id", "$$lid"]}}}
            collection_name_relation = relation_field_name.replace("_id", "")
        if "_ids" in relation_field_name:
            match_stage = {"$match": {"$expr": {"$in": ["$_id", "$$lid"]}}}
            collection_name_relation = relation_field_name.replace("_ids", "")

        if len(relation_field) > 3 and relation_field[3]:
            collection_name_relation = relation_field[3].replace("_id", "")

        _as = collection_name_relation
        if len(relation_field) > 4 and relation_field[4]:
            _as = relation_field[4]

        lookup_relation = [
            {
                "$lookup": {
                    "from": f"{_prefix}{collection_name_relation}",
                    "let": {"lid": f"${relation_field_name}"},
                    "pipeline": [
                        {"$addFields": {"_id": {"$toString": "$_id"}}},
                        match_stage,
                    ],
                    "as": _as,
                },
            }
        ]

        if not "_ids" in relation_field_name:
            lookup_relation.append(
                {
                    "$unwind": {
                        "path": f"${collection_name_relation}",
                        "preserveNullAndEmptyArrays": True,
                    }
                }
            )

        return lookup_relation, collection_name_relation

    def get_count_lookup_relations(
        self, query_relations: List[str]
    ) -> List[Dict[str, Any]]:
        """Get count lookup relations for query population"""
        query_lookup_relations = []

        for query_relation in query_relations:
            for relation in self.relations:
                relation_name = relation[1]
                if re.search(r"_ids$", relation_name):
                    relation_name = relation_name[:-4]

                if re.search(r"_id$", relation_name):
                    relation_name = relation_name[:-3]

                if relation_name == query_relation:
                    lookup_relation = self.get_count_lookup_relation(relation)
                    query_lookup_relations = [
                        *query_lookup_relations,
                        *lookup_relation[0],
                    ]

        return query_lookup_relations

    def build_populate_pipeline(self, populate_params):
        """Build populate pipeline"""
        return self.get_query_lookup_relations(populate_params)

    def make_aggregation_query(
        self, query: Dict[str, Any], base_pipeline: Optional[List] = None
    ) -> List[Dict[str, Any]]:
        """Make aggregation query pipeline"""
        pipeline = [] if not base_pipeline else deepcopy(base_pipeline)

        if "populate" in query:
            pipeline.extend(self.build_populate_pipeline(query["populate"]))

        if "filters" in query:
            filter_pipeline = self.build_filter_pipeline(query["filters"])
            pipeline.append({"$match": filter_pipeline})

        if "distinct" in query:
            pipeline.extend(
                self.build_distinct_pipeline(
                    query["distinct"], include_project=True, pipeline=pipeline
                )
            )
        elif "fields" in query:
            pipeline.append(
                self.build_fields_pipeline(query["fields"], query.get("populate", None))
            )

        if "sort" in query:
            pipeline.append(self.build_sort_pipeline(query["sort"]))

        pipeline = self.build_pagination_pipeline(query.get("pagination", {}), pipeline)

        return pipeline

    def make_count_aggregation_query(
        self, query: Dict[str, Any], base_pipeline: Optional[List] = None
    ) -> List[Dict[str, Any]]:
        """Make count aggregation query pipeline"""
        pipeline = deepcopy(base_pipeline) if base_pipeline else []

        if "filters" in query:
            if not pipeline:
                # Extract potential relation field names from filters, supporting
                # logical operators ($or/$and) and dot-notation (e.g., "company.name").
                def extract_relation_candidates(filters_dict):
                    relation_names = set()

                    def walk(node):
                        if isinstance(node, dict):
                            for k, v in node.items():
                                if k in ("$or", "$and"):
                                    # Value can be a list of conditions or a nested dict
                                    if isinstance(v, list):
                                        for item in v:
                                            walk(item)
                                    else:
                                        walk(v)
                                else:
                                    # Field key: take root before dot and strip _id/_ids
                                    if (
                                        isinstance(k, str)
                                        and k
                                        and not k.startswith("$")
                                    ):
                                        root = k.split(".")[0]
                                        root = re.sub(r"(_ids|_id)$", "", root)
                                        if root:
                                            relation_names.add(root)
                                    # Continue walking nested structures like
                                    # {"company": {"name": {"$containsi": "x"}}}
                                    walk(v)
                        elif isinstance(node, list):
                            for item in node:
                                walk(item)
                        # Primitives are ignored

                    walk(filters_dict)
                    return list(relation_names)

                relation_candidates = extract_relation_candidates(query["filters"])
                if relation_candidates:
                    populate_from_filters = self.get_count_lookup_relations(
                        relation_candidates
                    )
                    pipeline.extend(populate_from_filters)

            filter_pipeline = self.build_filter_pipeline(query["filters"])
            pipeline.append({"$match": filter_pipeline})

        if "distinct" in query:
            pipeline.extend(
                self.build_distinct_pipeline(
                    query["distinct"], include_project=False, pipeline=pipeline
                )
            )

        pipeline.append({"$count": "totalCount"})

        return pipeline

    def get_query_response(
        self,
        db_collection,
        query: Dict[str, Any],
        pipeline: Optional[List] = None,
        pipeline_count: Optional[List] = None,
        cache_client=None,
        cache_key_prefix: str = "",
        use_cache: bool = False,
        clear_cache: bool = False,
        debug: bool = False,
        start_time: float = 0,
        parsing_time: float = 0,
    ) -> Dict[str, Any]:
        """
        Get query response with optional caching support

        Args:
            db_collection: MongoDB collection object
            query: Query parameters
            pipeline: Optional base pipeline
            pipeline_count: Optional count pipeline
            cache_client: Optional cache client (Redis)
            cache_key_prefix: Prefix for cache keys
            use_cache: Whether to use caching
            clear_cache: Whether to clear cache before query
            debug: Whether to enable debug output
            start_time: Start time of the query
            parsing_time: Time spent parsing parameters
        """
        try:
            # Build pipelines
            pipeline_build_start = time.time()
            base_pipeline = self.make_aggregation_query(query, pipeline)
            count_pipeline = self.make_count_aggregation_query(query, pipeline_count)
            pipeline_build_time = time.time() - pipeline_build_start

            if debug:
                print("🔵 [DEBUG] Pipeline de agregación construido:")
                pprint(base_pipeline)
                print("🔵 [DEBUG] Pipeline de count construido:")
                pprint(count_pipeline)

                # Debug filters
                if "filters" in query:
                    filter_pipeline = self.build_filter_pipeline(query["filters"])
                    print("🔵 [DEBUG] Filtros aplicados:")
                    pprint(filter_pipeline)

                # Debug special operations
                if "populate" in query:
                    print("🔵 [DEBUG] Relaciones a popular:")
                    pprint(query["populate"])

                if "distinct" in query:
                    print("🔵 [DEBUG] Campos distinct:")
                    pprint(query["distinct"])

                if "sort" in query:
                    print("🔵 [DEBUG] Ordenamiento aplicado:")
                    pprint(query["sort"])

                if "pagination" in query:
                    print("🔵 [DEBUG] Paginación aplicada:")
                    pprint(query["pagination"])

            # Start MongoDB query timing
            mongodb_start_time = time.time()

            # Get data
            data_result = list(db_collection.aggregate(base_pipeline))

            # Get count
            if use_cache and cache_client:
                if debug:
                    print("🔵 [DEBUG] Configuración de cache:")
                    pprint(
                        {
                            "cache_key_prefix": cache_key_prefix,
                            "clear_cache": clear_cache,
                            "use_cache": use_cache,
                        }
                    )

                # Import cache utilities
                from ..cache import (
                    generate_cache_id,
                    get_or_set_cache,
                    datetime_serializer,
                )

                # Prepare cache key for meta (count)
                query_for_hash = deepcopy(query)
                query_for_hash.pop("pagination", None)
                query_hash = generate_cache_id(query_for_hash)
                count_key = f"{cache_key_prefix}:query:count:{query_hash}"

                if debug:
                    print("🔵 [DEBUG] Cache key generada:")
                    print(f"count_key: {count_key}")

                # Get or set meta from cache
                meta_result = get_or_set_cache(
                    cache_client,
                    count_key,
                    lambda: list(db_collection.aggregate(count_pipeline)),
                    clear_cache=(
                        f"{cache_key_prefix}:query:count:*" if clear_cache else False
                    ),
                    ttl=60 * 30,
                    serializer=lambda x: (
                        datetime_serializer(x[0]) if x else {"totalCount": 0}
                    ),
                )
            else:
                meta_result = list(db_collection.aggregate(count_pipeline))

            # End MongoDB query timing
            mongodb_time = time.time() - mongodb_start_time

            if debug:
                print("🔵 [DEBUG] Resultado de query de datos:")
                print(f"Registros encontrados: {len(data_result)}")
                if data_result:
                    print("Muestra del primer registro:")
                    pprint(data_result[0])
                    if len(data_result) > 1:
                        print(f"... y {len(data_result) - 1} registros más")
                else:
                    print("Sin datos encontrados")

                print("🔵 [DEBUG] Resultado de count:")
                pprint(meta_result)

            result = self.sanitize_result(query, data_result, meta_result)

            if debug:
                # Calculate total time
                total_time = time.time() - start_time

                print("🔵 [DEBUG] Respuesta final sanitizada:")
                preview_data = result.get("data", [])
                data_preview = {
                    "data_count": len(preview_data),
                    "first_record": preview_data[0] if preview_data else None,
                    "remaining_records": (
                        f"... y {len(preview_data) - 1} más"
                        if len(preview_data) > 1
                        else "ninguno más"
                    ),
                    "meta": result.get("meta", {}),
                    "has_pagination": "pagination" in query,
                }
                pprint(data_preview)

                print("🔵 [DEBUG] ⏱️  MÉTRICAS DE PERFORMANCE:")
                print(f"  📊 Tiempo de parsing/pre-consulta: {parsing_time:.3f}s")
                print(f"  🗄️  Tiempo real de consulta MongoDB: {mongodb_time:.3f}s")
                print(f"  🚀 Tiempo total de procesamiento: {total_time:.3f}s")
                print("=" * 60)

            return result
        except Exception as e:
            if debug:
                print(f"🔴 [DEBUG] Error en get_query_response: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e),
            )
