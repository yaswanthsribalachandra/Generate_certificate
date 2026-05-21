from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
import os

# LOAD ENV FILE
load_dotenv()

# GET CONNECTION STRING
connection_string = os.getenv(
    "AZURE_STORAGE_CONNECTION_STRING"
)

# DEBUG
print("CONNECTION:", connection_string)

# CHECK
if not connection_string:

    raise ValueError(
        "AZURE_STORAGE_CONNECTION_STRING missing"
    )

# CREATE CLIENT
blob_service_client = (
    BlobServiceClient.from_connection_string(
        connection_string
    )
)

# CONTAINERS
CACHE_CONTAINER = "cache280"

CERT_CONTAINER = "certificatestorage2"

print(
    "Azure Blob Connected Successfully"
)