import redis
import json

def connect_to_redis(redis_host, redis_port, redis_password):
    try:
        # Connect to Redis server
        r = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password, decode_responses=True)
        return r
    except Exception as e:
        print(f"Failed to connect to Redis server: {e}")
        return None

def probe_redis(r):
    # Get all keys in Redis
    keys = r.keys('*')

    # Iterate over each key
    for key in keys:
        # Get the type of the key
        key_type = r.type(key)
        print(f"Key: {key}")
        print(f"Type: {key_type}")

        # Get and print the value of the key based on its type
        if key_type == 'string':
            value = r.get(key)
            print(f"Value: {value}")
        elif key_type == 'hash':
            value = r.hgetall(key)
            print(f"Value: {json.dumps(value, indent=4)}")
        elif key_type == 'list':
            value = r.lrange(key, 0, -1)
            print(f"Value: {json.dumps(value, indent=4)}")
        elif key_type == 'set':
            value = r.smembers(key)
            print(f"Value: {json.dumps(list(value), indent=4)}")
        elif key_type == 'zset':
            value = r.zrange(key, 0, -1, withscores=True)
            print(f"Value: {json.dumps(value, indent=4)}")
        print()

# Example usage:
redis_host = "192.168.1.4"
redis_port = 6379
redis_password = "2Apple@@"

# Connect to Redis
redis_conn = connect_to_redis(redis_host, redis_port, redis_password)

if redis_conn:
    # Probe Redis
    probe_redis(redis_conn)
