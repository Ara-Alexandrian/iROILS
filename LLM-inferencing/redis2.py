# Import the RedisManager class from your Python script
from redis_class import RedisManager
from redis_class2 import RedisManager2







# Create an instance of the RedisManager class
# manager = RedisManager()
manager2 = RedisManager2()

# manager.run_all_summaries_and_evaluations()


# Check if the Redis connection was successfully created
if manager2.redis_conn:
    # Clear model data
    # Uncomment the next line to clear specific model data
    # manager.clear_model_data(model_name="mistral", field_name="LLM Summary")


    manager2.process_and_update_redis_data('2Apple@@')


    # Generate summaries
    # manager.generate_summaries(resume=False)
    # generate_all_summaries

    # Generate evaluations
    # manager.evaluate_summaries(resume=False)

    # Create Excel from Redis
    # manager.create_excel_from_redis()
else:
    print("Failed to connect to Redis server.")