import json
import random
import redis


# Function to create and return a Redis client
async def redis_client(host, port):
    redis_client = redis.Redis(host=host, port=port, decode_responses=True)
    return redis_client


# Function to set a cache value in Redis
async def set_cache(
    key: str,
    value: dict,
    redis_client_data: dict,
    expire_minutes: float,
    allow_random: bool = False,
):
    """
    Set a key-value pair in Redis with an optional random expiration time.

    Args:
        key (str): The key to set in Redis.
        value (dict): The value to store, which will be JSON-encoded.
        redis_client_data (dict): Dictionary containing Redis host and port.
        expire_minutes (float): Expiration time in minutes.
        allow_random (bool): If True, expiration time will be randomized.
    """
    try:
        # Create a Redis client
        r_client = await redis_client(
            redis_client_data["host"], redis_client_data["port"]
        )
        # Set the key-value pair with expiration time
        r_client.set(
            name=key,
            value=json.dumps(value),  # Serialize the value to JSON
            ex=(
                expire_minutes * random.randint(60, 120)  # Random expiration
                if allow_random
                else expire_minutes * 60  # Fixed expiration
            ),
        )
    except Exception as e:
        # Raise any exceptions encountered
        raise e


# Function to get a cache value from Redis
async def get_cache(key: str, redis_client_data: dict):
    """
    Retrieve a value from Redis by key.

    Args:
        key (str): The key to retrieve from Redis.
        redis_client_data (dict): Dictionary containing Redis host and port.

    Returns:
        dict or None: The value associated with the key, or None if not found.
    """
    try:
        # Create a Redis client
        r_client = await redis_client(
            redis_client_data["host"], redis_client_data["port"]
        )
        # Get the value associated with the key
        value = r_client.get(key)
        # Deserialize the JSON value if it exists
        return json.loads(value) if value else None
    except Exception as e:
        # Raise any exceptions encountered
        raise e


async def publish_message(channel: str, message: str, redis_client_data: dict):
    """
    Publish a message to a Redis channel.

    Args:
        channel (str): The channel to publish the message to.
        message (str): The message to publish.
        redis_client_data (dict): Dictionary containing Redis host and port.
    """
    try:
        # Create a Redis client
        r_client = await redis_client(
            redis_client_data["host"], redis_client_data["port"]
        )
        # Publish the message to the specified channel
        r_client.publish(channel, message)
    except Exception as e:
        # Raise any exceptions encountered
        raise e
    

async def subscribe_to_channel(channel: str, redis_client_data: dict):
    """
    Subscribe to a Redis channel and yield messages as they arrive.

    Args:
        channel (str): The channel to subscribe to.
        redis_client_data (dict): Dictionary containing Redis host and port.

    Yields:
        str: Messages received from the subscribed channel.
    """
    try:
        # Create a Redis client
        r_client = await redis_client(
            redis_client_data["host"], redis_client_data["port"]
        )
        pubsub = r_client.pubsub()
        pubsub.subscribe(channel)

        # Listen for messages on the subscribed channel
        for message in pubsub.listen():
            if message["type"] == "message":
                yield message["data"]
    except Exception as e:
        # Raise any exceptions encountered
        raise e