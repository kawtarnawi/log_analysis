
import requests as http
import json
import os
import logging

logger = logging.getLogger(__name__)

# the cache is next to main.py, whatever folder the program is started from
CACHE_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "country_cache.json")

# returned when ipinfo answers 429 (too many requests)
LIMIT = "limit"


def load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError):
            logger.error("country_cache.json is unreadable, starting with an empty cache")
            return {}

    return {}


def save_cache():
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(country_cache, f)
    except OSError as e:
        logger.error("Cannot save the cache: %s", e)


country_cache = load_cache()


def geo_location(ip):
    # returns the country code, "Unknown" if ipinfo has no country,
    # None if ipinfo did not answer (the ip will be retried next time) or LIMIT on a 429

    if ip in country_cache:
        return country_cache[ip]

    try:
        response = http.get("https://ipinfo.io/" + ip + "/json", timeout=5)
    except http.RequestException as e:
        logger.error("ipinfo %s : %s", ip, e)
        return None

    if response.status_code == 429:
        return LIMIT
    if response.status_code != 200:
        logger.error("ipinfo %s : http %d", ip, response.status_code)
        return None

    data = response.json()
    # private addresses (10.x, 127.x ...) are "bogon" and have no country
    if data.get("bogon"):
        country = "Private"
    else:
        country = data.get("country", "Unknown")

    country_cache[ip] = country
    return country


def locate_all(ips):
    # ips are sorted from the biggest attacker to the smallest,
    # so if ipinfo blocks us the important ones are already located
    new_ips = [ip for ip in ips if ip not in country_cache]
    logger.info("%d ips, %d not in the cache", len(ips), len(new_ips))

    for i, ip in enumerate(new_ips):
        if geo_location(ip) == LIMIT:
            logger.warning("ipinfo limit reached (429), %d ips stay Unknown, run again later",
                           len(new_ips) - i)
            break

    save_cache()
