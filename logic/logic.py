
# logic/logic.py

import requests
import time
import socket
import logging
from requests.adapters import HTTPAdapter, Retry
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_session() -> requests.Session:
    session = requests.Session()
    retries = Retry(
        total=3,
        backoff_factor=0.3,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods={"HEAD", "GET", "OPTIONS", "POST"}
    )
    adapter = HTTPAdapter(max_retries=retries, pool_connections=10, pool_maxsize=10)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    session.headers['Expect'] = ''
    session.headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1)'
    return session


def warm_up_connection(session: requests.Session, base_url: str, timeout: float = 2.0):
    try:
        response = session.head(base_url, timeout=timeout)
        response.raise_for_status()
        logger.info("Warm-up connection succeeded (HEAD)")
    except requests.RequestException:
        try:
            response = session.get(base_url, timeout=timeout)
            response.raise_for_status()
            logger.info("Warm-up connection succeeded (GET)")
        except Exception as e:
            logger.warning(f"Warm-up connection failed: {e}")


def login_optimized(session: requests.Session, username: str, password: str, url: str, timeout: float = 5.0):
    payload = {"email": username, "password": password}
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/plain, */*',
        'Connection': 'keep-alive',
        'Accept-Encoding': 'gzip, deflate'
    }

    start_time = time.perf_counter()
    response = session.post(url, json=payload, headers=headers, timeout=timeout)
    response.raise_for_status()
    elapsed = time.perf_counter() - start_time

    data = response.json()
    if not data.get("status", False):
        raise ValueError(f"Login failed: {data.get('message', 'Unknown error')}")

    return data, elapsed, response.text


def logic_main(url: str, username: str, password: str):
    try:
        socket.gethostbyname("demoerp.nexgeno.cloud")
    except socket.gaierror as e:
        logger.error(f"DNS resolution failed: {e}")
        return None

    session = create_session()
    logger.info("⏱️ Warming up connection...")
    warm_up_connection(session, "https://demoerp.nexgeno.cloud/")

    try:
        data, duration, _ = login_optimized(session, username, password, url)
        logger.info(f"✅ Login succeeded in {duration:.4f} seconds.")

        # Extracting values from response
        firstname = data.get("firstname", "")
        lastname = data.get("lastname", "")
        full_name = f"{firstname} {lastname}".strip()
        thumb_url = data.get("profile_thumb")
        job_position = data.get("job_position")

        checkin_time_str = data.get("checkin", {}).get("datetime")
        checkin_time_fmt = None

        if checkin_time_str:
            try:
                dt_obj = datetime.strptime(checkin_time_str, "%Y-%m-%d %H:%M:%S")
                checkin_time_fmt = dt_obj.strftime("%I:%M %p")
            except ValueError:
                logger.warning("Invalid check-in time format")

        return {
            "full_name": full_name,
            "profile_thumb": thumb_url,
            "job_position": job_position,
            "checkin_time": checkin_time_fmt,
            "duration": duration
        }

    except Exception as e:
        logger.error(f"❌ Login attempt failed: {e}")
        return None


def clock_in(session: requests.Session, username: str, password: str, url: str, timeout: float = 5.0):
    """
    Send a clock-in request to the server using stored username and password.
    """
    payload = {"email": username, "password": password}  # or whatever payload your clock-in API expects

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/plain, */*',
        'Connection': 'keep-alive',
        'Accept-Encoding': 'gzip, deflate'
    }

    start_time = time.perf_counter()
    response = session.post(url, json=payload, headers=headers, timeout=timeout)
    response.raise_for_status()
    elapsed = time.perf_counter() - start_time

    data = response.json()
    if not data.get("status", False):
        raise ValueError(f"Clock-in failed: {data.get('message', 'Unknown error')}")

    return data, elapsed, response.text





#without our code 
# 🧠 DNS Lookup	~20–50ms	Translate dologic_main → IP
# 🤝 TCP Handshake	~20–50ms	3-way handshake
# 🔐 TLS Handshake	~50–100ms	SSL cert exchange + encryption setup
# 📤 Request + Network Delay	~10–50ms	Send payload over internet
# 💻 Server Processing	~50–150ms	Server authenticates, generates response
# 📥 Response Reception	~10–30ms	Receive + parse response


# Withour code 
# Skip DNS / TCP / TLS (reused)	~0ms
# Send POST + Receive response	~300–490ms 



# Post-Man 
#600 ms
#612 ms 
#695 ms


# My Code 
#337 ms
#341 ms
#454 ms



# curl -s --connect-timeout 5 \
#   -w "\
# time_namelookup:     %{time_namelookup}s\n\
# time_connect:        %{time_connect}s\n\
# time_appconnect:     %{time_appconnect}s\n\
# time_pretransfer:    %{time_pretransfer}s\n\
# time_starttransfer:  %{time_starttransfer}s\n\
# time_total:          %{time_total}s\n" \
#   -o /dev/null \
#   https://demoerp.nexgeno.cloud/admin/timesheets_api/authenticate