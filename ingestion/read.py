
import gzip
import os
import os.path as pt
import logging

logger = logging.getLogger(__name__)


def ingest(path: str):
    rows = []

    try:
        files = sorted(os.listdir(path))

        for file in files:
            file_path = pt.join(path, file)

            try:
                if file.endswith('.gz'):
                    opener = gzip.open
                else:
                    opener = open

                with opener(file_path, mode='rt', encoding='utf-8',
                            errors='replace') as f:
                    rows.extend(f.readlines())

                logger.info("File successfully read: %s", file)

            except (OSError, EOFError) as e:
                logger.error("Error reading file %s: %s", file, e)

    except OSError as e:
        logger.exception("Error accessing directory %s: %s", path, e)

    return rows
