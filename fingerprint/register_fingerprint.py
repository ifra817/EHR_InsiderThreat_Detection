import os
import sys
import subprocess
import pymysql

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)

from Database.db_connect import get_connection

IMG_WIDTH = 260
IMG_HEIGHT = 300

# === [Step 1: Get user input] ===
email = input("\nEnter email: ").strip()
password = input("Enter password: ").strip()

# === [Step 2: Setup Paths] ===
EXE_PATH = os.path.abspath("C:/Users/Dell/Documents/My Projects/EHR_InsiderThreat_Detection/fingerprint/capture/CaptureFingerprint/x64/Debug/CaptureFingerprint.exe")
STORE_SCRIPT = os.path.abspath("C:/Users/Dell/Documents/My Projects/EHR_InsiderThreat_Detection/fingerprint/store_template.py")
FP_DIR = os.path.abspath("C:/Users/Dell/Documents/My Projects/EHR_InsiderThreat_Detection/fingerprint/fingerprints")
fp_path = os.path.join(FP_DIR, f"{email}.dat")

# === [Step 3: Connect to DB] ===
conn = get_connection()
if not conn:
    print("❌ Failed to connect to database.")
    sys.exit()

try:
    cursor = conn.cursor()

    # Check if user exists
    cursor.execute("SELECT user_id FROM Users WHERE email = %s AND password = %s", (email, password))
    result = cursor.fetchone()

    if result:
        user_id = result['user_id']
        print(f"✅ Existing user found with ID: {user_id}")

        # Check if fingerprint already exists
        cursor.execute("SELECT fingerprint_id FROM Fingerprints WHERE user_id = %s", (user_id,))
        fp_result = cursor.fetchone()

        if fp_result:
            print("✅ Fingerprint already registered.")
        else:
            print("🧾 Fingerprint not found. Capturing...")

            subprocess.run([EXE_PATH, email], check=True)
            if not os.path.exists(fp_path):
                raise FileNotFoundError(f"Expected fingerprint file not found: {fp_path}")

            subprocess.run([sys.executable, STORE_SCRIPT, email], check=True)

            with open(fp_path, 'rb') as f:
                fingerprint_data = f.read()

            if len(fingerprint_data) != IMG_WIDTH * IMG_HEIGHT:
                raise ValueError("Invalid fingerprint size.")

            cursor.execute(
                "INSERT INTO Fingerprints (user_id, fingerprint_data) VALUES (%s, %s)",
                (user_id, fingerprint_data)
            )
            conn.commit()
            print("✅ Fingerprint registered successfully.")

    else:
        print("👤 New user. Registering...")

        cursor.execute("INSERT INTO Users (email, password) VALUES (%s, %s)", (email, password))
        user_id = cursor.lastrowid
        conn.commit()

        subprocess.run([EXE_PATH, email], check=True)
        if not os.path.exists(fp_path):
            raise FileNotFoundError(f"Expected fingerprint file not found: {fp_path}")

        subprocess.run([sys.executable, STORE_SCRIPT, email], check=True)

        with open(fp_path, 'rb') as f:
            fingerprint_data = f.read()

        if len(fingerprint_data) != IMG_WIDTH * IMG_HEIGHT:
            raise ValueError("Invalid fingerprint size.")

        cursor.execute(
            "INSERT INTO Fingerprints (user_id, fingerprint_data) VALUES (%s, %s)",
            (user_id, fingerprint_data)
        )
        conn.commit()
        print("✅ New user and fingerprint registered successfully.")

except pymysql.MySQLError as db_err:
    print(f"❌ Database Error: {db_err}")
    conn.rollback()
except Exception as e:
    print(f"❌ Error: {e}")
    conn.rollback()
finally:
    if conn:
        cursor.close()
        conn.close()
