import certifi
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from base_utils.exception import ImproperConfigurationError
import asyncio

# Global variables for MongoDB client and database name
client: AsyncIOMotorClient | None = None
db_name = None


# Function to initialize the MongoDB connection
async def init(
    test: bool,
    db_setup_data: dict,
    loop: asyncio.AbstractEventLoop = asyncio.get_event_loop(),
) -> None:
    """
    Initialize the MongoDB client and Beanie ODM.

    Args:
        test (bool): Whether the environment is for testing.
        db_setup_data (dict): Dictionary containing MongoDB setup data.
        loop (asyncio.AbstractEventLoop): Event loop for async operations.

    Raises:
        ImproperConfigurationError: If required MongoDB configuration is missing.
    """
    global client
    global db_name

    # Extract connection parameters
    conn_params = {
        "host": db_setup_data.get("host"),
        "username": db_setup_data.get("username"),
        "password": db_setup_data.get("password"),
    }
    prod = db_setup_data.get("prod")
    db_name = db_setup_data.get("db_name")

    # Validate connection parameters
    if all(conn_params.values()):
        # Initialize the MongoDB client
        client = AsyncIOMotorClient(
            host=f"mongodb+srv://{conn_params['host']}/?retryWrites=true&w=majority",
            username=conn_params["username"],
            password=conn_params["password"],
            uuidRepresentation="standard",
            tlsCAFile=certifi.where(),
            io_loop=loop,
        )
        # Verify the connection
        print(await client.server_info())
    else:
        raise ImproperConfigurationError("Problem with MongoDB environment variables")

    # Adjust database name based on environment
    if prod == "false" and not test:
        db_name += "_dev"
    elif prod == "false" and test:
        db_name += "_test"

    # Initialize Beanie ODM
    if db_name is not None:
        await init_beanie(
            database=client[db_name],
            document_models=db_setup_data.get("document_models"),
            allow_index_dropping=True,
            recreate_views=True,
        )
        return client, db_name
    else:
        raise ImproperConfigurationError("Problem with MongoDB environment variables")


# Function to close the MongoDB connection
async def close():
    """
    Close the MongoDB client connection.

    Raises:
        Exception: If an error occurs while closing the connection.
    """
    try:
        global client
        client.close()
    except Exception as e:
        raise e
