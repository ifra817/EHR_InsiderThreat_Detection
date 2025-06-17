import os
import subprocess
import numpy as np


from fingerprint.match_utils import preprocess_fingerprint, extract_minutiae, compare_minutiae
from Database.db_connect import get_connection

IMG_WIDTH = 260
IMG_HEIGHT = 300

# === [PATH CONFIGURATION] ===
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FINGERPRINT_DIR = os.path.join(BASE_DIR, "fingerprint", "fingerprints")

import subprocess
import os

IMG_WIDTH = 260
IMG_HEIGHT = 300

def capture_fingerprint_live(username: str) -> str:
    """
    Captures fingerprint via scanner and returns the path to the saved .dat file.
    """
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # goes up from /fingerprint
    FINGERPRINT_DIR = os.path.join(BASE_DIR, "fingerprint")
    FINGERPRINTS_DIR = os.path.join(FINGERPRINT_DIR, "fingerprints")
    EXE_PATH = os.path.join(FINGERPRINT_DIR, "capture", "CaptureFingerprint", "x64", "Debug", "CaptureFingerprint.exe")
    print("[DEBUG] EXE path:", EXE_PATH)
    print("[DEBUG] EXE path:", EXE_PATH)

    fp_path = os.path.join(FINGERPRINTS_DIR, f"{username}.dat")
    if os.path.exists(fp_path):
        os.remove(fp_path)
    print("🔒 Activating fingerprint scanner...")
    try:
        print("[DEBUG] Does EXE exist?", os.path.exists(EXE_PATH))
        print("[DEBUG] Is EXE a file?", os.path.isfile(EXE_PATH))
        print("[DEBUG] Current working directory:", os.getcwd())
        subprocess.run([EXE_PATH, username], shell=True, check=True)

        if not os.path.exists(fp_path):
            raise FileNotFoundError(f"❌ Fingerprint file not found: {fp_path}")
        
        print("✅ Fingerprint captured successfully.")
        return fp_path

    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"❌ Failed to capture fingerprint. Error: {e}")


def match_fingerprint(username: str) -> bool:
    conn = None
    cursor = None
    try:
        live_path = capture_fingerprint_live(username)
        print(f"[DEBUG] Using fingerprint file: {live_path}")

        with open(live_path, 'rb') as f:
            raw = f.read()

        if len(raw) != IMG_WIDTH * IMG_HEIGHT:
            print("ERROR: Invalid fingerprint size.")
            return False

        img = np.frombuffer(raw, dtype=np.uint8).reshape((IMG_HEIGHT, IMG_WIDTH))
        skeleton = preprocess_fingerprint(img)
        live_minutiae = extract_minutiae(skeleton)

        if len(live_minutiae) < 10:
            print("ERROR: Poor fingerprint quality.")
            return False

        conn = get_connection()
        cursor = conn.cursor()


        cursor.execute("""
            SELECT f.fingerprint_data
            FROM Fingerprints f
            JOIN Users u ON f.user_id = u.user_id
            WHERE u.email = %s
        """, (username,))
        result = cursor.fetchone()

        if not result:
            print("ERROR: No stored fingerprint.")
            return False

        stored_img = np.frombuffer(result['fingerprint_data'], dtype=np.uint8).reshape((IMG_HEIGHT, IMG_WIDTH))
        stored_skeleton = preprocess_fingerprint(stored_img)
        stored_minutiae = extract_minutiae(stored_skeleton)

        matches, _, _ = compare_minutiae(live_minutiae, stored_minutiae)
        ratio = matches / max(len(stored_minutiae), 1)
        print(f"[DEBUG] Match ratio: {ratio:.3f}")

        return ratio > 0.5

    except Exception as e:
        print("UNEXPECTED ERROR:", str(e))
        return False

    finally:
        if cursor: cursor.close()
        if conn: conn.close()
