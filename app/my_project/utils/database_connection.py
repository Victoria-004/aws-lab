import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv() 

def get_db_connection():
    config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD'),
        'database': os.getenv('DB_NAME', 'lab3_db'),
        'port': int(os.getenv('DB_PORT', '3306')),
        'charset': 'utf8mb4',
        'collation': 'utf8mb4_unicode_ci'
    }
    return mysql.connector.connect(**config)

