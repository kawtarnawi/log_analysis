import psycopg2
from logger_config import app_logger


# Configuration PostgreSQL
DB_CONFIG = {
    "host": "localhost",
    "database": "log_analysis",
    "user": "postgres",
    "password": "1234567",
    "port": 5432
}


def get_connection():
    """Créer une connexion à PostgreSQL."""
    try:
        connection = psycopg2.connect(**DB_CONFIG)
        return connection

    except psycopg2.Error as e:
        app_logger.error("Erreur de connexion PostgreSQL : %s", e)
        return None


def create_logs_table():
    """Créer la table des résultats analysés."""
    connection = get_connection()

    if connection is None:
        return False

    try:
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS logs_parsed (
                id SERIAL PRIMARY KEY,
                status VARCHAR(20),
                username VARCHAR(100),
                ip VARCHAR(45),
                country VARCHAR(10),
                is_invalid_user BOOLEAN
            )
        """)

        connection.commit()
        cursor.close()

        app_logger.info("Table logs_parsed créée ou déjà existante")
        return True

    except psycopg2.Error as e:
        connection.rollback()
        app_logger.error("Erreur création logs_parsed : %s", e)
        return False

    finally:
        connection.close()


def save_logs(parsed_logs):
    """Enregistrer les événements analysés avec executemany."""
    if not parsed_logs:
        app_logger.info("Aucun événement à sauvegarder")
        return

    connection = get_connection()

    if connection is None:
        return

    try:
        cursor = connection.cursor()

        query = """
            INSERT INTO logs_parsed
            (status, username, ip, country, is_invalid_user)
            VALUES (%s, %s, %s, %s, %s)
        """

        cursor.executemany(query, parsed_logs)

        connection.commit()

        app_logger.info(
            "%d événements enregistrés dans PostgreSQL",
            cursor.rowcount
        )

        cursor.close()

    except psycopg2.Error as e:
        connection.rollback()
        app_logger.error("Erreur sauvegarde des logs : %s", e)

    finally:
        connection.close()