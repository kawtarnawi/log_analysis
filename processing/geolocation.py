
import requests as http
import ipaddress

from logger_config import app_logger
from storage import cache_db


# Remplacer par ton token personnel IPinfo
TOKEN = "b6b9f02d87e8d2"

LIMIT = "limit"

# Cache en mémoire
country_cache = {}


def initialize_cache():
    """Charger le cache PostgreSQL au démarrage."""
    global country_cache

    try:
        country_cache = cache_db.load_cache()

        app_logger.info(
            "Cache chargé depuis PostgreSQL : %d IP connues",
            len(country_cache)
        )

    except Exception as e:
        app_logger.error("Erreur initialisation du cache : %s", e)
        country_cache = {}


def geo_location(ip):
    """
    Rechercher le pays d'une IP :
    1. Cache mémoire
    2. PostgreSQL
    3. Vérification IP
    4. API IPinfo
    5. Sauvegarde PostgreSQL
    """

    # 1. Vérifier le cache mémoire
    if ip in country_cache:
        return country_cache[ip]

    # 2. Vérifier PostgreSQL
    country = cache_db.get_country(ip)

    if country is not None:
        country_cache[ip] = country
        return country

    # 3. Vérifier la validité de l'adresse IP
    try:
        address = ipaddress.ip_address(ip)

    except ValueError:
        app_logger.error("Adresse IP invalide : %s", ip)
        return "Unknown"

    # 4. Ignorer les IP privées et non publiques
    if not address.is_global:
        country_cache[ip] = "Private"
        cache_db.save_ip(ip, "Private")

        app_logger.info("IP privée ou non publique ignorée : %s", ip)
        return "Private"

    # 5. Appeler IPinfo pour les IP publiques
    try:
        response = http.get(
            "https://ipinfo.io/" + ip + "/json",
            params={"token": TOKEN},
            timeout=10
        )

        if response.status_code == 429:
            app_logger.warning("Limite API IPinfo atteinte pour %s", ip)
            return LIMIT

        if response.status_code != 200:
            app_logger.error(
                "Erreur IPinfo pour %s : HTTP %d",
                ip,
                response.status_code
            )
            return None

        data = response.json()

        country = data.get("country")

        if not country:
            app_logger.warning("Pays introuvable pour %s", ip)
            return "Unknown"

        # 6. Enregistrer dans le cache mémoire
        country_cache[ip] = country

        # 7. Enregistrer dans PostgreSQL
        saved = cache_db.save_ip(ip, country)

        if saved:
            app_logger.info(
                "IP géolocalisée et sauvegardée : %s -> %s",
                ip,
                country
            )

        return country

    except http.RequestException as e:
        app_logger.error("Erreur réseau pour %s : %s", ip, e)
        return None

    except ValueError as e:
        app_logger.error("Réponse JSON invalide pour %s : %s", ip, e)
        return None

    except Exception as e:
        app_logger.error("Erreur géolocalisation %s : %s", ip, e)
        return None


def locate_all(ips):
    """Géolocaliser les IP absentes du cache."""

    new_ips = [
        ip for ip in ips
        if ip not in country_cache
    ]

    app_logger.info(
        "%d IP au total, %d absentes du cache",
        len(ips),
        len(new_ips)
    )

    for i, ip in enumerate(new_ips):

        result = geo_location(ip)

        # Arrêter les appels si IPinfo répond 429
        if result == LIMIT:
            app_logger.warning(
                "Limite API atteinte : %d IP restent à géolocaliser",
                len(new_ips) - i
            )
            break
