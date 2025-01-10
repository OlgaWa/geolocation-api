import os

from dotenv import load_dotenv

load_dotenv()

# Get environment variables
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")
IPSTACK_API_KEY = os.getenv("IPSTACK_API_KEY")
IPSTACK_URL = os.getenv("IPSTACK_URL")
