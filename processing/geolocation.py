
import requests as http
import json
import os

CACHE_FILE = "country_cache.json"


def load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r") as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError):
            return {}

    return {}


def save_cache():
    with open(CACHE_FILE, "w") as f:
        json.dump(country_cache, f)


country_cache = load_cache()


def geo_location(ip):

    if ip in country_cache:
        return country_cache[ip]

    try:
        response = http.get(
            "https://ipinfo.io/" + ip + "/json",
            timeout=2
        )

        if response.status_code == 200:
            country = response.json().get("country")
            country_cache[ip] = country if country else "Unknown"
        else:
            country_cache[ip] = "Unknown"

    except http.RequestException:
        country_cache[ip] = "Unknown"

    save_cache()

    return country_cache[ip]
