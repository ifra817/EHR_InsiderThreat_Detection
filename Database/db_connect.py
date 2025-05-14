
import pymysql
import json
import os


def get_connection():
    print("[DEBUG] Entered get_connection")
    config_path = os.path.join(os.path.dirname(__file__), 'db_config.json')
    print(config_path)
    try:
        with open(config_path, 'r') as f:
            db_config = json.load(f)
        conn = pymysql.connect(
            host=db_config.get("host"),
            user=db_config.get("user"),
            password=db_config.get("password"),
            database=db_config.get("database"),
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

        print("[DEBUG] DB connection successful")
        return conn
    except Exception as err:
        print(f"[ERROR] Database connection error: {err}")
        return None
