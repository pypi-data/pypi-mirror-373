"""
Cache utilities - Generic caching functions that can be used across projects
"""

import hashlib
import json
from typing import Callable, Any, Optional, Union
from fastapi.encoders import jsonable_encoder
from bson.objectid import ObjectId
from fastapi import Request
import functools

# Import core utilities
from ..core.data import normalize
from ..core.serialization import datetime_serializer


def generate_cache_id(params: dict) -> str:
    """
    Utility to generate a cache key hash from a dictionary.
    Creates a consistent hash based on normalized dictionary content.

    Args:
        params: Dictionary of parameters to hash

    Returns:
        Cache key string
    """
    normalized = normalize(params)
    encoded_data = jsonable_encoder(normalized, custom_encoder={ObjectId: str})
    serialized = json.dumps(encoded_data, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def get_or_set_cache(
    redis_client,
    cache_key: str,
    fetch_func: Callable,
    clear_cache: Union[str, bool] = False,
    ttl: Optional[int] = None,
    serializer: Optional[Callable] = None,
) -> Any:
    """
    Retrieve data from cache if available, otherwise fetch, cache, and return it.
    Optionally clear cache before fetching.

    Args:
        redis_client: Redis client instance
        cache_key: Key to use for caching
        fetch_func: Function to call if cache miss
        clear_cache: Pattern to clear or boolean to clear specific key
        ttl: Time to live in seconds
        serializer: Function to serialize data before caching

    Returns:
        Cached or fetched data
    """
    if clear_cache:
        invalidate_cache_keys(
            redis_client, clear_cache if isinstance(clear_cache, str) else cache_key
        )

    if redis_client.exists(cache_key):
        return json.loads(redis_client.get(cache_key))

    data = fetch_func()
    if serializer:
        data = serializer(data)

    encoded_data = jsonable_encoder(data, custom_encoder={ObjectId: str})
    redis_client.set(cache_key, json.dumps(encoded_data), ex=ttl)
    return encoded_data


def invalidate_cache_keys(redis_client, pattern: str) -> int:
    """
    Utility to invalidate cache keys matching a pattern.

    Args:
        redis_client: Redis client instance
        pattern: Pattern to match keys for deletion

    Returns:
        Number of keys deleted
    """
    cursor = 0
    batch_size = 1000
    total_deleted = 0

    while True:
        cursor, keys = redis_client.scan(cursor=cursor, match=pattern, count=batch_size)
        if keys:
            redis_client.unlink(*keys)
            total_deleted += len(keys)
        if cursor == 0:
            break

    return total_deleted


async def build_cache_key(
    request: Request, api_name: str, collection: str, endpoint_type: str
) -> str:
    """
    Builds a cache key based on the request, api name, collection, and endpoint type.

    Incorporates HTTP method, URL path, path parameters and query parameters to
    avoid collisions between routes that differ only by path params.

    Args:
        request: FastAPI request object
        api_name: Name of the API
        collection: Name of the collection
        endpoint_type: Type of endpoint

    Returns:
        Cache key string
    """
    # Ensure plain dicts for hashing
    query_params_dict = dict(request.query_params) if request.query_params else {}
    path_params_dict = (
        dict(request.path_params) if getattr(request, "path_params", None) else {}
    )

    key_material = {
        "method": request.method,
        "path": request.url.path,
        "path_params": path_params_dict,
        "query": query_params_dict,
    }

    # Include request body for methods where it affects the response identity
    if request.method in {"POST", "PUT"}:
        content_type = (request.headers.get("content-type") or "").split(";")[0].lower()
        body_hash: Optional[str] = None
        if content_type == "application/json":
            try:
                json_body = await request.json()
                normalized_body = normalize(json_body)
                encoded_body = jsonable_encoder(
                    normalized_body, custom_encoder={ObjectId: str}
                )
                key_material["body"] = encoded_body
            except Exception:
                body_bytes = await request.body()
                if body_bytes:
                    body_hash = hashlib.sha256(body_bytes).hexdigest()
        else:
            body_bytes = await request.body()
            if body_bytes:
                body_hash = hashlib.sha256(body_bytes).hexdigest()

        if body_hash:
            key_material["body_hash"] = body_hash

    hashed = generate_cache_id(key_material)
    return f"{api_name}:{collection}:{endpoint_type}:{hashed}"


def cache_response(
    redis_client,
    api_name: str,
    collection: str,
    endpoint_type: str,
    tags: list[str],
    ttl: int | None = None,
    use_cache: bool = True,
):
    """
    Decorator to cache the response of an endpoint.

    Args:
        redis_client: Redis client instance
        api_name: Name of the API
        collection: Name of the collection
        endpoint_type: Type of endpoint
        tags: List of tags to use for caching
        ttl: Time to live in seconds
        use_cache: Whether to use cache

    Returns:
        Decorator function
    """

    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            if not use_cache:
                return await func(*args, **kwargs)

            # Detectar el Request
            request: Optional[Request] = kwargs.get("request")
            if request is None:
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break
            if request is None:
                raise ValueError("Request object not found in endpoint parameters.")

            query_params = request.query_params
            clear_cache_value = query_params.get("clear_cache")
            if isinstance(clear_cache_value, str):
                clear_cache_flag = clear_cache_value.lower() in {
                    "1",
                    "true",
                    "yes",
                    "y",
                }
            else:
                clear_cache_flag = bool(clear_cache_value)
            if clear_cache_flag:
                invalidate_tag(redis_client, f"{collection}")

            # Construir clave
            cache_key = await build_cache_key(
                request, api_name, collection, endpoint_type
            )
            if redis_client.exists(cache_key):
                return json.loads(redis_client.get(cache_key))

            response = await func(*args, **kwargs)
            encoded_data = jsonable_encoder(response, custom_encoder={ObjectId: str})
            redis_client.set(cache_key, json.dumps(encoded_data), ex=ttl)
            for tag in tags:
                redis_client.sadd(f"tag:{tag}", cache_key)

            return encoded_data

        return wrapper

    return decorator


def cache_factory(redis_client, api_name: str, collection: str):
    """
    Factory to create cache decorators for different endpoint types.

    Args:
        redis_client: Redis client instance
        api_name: Name of the API
        collection: Name of the collection

    Returns:
        Decorator function
    """

    def wrapper(
        endpoint_type: str,
        tags: list[str],
        ttl: int | None = None,
        use_cache: bool = True,
    ):
        return cache_response(
            redis_client=redis_client,
            api_name=api_name,
            collection=collection,
            endpoint_type=endpoint_type,
            tags=tags,
            ttl=ttl,
            use_cache=use_cache,
        )

    return wrapper


def invalidate_tag(redis_client, tag: str):
    """
    Utility to invalidate cache keys associated with a tag.

    Args:
        redis_client: Redis client instance
        tag: Tag to invalidate
    """
    keys = redis_client.smembers(f"tag:{tag}")
    for key in keys:
        redis_client.delete(key)
    redis_client.delete(f"tag:{tag}")
