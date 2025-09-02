# OpenLink Python Utils

A comprehensive Python package providing reusable utilities for caching, data manipulation, parsing, and MongoDB query building. Developed by OpenLink SpA for use across multiple projects.

## Overview

This package abstracts common functionality for:

-  **Caching**: Redis-based caching utilities with serialization support
-  **Query Building**: MongoDB aggregation pipeline builders with advanced filtering, sorting, pagination, and population features

## Installation

Install from PyPI:

```bash
pip install oplnk-python-utils
```

Or install in development mode:

```bash
pip install -e /path/to/oplnk-python-utils
```

Add to your `requirements.txt`:

```
oplnk-python-utils>=1.0.0
```

## Core Module

The core module contains general-purpose utilities organized by functionality. These are the foundational utilities used by other modules and can be used independently.

### Data Utilities (`core.data`)

Functions for data structure manipulation and normalization.

```python
from oplnk_python_utils.core.data import normalize, merge_dicts

# Normalize data for consistent processing (useful for caching)
data = {"z": 1, "a": {"c": 3, "b": 2}}
normalized = normalize(data)
# Result: {"a": {"b": 2, "c": 3}, "z": 1} - keys sorted recursively

# Merge multiple dictionaries with nested structure support
result = merge_dicts(
    {"filters": {"name": "John"}},
    {"filters": {"age": 25}},
    {"sort": ["name:asc"]}
)
# Result: {"filters": {"name": ["John"], "age": 25}, "sort": ["name:asc"]}

# Advanced merging with arrays and conflicts
dict1 = {"tags": ["python"], "meta": {"version": 1}}
dict2 = {"tags": ["fastapi"], "meta": {"author": "team"}}
merged = merge_dicts(dict1, dict2)
# Result: {"tags": ["python", "fastapi"], "meta": {"version": 1, "author": "team"}}
```

#### Data Functions

-  **`normalize(value)`**: Recursively normalize data structures by sorting dictionary keys
-  **`merge_dicts(*dicts)`**: Intelligently merge multiple dictionaries with nested structure support

### Parsing Utilities (`core.parsing`)

Functions for parsing query parameters, type conversion, and safe field-path handling for MongoDB aggregation.

```python
from oplnk_python_utils.core.parsing import (
    parse_params_to_dict,
    infer_type,
    parse_key_string_to_list,
    parse_list_to_dict
)

# Parse nested query parameters (main function)
params = {
    "filters[name][$containsi]": "john",
    "filters[age][$gte]": "18",
    "pagination[page]": "1",
    "sort[0]": "name:asc",
    "populate[0]": "user"
}
parsed = parse_params_to_dict(params)
# Result: {
#   "filters": {"name": {"$containsi": "john"}, "age": {"$gte": 18}},
#   "pagination": {"page": 1},
#   "sort": ["name:asc"],
#   "populate": ["user"]
# }

# Smart type inference with various formats
value = infer_type("123")           # Returns: 123 (int)
value = infer_type("12.5")          # Returns: 12.5 (float)
value = infer_type("true")          # Returns: True (bool)
value = infer_type("false")         # Returns: False (bool)
value = infer_type("hello")         # Returns: "hello" (str)
value = infer_type(["1", "2"])      # Returns: [1, 2] (list with converted types)

# Lower-level parsing functions
keys = parse_key_string_to_list("filters[name][$eq]")
# Result: ["filters", "name", "$eq"]

nested_dict = parse_list_to_dict(["filters", "name", "$eq"], "john")
# Result: {"filters": {"name": {"$eq": "john"}}}
```

#### Parsing Functions

-  **`parse_params_to_dict(params)`**: Parse FastAPI QueryParams or dict into structured nested dictionary
-  **`infer_type(value)`**: Smart type inference from string values (supports int, float, bool, datetime, lists)
-  **`parse_key_string_to_list(s)`**: Parse bracketed notation strings like `"filters[name][$eq]"`
-  **`parse_list_to_dict(lst, value)`**: Convert key list and value into nested dictionary structure

