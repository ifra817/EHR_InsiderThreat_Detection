
import mysql.connector
import json
import os


config_path = os.path.join(os.path.dirname(__file__), 'db_config.json')

with open(config_path, 'r') as f:
    db_config = json.load(f)
    
def get_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        return None