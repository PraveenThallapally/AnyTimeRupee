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
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        create_table = """
        CREATE TABLE IF NOT EXISTS persons (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            phone VARCHAR(20),
            address TEXT,
            age INT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        
        cursor.execute(create_table)
        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Database initialized successfully! Table 'persons' ready.")
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