#### Field Path Utilities for Aggregation (NEW)

-  **`normalize_field_path(field)`**: Normalize paths with array notation for MongoDB aggregation.
   -  Example: `"user.addresses[1].street" -> "user.addresses.1.street"`
-  **`validate_field_path(field)`**: Validate field paths for invalid characters before using them in pipelines.
-  **`build_aggregation_field_expression(field)`**: Produce a proper aggregation expression, automatically prefixing with `$` when needed.
   -  Example: `"user.addresses[1].street" -> "$user.addresses.1.street"`

### Serialization Utilities (`core.serialization`)

Functions for converting data types to serializable formats.

```python
from oplnk_python_utils.core.serialization import datetime_serializer
from datetime import datetime

# Serialize datetime objects for JSON/cache storage
data = {
    "created_at": datetime.now(),
    "users": [
        {"last_login": datetime.now(), "name": "John"},
        {"last_login": datetime.now(), "name": "Jane"}
    ],
    "metadata": {
        "processed_at": datetime.now()
    }
}

serialized = datetime_serializer(data)
# All datetime objects converted to ISO strings recursively
# Non-datetime values remain unchanged
```

#### Serialization Functions

-  **`datetime_serializer(data)`**: Recursively convert datetime objects to ISO format strings in any data structure

## Cache Module

Advanced caching utilities with Redis integration and intelligent cache key management. The module provides both low-level caching utilities and high-level endpoint decorators for comprehensive caching strategies.

### Low-Level Cache Utilities

```python
from oplnk_python_utils.cache import generate_cache_id, get_or_set_cache, invalidate_cache_keys

# Generate consistent cache keys from complex data
cache_key = generate_cache_id({
    "filters": {"name": "John", "status": "active"},
    "sort": ["created_at:desc"]
})
# Automatically normalizes data internally and creates SHA256 hash

# Get from cache or execute a function and cache result (sync fetch_func)
def fetch_users():
    # Some expensive database operation (sync example)
    return list(db.collection.find({"status": "active"}))

result = get_or_set_cache(
    redis_client=redis,
    cache_key="user_query_abc123",
    fetch_func=fetch_users,  # zero-arg callable
    ttl=3600,  # 1 hour
    serializer=datetime_serializer
)

# Invalidate multiple cache keys by pattern
invalidated_count = invalidate_cache_keys(redis, "user_*")
print(f"Invalidated {invalidated_count} cache entries")
```

### Endpoint-Level Caching (NEW)

High-level decorators for caching entire endpoint responses with automatic cache key generation and tag-based invalidation.

```python
from oplnk_python_utils.cache import cache_response, cache_factory, build_cache_key, invalidate_tag
from fastapi import FastAPI, Request
import redis

app = FastAPI()
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Method 1: Direct decorator usage
@app.get("/users")
@cache_response(
    redis_client=redis_client,
    api_name="myapi",
    collection="users",
    endpoint_type="read",
    tags=["users", "all_data"],
    ttl=3600,  # 1 hour
    use_cache=True
)
async def get_users(request: Request):
    # Your endpoint logic here
    return {"users": [...]}

# Method 2: Factory pattern for reusable decorators
users_cache = cache_factory(redis_client, "myapi", "users")

@app.get("/users")
@users_cache(
    endpoint_type="read",
    tags=["users", "public"],
    ttl=1800  # 30 minutes
)
async def get_users(request: Request):
    return {"users": [...]}

@app.post("/users")
@users_cache(
    endpoint_type="create",
    tags=["users"],
    ttl=0  # No caching for write operations
)
async def create_user(request: Request):
    # Automatically invalidates 'users' tag after creation
    return {"created": True}

# Manual cache key building (build_cache_key is async)
@app.get("/custom")
async def custom_endpoint(request: Request):
    cache_key = await build_cache_key(request, "myapi", "custom", "read")
    # Use cache_key for custom caching logic
    return {"data": "custom"}

# Tag-based cache invalidation
@app.delete("/users/{user_id}")
async def delete_user(user_id: str):
    # Delete user logic here
    # ...

    # Invalidate all cached responses tagged with 'users'
    invalidate_tag(redis_client, "users")
    return {"deleted": True}
```

