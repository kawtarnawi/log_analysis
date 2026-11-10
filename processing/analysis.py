import re
import logging

from ingestion import read
from processing import extract_transfrom
from processing import geolocation
from processing import dashboard

from logger_config import app_logger


def analyze(rows):
    successful_users = {}
    failed_ips = {}
    invalid_users = {}

    # Événements qui seront enregistrés dans PostgreSQL
    parsed_events = []

    for row in rows:
        result = extract_transfrom.extract(row)

        if result:
            auth = extract_transfrom.extract_auth(result["message"])

            if auth:
                status = auth["status"]
                user = auth["user"]
                ip = auth["ip"]

                repeated = re.search(
                    r"message repeated (\d+) times",
                    result["message"]
                )

                count = int(repeated.group(1)) if repeated else 1

                is_invalid = auth["invalid"] == "invalid user"

                # Ajouter chaque événement au futur enregistrement
                for _ in range(count):
                    parsed_events.append(
                        (status, user, ip, is_invalid)
                    )

                if status == "Accepted":
                    successful_users[user] = (
                        successful_users.get(user, 0) + count
                    )

                elif status == "Failed":
                    failed_ips[ip] = failed_ips.get(ip, 0) + count

                    if is_invalid:
                        invalid_users[user] = (
                            invalid_users.get(user, 0) + count
                        )

    # Géolocalisation des IP ayant échoué
    ips = sorted(
        failed_ips,
        key=lambda ip: failed_ips[ip],
        reverse=True
    )

    geolocation.locate_all(ips)

    # Construire les résultats finaux avec les pays
    parsed_logs = []

    for status, user, ip, is_invalid in parsed_events:

        country = geolocation.country_cache.get(ip, "Unknown")

        parsed_logs.append(
            (status, user, ip, country, is_invalid)
        )

    # Calcul des tentatives échouées par pays
    failed_countries = {}

    for ip, count in failed_ips.items():
        country = geolocation.country_cache.get(ip, "Unknown")

        failed_countries[country] = (
            failed_countries.get(country, 0) + count
        )

    app_logger.info(
        "%d tentatives échouées provenant de %d IP",
        sum(failed_ips.values()),
        len(failed_ips)
    )

    app_logger.info(
        "%d événements prêts pour PostgreSQL",
        len(parsed_logs)
    )

    return successful_users, failed_countries, invalid_users, parsed_logs


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s:%(name)s:%(message)s"
    )

    rows = read.ingest("./data")

    geolocation.initialize_cache()

    successful, failed, invalid, parsed_logs = analyze(rows)

    dashboard.show_dashboard(successful, failed, invalid)