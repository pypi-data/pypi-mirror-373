import os
from ardent import ArdentClient, ArdentError, ArdentValidationError
from dotenv import load_dotenv
from uuid import uuid4

load_dotenv()

Ardent_Client = ArdentClient(
    public_key=os.getenv("PUBLIC_KEY"), 
    secret_key=os.getenv("SECRET_KEY"),
    base_url=os.getenv("BASE_URL"),
)