### Cache Key Structure

The caching system generates structured cache keys based on:

-  **API Name**: Namespace for your application
-  **Collection**: The data collection being cached
-  **Endpoint Type**: Type of operation (read, create, update, delete)
-  **Query Hash**: SHA256 hash of normalized query parameters

Example cache key: `myapi:users:read:a1b2c3d4e5f6...`

### Tag-Based Cache Management

```python
# Cache responses with multiple tags
@cache_response(
    redis_client=redis_client,
    api_name="ecommerce",
    collection="products",
    endpoint_type="read",
    tags=["products", "catalog", "public_data"],
    ttl=7200  # 2 hours
)
async def get_products(request: Request):
    return {"products": [...]}

# Invalidate specific tag groups
invalidate_tag(redis_client, "products")      # Invalidates all product-related cache
invalidate_tag(redis_client, "catalog")       # Invalidates all catalog cache
invalidate_tag(redis_client, "public_data")   # Invalidates all public data cache
```

### Cache Functions Reference

#### Low-Level Functions

-  **`generate_cache_id(params)`**: Generate SHA256 hash from normalized data for consistent cache keys
-  **`get_or_set_cache(redis_client, cache_key, fetch_func, clear_cache=False, ttl=None, serializer=None)`**: Get cached result or execute function and cache with automatic serialization
-  **`invalidate_cache_keys(redis_client, pattern)`**: Delete cache keys matching pattern (supports wildcards)

#### Endpoint Caching Functions

-  **`build_cache_key(request, api_name, collection, endpoint_type)`**: Build structured cache key from request parameters
-  **`cache_response(redis_client, api_name, collection, endpoint_type, tags, ttl=None, use_cache=True)`**: Decorator for caching endpoint responses
-  **`cache_factory(redis_client, api_name, collection)`**: Factory function to create reusable cache decorators
-  **`invalidate_tag(redis_client, tag)`**: Invalidate all cache keys associated with a specific tag

### Automatic Cache Invalidation

The caching system supports automatic cache clearing via query parameters:

```python
# Clear cache before executing endpoint
GET /users?clear_cache=true

# This will:
# 1. Invalidate the collection tag (e.g., "users")
# 2. Execute the endpoint normally
# 3. Cache the fresh response
```

## Query Module

The query module provides a MongoDB aggregation pipeline builder with advanced features.

### Usage

```python
from oplnk_python_utils.query import QueryBuilder
from pymongo import MongoClient

# Initialize MongoDB
db = MongoClient()["mydb"]
collection = db["users"]

# Create query builder
query_builder = QueryBuilder(
    collection_prefix="myapp",
    relations=[
        ["User", "user_id", "myapp", "users"],
        ["Role", "role_ids", "myapp", "roles"]
    ]
)

# Build query
query = {
    "filters": {
        "name": {"$containsi": "john"},
        "age": {"$gte": 18},
        "$or": [
            {"status": {"$eq": "active"}},
            {"last_login": {"$gte": "2023-01-01"}}
        ]
    },
    "sort": ["name:asc", "age:desc"],
    "pagination": {"page": 1, "pageSize": 10},
    "populate": ["role"],
    "fields": ["name", "email", "age"]
}

# Method 1: Using parsed query dictionary
results = query_builder.get_query_response(
    db_collection=collection,
    query=query,
    cache_client=redis_client,
    cache_key_prefix="users",
    use_cache=True
)

# Method 2: Using raw query parameters (like from FastAPI request)
raw_params = {
    "filters[name][$containsi]": "john",
    "filters[age][$gte]": "18",
    "sort[0]": "name:asc",
    "pagination[page]": "1",
    "pagination[pageSize]": "10"
}

# Option A: Parse manually then use get_query_response
from oplnk_python_utils.core.parsing import parse_params_to_dict
parsed_query = parse_params_to_dict(raw_params)
results = query_builder.get_query_response(
    db_collection=collection,
    query=parsed_query,
    cache_client=redis_client,
    cache_key_prefix="users",
    use_cache=True
)

# Option B: Use read_query with automatic parsing (recommended)
results = query_builder.read_query(
    db_collection=collection,
    params=raw_params,  # Will be parsed automatically using core.parsing
    cache_client=redis_client,
    cache_key_prefix="users",
    use_cache=False  # Note: Endpoint-level caching is now preferred over query-level caching
)

print(results)
# {
#     "data": [...],
#     "meta": {"totalCount": 150}
# }
```

