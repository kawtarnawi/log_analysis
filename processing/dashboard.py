import matplotlib.pyplot as plt


def show_dashboard(successful_users, failed_countries, invalid_users):

    # 1. Tentatives échouées par pays
    countries = list(failed_countries.keys())
    failures = list(failed_countries.values())

    plt.figure(figsize=(12, 7))
    plt.barh(countries, failures)
    plt.title("Failed attempts by country")
    plt.xlabel("Number of failed attempts")
    plt.ylabel("Country")
    plt.tight_layout()
    plt.show()

    # 2. Connexions réussies par utilisateur
    users = list(successful_users.keys())
    attempts = list(successful_users.values())

    plt.figure(figsize=(8, 5))
    plt.bar(users, attempts)
    plt.title("Successful attempts by user")
    plt.xlabel("User")
    plt.ylabel("Number of successful attempts")
    plt.tight_layout()
    plt.show()

    # 3. Tentatives avec utilisateur invalide
    plt.figure(figsize=(6, 5))
    plt.bar(["Invalid users"], [invalid_users])
    plt.title("Failed attempts with invalid user")
    plt.ylabel("Number of attempts")
import matplotlib.pyplot as plt


def show_dashboard(successful_users, failed_countries, invalid_users):

    # 1. Failed attempts by country

    countries = {
        country: count
        for country, count in failed_countries.items()
        if country != "Unknown"
    }

    countries = dict(
        sorted(countries.items(), key=lambda item: item[1])
    )

    plt.figure(figsize=(12, 8))
    plt.barh(list(countries.keys()), list(countries.values()))

    plt.title("Failed attempts by country")
    plt.xlabel("Number of failed attempts")
    plt.ylabel("Country")
    plt.tight_layout()
    plt.show()

    print("Attempts with unknown country:",
          failed_countries.get("Unknown", 0))

    # 2. Successful attempts by user

    users = list(successful_users.keys())
    attempts = list(successful_users.values())

    plt.figure(figsize=(8, 5))
    plt.bar(users, attempts)

    plt.title("Successful attempts by user")
    plt.xlabel("User")
    plt.ylabel("Number of successful attempts")
    plt.tight_layout()
    plt.show()

    # 3. Failed attempts with invalid user

    plt.figure(figsize=(7, 5))
    plt.bar(["Invalid users"], [invalid_users])

    plt.title("Failed attempts with invalid user")
    plt.ylabel("Number of attempts")
    plt.tight_layout()
    plt.show()

    plt.tight_layout()
    plt.show()