# store_template.py
import os
import sys
import numpy as np
import mysql.connector
from datetime import datetime
from match_utils import preprocess_fingerprint, extract_minutiae
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)

from Database.db_connect import get_connection  # ✅ Use your existing database connector

IMG_WIDTH = 260
IMG_HEIGHT = 300

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FINGERPRINT_DIR = os.path.join(BASE_DIR, "fingerprints")

# ---------- Step 1: Load fingerprint file ----------
username = sys.argv[1]
path = os.path.join(FINGERPRINT_DIR, f"{username}.dat")

with open(path, 'rb') as f:
    raw = f.read()

if len(raw) != IMG_WIDTH * IMG_HEIGHT:
    raise ValueError("Invalid image size.")

img = np.frombuffer(raw, dtype=np.uint8).reshape((IMG_HEIGHT, IMG_WIDTH))

# You can add this later after testing core storage works
# skeleton = preprocess_fingerprint(img)
# minutiae = extract_minutiae(skeleton)
# data_json = json.dumps(minutiae)

# ---------- Step 2: Save to Database ----------
try:
    conn = get_connection()
    cursor = conn.cursor()

    # Get user_id using email (username is email in your case)
    cursor.execute("SELECT user_id FROM Users WHERE email = %s", (username,))
    result = cursor.fetchone()

    if not result:
        raise Exception("❌ User not found in database")

    user_id = result[0]

    # Store the fingerprint
    cursor.execute("""
        INSERT INTO Fingerprints (user_id, fingerprint_data)
        VALUES (%s, %s)
    """, (user_id, img.tobytes()))

    conn.commit()
    print(f"✅ Fingerprint template stored for user ID: {user_id}")

except mysql.connector.Error as db_err:
    print(f"❌ Database Error: {db_err}")

except Exception as e:
    print(f"❌ Error: {e}")

finally:
    if conn.is_connected():
        cursor.close()
        conn.close()