### QueryBuilder Methods

#### Pipeline Builders

-  **`build_filter_pipeline(filters)`**: Build MongoDB filter pipeline
-  **`build_sort_pipeline(sort_params)`**: Build sort pipeline
-  **`build_fields_pipeline(fields_params)`**: Build field projection pipeline
-  **`build_distinct_pipeline(distinct_params)`**: Build distinct pipeline
-  **`build_pagination_pipeline(pagination_params)`**: Build pagination pipeline
-  **`build_populate_pipeline(populate_params)`**: Build population pipeline

#### Aggregation Builders

-  **`make_aggregation_query(query, base_pipeline=None)`**: Build complete aggregation pipeline
-  **`make_count_aggregation_query(query, base_pipeline=None)`**: Build count aggregation pipeline

#### Query Execution

-  **`get_query_response(db_collection, query, ...)`**: Execute query with optional caching
-  **`read_query(db_collection, params=None, query=None, ...)`**: Complete query method with parameter parsing

#### Core Module Integration

The QueryBuilder class leverages utilities from the core module for enhanced functionality:

-  **Parameter parsing**: Uses `core.parsing.parse_params_to_dict()` for automatic query parameter parsing
-  **Data normalization**: Uses `core.data.normalize()` for consistent cache key generation
-  **Datetime serialization**: Uses `core.serialization.datetime_serializer()` for cache-friendly data

