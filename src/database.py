import boto3
import json
from botocore.exceptions import ClientError
import mysql.connector
 
def get_secret():
    secret_name = "my-app-db-credentials"
    region_name = "us-west-2"
 
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )
 
    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        raise e
 
    secret = json.loads(get_secret_value_response['SecretString'])
    return secret
 
# Get credentials
credentials = get_secret()
 
DB_HOST = credentials['DB_HOST']
DB_USER = credentials['DB_USER']
DB_PASSWORD = credentials['DB_PASSWORD']
DB_NAME = credentials['DB_NAME']
DB_PORT = int(credentials['DB_PORT'])
 
def get_db_connection():
    connection = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        port=DB_PORT
    )
    return connection
 
def init_database():
    pass
