import redis
from functools import wraps
import json

redis_client = None

def init_cache(app):
    global redis_client
    redis_client = redis.from_url(app.config["REDIS_URL"])

def cache_result(expire_time=300):  # 5 min default
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if redis_client is None:
                return f(*args, **kwargs)

            cache_key = f"{f.__name__}:{str(args)}:{str(kwargs)}"
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            result = f(*args, **kwargs)
            redis_client.setex(cache_key, expire_time, json.dumps(result, default=str))
            return result
        return wrapper
    return decorator

def test_cache():
    redis_client.set("ping", "pong", ex=60)
    value = redis_client.get("ping")
    return value