See the [Core Module](#core-module) section for detailed documentation of these utilities.

### Supported Filter Operators

#### Text Search

-  `$contains`, `$containsi` (case-insensitive)
-  `$notContains`, `$notContainsi`
-  `$startsWith`, `$startsWithi`
-  `$endsWith`, `$endsWithi`
-  `$eqi` (case-insensitive equality), `$nei`

#### Comparison

-  `$eq`, `$ne`, `$lt`, `$lte`, `$gt`, `$gte`
-  `$in`, `$notIn`
-  `$between` (requires array with 2 elements)

#### Logical

-  `$and`, `$or`

#### Existence

-  `$exists`, `$notExists`
-  `$null`, `$notNull`

#### Arrays

-  `$listContains`, `$listNotContains`

### Query Structure

```python
query = {
    "filters": {
        # Filter conditions
        "field": {"$operator": "value"},
        "$or": [
            {"field1": {"$eq": "value1"}},
            {"field2": {"$gt": 10}}
        ]
    },
    "sort": ["field1:asc", "field2:desc"],
    "pagination": {
        "page": 1,
        "pageSize": 20
    },
    "populate": ["relation1", "relation2"],  # or {"relation1": True}
    "fields": ["field1", "field2", "field3"],
    "distinct": ["field1", "field2"]
}
```

## Integration with Existing CRUD

### Before (Original CRUD + Endpoints)

```python
# CRUD Class - 30+ lines of complex query logic
class CRUD:
    def __init__(self, collection, relations=[]):
        # ... original implementation

    def read_query(self, query, pipeline=None, pipeline_count=None, use_cache=False):
        # ... 30+ lines of complex caching and query logic

# Endpoint - Manual parameter parsing
from src.utils import parse_params_to_dict

@router.get("/query")
async def get_data(request: Request):
    params = request.query_params
    query = parse_params_to_dict(params)  # Manual parsing
    return crud.read_query(query, pipeline=base_pipeline, use_cache=True)
```

### After (Using Utils Package)

```python
# CRUD Class - Now super clean!
from oplnk_python_utils.query import QueryBuilder

class CRUD(QueryBuilder):
    def __init__(self, collection, relations=[]):
        self.collection = collection
        self.db = db[self.collection]
        super().__init__(collection_prefix=PREFIX, relations=relations)

    def read_query(self, params=None, query=None, pipeline=None, pipeline_count=None):
        # Just 4 lines! All complexity abstracted away
        return super().read_query(
            db_collection=self.db, params=params, query=query,
            pipeline=pipeline, pipeline_count=pipeline_count
        )

# Endpoint - With new endpoint-level caching!
from oplnk_python_utils.cache import cache_factory
from oplnk_python_utils.core.parsing import parse_params_to_dict

# Create reusable cache decorator for this collection
users_cache = cache_factory(redis_client, "myapp", "users")

@router.get("/query")
@users_cache(
    endpoint_type="read",
    tags=["users", "queries"],
    ttl=3600  # Cache for 1 hour
)
async def get_data(request: Request):
    # Option 1: Manual parsing (explicit control)
    query = parse_params_to_dict(request.query_params)
    return crud.read_query(query=query, pipeline=base_pipeline)

    # Option 2: Automatic parsing (convenience)
    return crud.read_query(
        params=request.query_params,  # Parsed automatically
        pipeline=base_pipeline
    )

# Write operations with cache invalidation
@router.post("/users")
@users_cache(
    endpoint_type="create",
    tags=["users"],
    ttl=0  # No caching for write operations
)
async def create_user(request: Request, user_data: dict):
    result = crud.create(user_data)
    # Cache is automatically invalidated due to 'users' tag
    return result
```

## Advanced Features

### Custom Relation Definitions

```python
relations = [
    # Basic relation: [Type, field_name, prefix, collection_name]
    ["User", "user_id", "myapp", "users"],

    # Array relation
    ["Role", "role_ids", "myapp", "roles"],

    # Custom alias: [Type, field_name, prefix, collection_name, alias]
    ["Department", "dept_id", "myapp", "departments", "department"],

    # Special Users relation (built-in handling)
    ["Users", "person", "", ""]
]
```

### Custom Pipelines

```python
# Custom base pipeline
base_pipeline = [
    {"$match": {"deleted": False}},
    {"$lookup": {...}}
]

results = query_builder.get_query_response(
    db_collection=collection,
    query=query,
    pipeline=base_pipeline,  # Custom data pipeline
    pipeline_count=custom_count_pipeline  # Custom count pipeline
)
```

### Smart Text Search

The query builder automatically handles mixed-type searching:

```python
# Search for "10" will match:
# - String fields containing "10"
# - Numeric fields equal to 10
# - Numeric fields in range 10.0-10.999
# - Numbers starting with 10 (100, 1000, etc.)
filters = {
    "amount": {"$containsi": "10"}
}
```

## Dependencies

-  `pymongo`: MongoDB driver
-  `redis`: Redis client
-  `fastapi`: For HTTP exceptions

## License

This package is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

This package is developed and maintained by OpenLink SpA. For questions or support, please contact [contacto@openlink.cl](mailto:contacto@openlink.cl).

## Repository

Source code is available at: [https://github.com/openlinkspa/oplnk-python-utils](https://github.com/openlinkspa/oplnk-python-utils)
