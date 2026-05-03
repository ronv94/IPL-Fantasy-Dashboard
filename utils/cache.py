from flask_caching import Cache

cache = Cache(config={
    "CACHE_TYPE": "SimpleCache",
    "CACHE_DEFAULT_TIMEOUT": 300,
})


def clear_data_cache():
    """Flush all cached data. Call after any DB write."""
    cache.clear()
