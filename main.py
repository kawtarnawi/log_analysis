import logging

from ingestion import read
from processing import analysis
from processing import dashboard
from processing import geolocation

from storage import save_db
from storage import cache_db

from logger_config import app_logger


if __name__ == "__main__":

    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s:%(name)s:%(message)s"
    )

    try:
        print("Reading log files...")

        # 1. Initialisation des tables PostgreSQL
        save_db.create_logs_table()
        cache_db.create_cache_table()

        # 2. Chargement du cache depuis PostgreSQL
        geolocation.initialize_cache()

        # 3. Ingestion des fichiers
        rows = read.ingest("./data")

        print("Analyzing", len(rows), "lines...")

        # 4. Analyse et géolocalisation
        successful, failed, invalid, parsed_logs = analysis.analyze(rows)

        # 5. Sauvegarde des résultats finaux
        save_db.save_logs(parsed_logs)

        # 6. Affichage des statistiques
        print("\nSuccessful attempts by user:")
        print(successful)

        print("\nFailed attempts by country:")
        print(failed)

        print("\nFailed attempts with invalid user:")
        print(
            sum(invalid.values()),
            "attempts,",
            len(invalid),
            "different usernames"
        )

        # 7. Dashboard
        print("\nGenerating dashboard...")

        dashboard.show_dashboard(successful, failed, invalid)

        app_logger.info("Pipeline terminé avec succès")

    except Exception as e:
        app_logger.error("Erreur pendant l'exécution du pipeline : %s", e)