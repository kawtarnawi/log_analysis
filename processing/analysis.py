
from ingestion import read
from processing import extract_transfrom
from processing import geolocation
from processing import dashboard


def analyze(rows):
    successful_users = {}
    failed_countries = {}
    invalid_users = 0

    for row in rows:
        result = extract_transfrom.extract(row)

        if result:
            auth = extract_transfrom.extract_auth(result["message"])

            if auth:
                status = auth["status"]
                user = auth["user"]
                ip = auth["ip"]

                if status == "Accepted":
                    successful_users[user] = successful_users.get(user, 0) + 1

                elif status == "Failed":

                    # Utiliser uniquement les pays déjà enregistrés
                    country = geolocation.country_cache.get(ip, "Unknown")

                    failed_countries[country] = failed_countries.get(country, 0) + 1

                    if auth["invalid"] == "invalid user":
                        invalid_users += 1

    return successful_users, failed_countries, invalid_users


if __name__ == "__main__":
    print("Reading log files...")

    rows = read.ingest("./data")

    print("Analyzing", len(rows), "lines...")

    successful, failed, invalid = analyze(rows)

    print("\nSuccessful attempts by user:")
    print(successful)

    print("\nFailed attempts by country:")
    print(failed)

    print("\nFailed attempts with invalid user:")
    print(invalid)

    print("\nGenerating dashboard...")

    dashboard.show_dashboard(successful, failed, invalid)
