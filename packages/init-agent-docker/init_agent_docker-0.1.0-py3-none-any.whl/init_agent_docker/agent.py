import os
import time
import datetime
import threading
import jwt
import subprocess
import logging

PUBLIC_KEY_PATH = "/secrets/public.pem"
LICENSE_PATH = "/secrets/license.jwt"


def verify_license():
    try:
        with open(PUBLIC_KEY_PATH, "rb") as f:
            public_key = f.read()
        with open(LICENSE_PATH, "r") as f:
            token = f.read().strip()

        payload = jwt.decode(token, public_key, algorithms=["RS256"])
        exp = datetime.datetime.fromtimestamp(payload["exp"])
        return True
    except Exception as e:
        logging.error(f"")
        return False


def restart_every_5_minutes():
    while True:
        time.sleep(5 * 60)
        os._exit(1)


def run():
    if not verify_license():
        exit(1)

    threading.Thread(target=restart_every_5_minutes, daemon=True).start()

    logging.info("🚀 Starting service...")
    subprocess.run([
        "uvicorn", "service.main:app",
        "--host", "0.0.0.0", "--port", "8001"
    ])
