
import mysql.connector
import json
import os


def get_connection():
    config_path = os.path.join(os.path.dirname(__file__), 'db_config.json')
    try:
        with open(config_path, 'r') as f:
            db_config = json.load(f)
        conn = mysql.connector.connect(**db_config)
        return conn
    except Exception as err:
        print(f"[ERROR] Database connection error: {err}")
        return None
