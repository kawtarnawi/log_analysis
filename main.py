from ingestion import read
from processing import extract_transfrom

if __name__ == "__main__":
    rows = read.ingest('./data')

    for row in rows:
        result = extract_transfrom.extract(row)

        if result:
            auth = extract_transfrom.extract_auth(result["message"])

            if auth:
                print(auth)
                break