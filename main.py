
import logging

from ingestion import read
from processing import analysis
from processing import dashboard


if __name__ == "__main__":

    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s:%(name)s:%(message)s"
    )

    print("Reading log files...")

    rows = read.ingest("./data")

    print("Analyzing", len(rows), "lines...")

    successful, failed, invalid = analysis.analyze(rows)

    print("\nSuccessful attempts by user:")
    print(successful)

    print("\nFailed attempts by country:")
    print(failed)

    print("\nFailed attempts with invalid user:")
    print(invalid)

    print("\nGenerating dashboard...")

    dashboard.show_dashboard(successful, failed, invalid)
