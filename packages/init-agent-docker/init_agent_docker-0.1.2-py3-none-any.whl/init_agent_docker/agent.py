import os
import time
import datetime
import threading
import jwt
import subprocess
import logging
import schedule

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

def daily_restart():
    while True:
        now = datetime.datetime.now()
        tomorrow = (now + datetime.timedelta(days=1)).replace(
            hour=1, minute=0, second=0, microsecond=0
        )
        sleep_seconds = (tomorrow - now).total_seconds()
        time.sleep(sleep_seconds)
        os._exit(1)

def restart_container():
    os._exit(1)

def daily_restart_scheduler():
    schedule.every().day.at("01:25").do(restart_container)
    while True:
        schedule.run_pending()
        time.sleep(1)

def run():
    if not verify_license():
        exit(1)

    # threading.Thread(target=restart_every_5_minutes, daemon=True).start()
    # threading.Thread(target=daily_restart, daemon=True).start()
    threading.Thread(target=daily_restart_scheduler, daemon=True).start()

    logging.info("🚀 Starting service...")
    subprocess.run([
        "uvicorn", "service.main:app",
        "--host", "0.0.0.0", "--port", "8001"
    ])
