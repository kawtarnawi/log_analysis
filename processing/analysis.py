
import re
import logging

from ingestion import read
from processing import extract_transfrom
from processing import geolocation
from processing import dashboard

logger = logging.getLogger(__name__)


def analyze(rows):
    successful_users = {}
    failed_ips = {}
    invalid_users = {}

    for row in rows:
        result = extract_transfrom.extract(row)

        if result:
            auth = extract_transfrom.extract_auth(result["message"])

            if auth:
                status = auth["status"]
                user = auth["user"]
                ip = auth["ip"]

                # "message repeated 4 times: [ Failed password ...]" = 4 attempts, not 1
                repeated = re.search(r"message repeated (\d+) times", result["message"])
                count = int(repeated.group(1)) if repeated else 1

                if status == "Accepted":
                    successful_users[user] = successful_users.get(user, 0) + count

                elif status == "Failed":
                    failed_ips[ip] = failed_ips.get(ip, 0) + count

                    if auth["invalid"] == "invalid user":
                        invalid_users[user] = invalid_users.get(user, 0) + count

    # country of every attacking ip (ipinfo is only called for the ips not in the cache)
    ips = sorted(failed_ips, key=lambda ip: failed_ips[ip], reverse=True)
    geolocation.locate_all(ips)

    failed_countries = {}
    for ip, count in failed_ips.items():
        country = geolocation.country_cache.get(ip, "Unknown")
        failed_countries[country] = failed_countries.get(country, 0) + count

    logger.info("%d failed attempts from %d ips", sum(failed_ips.values()), len(failed_ips))

    return successful_users, failed_countries, invalid_users


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")

    rows = read.ingest("./data")
    successful, failed, invalid = analyze(rows)
    dashboard.show_dashboard(successful, failed, invalid)
