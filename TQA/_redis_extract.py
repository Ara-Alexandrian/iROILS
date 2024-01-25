import pandas as pd
import redis

# Load the data from Excel file
excel_file_path = r'TQA/extracted.xlsx'  # Change this to your actual file path
df = pd.read_excel(excel_file_path)

# Assuming the Redis server is on localhost and the default port, with no password
# Change these to your actual Redis server details

redis_host = "192.168.1.4"
redis_port = 6379
redis_password = ""

def fetch_data_from_redis(redis_host, redis_port, redis_password, event_keys):
    try:
        # Connect to Redis server
        r = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password, decode_responses=True)

        all_events = []
        # Retrieve and print the data for each event key
        for key in event_keys:
            event_data = r.hgetall(key)
            if event_data:
                print(f"Data for {key}: {event_data}")
                all_events.append(event_data)
            else:
                print(f"No data found for {key}")

        # Convert the list of dictionaries to a pandas DataFrame
        df = pd.DataFrame(all_events)
        return df
    
    except Exception as e:
        print(e)




# Sample list of event keys to fetch from Redis
# Replace these with the actual event keys you've used
sample_event_keys = ['event:37104', 'event:36888', 'event:36747']

# Fetch data from Redis and store it in a DataFrame
events_df = fetch_data_from_redis(redis_host, redis_port, redis_password, sample_event_keys)

# # Limit to the first 10 event keys
# events_df = fetch_data_from_redis(redis_host, redis_port, redis_password, sample_event_keys[:10])

# Print the resulting DataFrame
print(events_df)



def fetch_near_miss_events(redis_host, redis_port, redis_password):
    try:
        # Connect to Redis server
        r = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password, decode_responses=True)

        # Use the SCAN command to fetch keys
        near_miss_events = []
        cursor = '0'
        while True:
            cursor, keys = r.scan(cursor=cursor, match='event:*', count=100)
            for key in keys:
                event_data = r.hgetall(key)
                if event_data.get('104.Classification') == 'Near-miss' and len(near_miss_events) < 10:
                    near_miss_events.append(event_data)
                    if len(near_miss_events) == 10:
                        break
            if cursor == '0' or len(near_miss_events) == 10:
                break  # Break when scan has returned to the start or we've found 10 events

        return near_miss_events
    
    except Exception as e:
        print(e)

# Fetch near miss events from Redis and store it in a DataFrame
near_miss_events = fetch_near_miss_events(redis_host, redis_port, redis_password)

# Convert the list of dictionaries to a pandas DataFrame
events_df = pd.DataFrame(near_miss_events)

# Print the resulting DataFrame
print(events_df)
