import os
from dotenv import load_dotenv

load_dotenv()

TALLY_URL = os.getenv("TALLY_URL", "http://localhost:9000")

DATABASE_URL = os.getenv("DATABASE_URL")

CONNECTOR_NAME = "tally-connector"
CONNECTOR_VERSION = "v1"
SOURCE = "tally-http-xml"
