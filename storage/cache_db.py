import psycopg2
from logger_config import app_logger
from storage.save_db import get_connection


def create_cache_table():
    """Créer la table du cache des IP."""
    connection = get_connection()

    if connection is None:
        return False

    try:
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ip_cache (
                ip VARCHAR(45) PRIMARY KEY,
                country VARCHAR(10) NOT NULL
            )
        """)

        connection.commit()
        cursor.close()

        app_logger.info("Table ip_cache créée ou déjà existante")
        return True

    except psycopg2.Error as e:
        connection.rollback()
        app_logger.error("Erreur création ip_cache : %s", e)
        return False

    finally:
        connection.close()


def load_cache():
    """Charger toutes les IP enregistrées dans un dictionnaire."""
    cache = {}

    connection = get_connection()

    if connection is None:
        return cache

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT ip, country
            FROM ip_cache
        """)

        rows = cursor.fetchall()

        for ip, country in rows:
            cache[ip] = country

        cursor.close()

        app_logger.info(
            "Cache chargé depuis PostgreSQL : %d IP connues",
            len(cache)
        )

    except psycopg2.Error as e:
        app_logger.error("Erreur chargement du cache : %s", e)

    finally:
        connection.close()

    return cache


def get_country(ip):
    """Rechercher le pays d'une IP directement dans PostgreSQL."""
    connection = get_connection()

    if connection is None:
        return None

    try:
        cursor = connection.cursor()

        cursor.execute(
            "SELECT country FROM ip_cache WHERE ip = %s",
            (ip,)
        )

        result = cursor.fetchone()
        cursor.close()

        if result:
            return result[0]

        return None

    except psycopg2.Error as e:
        app_logger.error("Erreur recherche IP %s : %s", ip, e)
        return None

    finally:
        connection.close()


def save_ip(ip, country):
    """Insérer une nouvelle IP sans remplacer une IP existante."""
    connection = get_connection()

    if connection is None:
        return False

    try:
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO ip_cache (ip, country)
            VALUES (%s, %s)
            ON CONFLICT (ip) DO NOTHING
        """, (ip, country))

        connection.commit()
        cursor.close()

        app_logger.info("IP enregistrée dans le cache : %s -> %s", ip, country)
        return True

    except psycopg2.Error as e:
        connection.rollback()
        app_logger.error("Erreur sauvegarde IP %s : %s", ip, e)
        return False

    finally:
        connection.close()