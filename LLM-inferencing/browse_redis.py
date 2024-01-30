import math
import redis
import json


# Setup Redis connection - Modify these variables as per your environment
redis_host = "192.168.1.4"
redis_port = 6379
redis_password = ""

def connect_to_redis(redis_host, redis_port, redis_password):
    try:
        r = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password, decode_responses=True)
        return r
    except Exception as e:
        print(f"Failed to connect to Redis server: {e}")
        return None

def browse_redis_data(r, page_size=10):
    try:
        cursor = '0'
        page_num = 1
        
        # Total keys for pagination
        total_keys = r.dbsize()
        total_pages = math.ceil(total_keys / page_size)

        while True:
            cursor, keys = r.scan(cursor=cursor, count=page_size)
            print(f"\nPage {page_num}/{total_pages} (Showing {len(keys)} records):\n")
            print('-' * 100)  # Adding a separator for each page

            for key in keys:
                narrative = r.hget(key, 'Narrative') if r.hexists(key, 'Narrative') else 'No narrative'
                summary = r.hget(key, 'mistral:LLM Summary') if r.hexists(key, 'mistral:LLM Summary') else 'No summary'
                
                print(f"Event: {key}")
                print(f"\nNarrative:\n{narrative}")
                print(f"\nSummary:\n{summary}")
                print('\n' + '-' * 100)  # Adding a separator for each record

            if cursor == '0':
                break

            input_choice = input("\nPress Enter to continue to the next page or type 'exit' to quit: ").strip().lower()
            if input_choice == 'exit':
                break
            
            page_num += 1

    except Exception as e:
        print(f"Error occurred while browsing Redis data: {e}")


# Connect to Redis
redis_conn = connect_to_redis(redis_host, redis_port, redis_password)

# Run the browser function if the connection is successful
if redis_conn:
    browse_redis_data(redis_conn, page_size=5)  # Customize the page_size as needed
