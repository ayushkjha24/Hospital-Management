import redis
from functools import wraps
import json

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_result(expire_time=300):  # 5 min default
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            cache_key = f"{f.__name__}:{str(args)}:{str(kwargs)}"
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            result = f(*args, **kwargs)
            redis_client.setex(cache_key, expire_time, json.dumps(result, default=str))
            return result
        return wrapper
    return decorator