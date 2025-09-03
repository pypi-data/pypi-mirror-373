import os
from dotenv import load_dotenv
from Osdental.Database.Connection import Connection
from Osdental.Encryptor.Aes import AES

load_dotenv(dotenv_path='.env', override=True)

db_catalog = Connection(os.getenv('DATABASE_CATALOG'))
db_security = Connection(os.getenv('DATABASE_SECURITY'))
db_connection = Connection(os.getenv('DATABASE_CONNECTION'))
microservice_name = os.getenv('MICROSERVICE_NAME')
jwt_user_key = os.getenv('JWT_USER_KEY')
aes = AES()
environment = os.getenv('ENVIRONMENT')
microservice_name = os.getenv('MICROSERVICE_NAME')
microservice_version = os.getenv('MICROSERVICE_VERSION')