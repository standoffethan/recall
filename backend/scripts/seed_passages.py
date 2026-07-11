import os
import time
import re
import json
import random
import requests
import psycopg2

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://appuser:apppass@localhost:5433/appdb"
)

DATASET = "sedthh/gutenberg_english"
CONFIG = "default"
SPLIT = "train"
BATCH_SIZE = 20        # rows fetched per HTTP request — small and light
MAX_BOOKS = 200         # start small; bump up later once this works

TARGET_LENGTHS = [100, 150, 200, 250, 300, 350, 400, 500, 600]
PASSAGES_PER_BOOK_PER_LENGTH = 1

API_URL = "https://datasets-server.huggingface.co/rows"


def clean_text(text):
    return re.sub(r"\s+", " ", text).strip()


def random_chunk(words, length):
    if len(words) < length:
        return None
    start = random.randint(0, len(words) - length)
    return " ".join(words[start:start + length])

def fetch_rows(offset, length, max_retries=5):
    params = {
        "dataset": DATASET,
        "config": CONFIG,
        "split": SPLIT,
        "offset": offset,
        "length": length,
    }
    for attempt in range(1, max_retries + 1):
        try:
            resp = requests.get(API_URL, params=params, timeout=30)
            resp.raise_for_status()
            return resp.json()["rows"]
        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response is not None else None
            if status in (502, 503, 504) and attempt < max_retries:
                wait = attempt * 2
                print(f"  Got {status}, retrying in {wait}s (attempt {attempt}/{max_retries})...")
                time.sleep(wait)
                continue
            raise

def main():
    print("Connecting to Postgres...")
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    processed = 0
    passages_inserted = 0
    offset = 0

    while processed < MAX_BOOKS:
        print(f"Fetching rows {offset} to {offset + BATCH_SIZE}...")
        rows = fetch_rows(offset, BATCH_SIZE)
        if not rows:
            print("No more rows available.")
            break

        for entry in rows:
            row = entry["row"]
            meta_raw = row.get("METADATA")
            text_raw = row.get("TEXT")
            if not meta_raw or not text_raw:
                continue

            try:
                meta = json.loads(meta_raw)
            except (json.JSONDecodeError, TypeError):
                continue

            title = meta.get("title")
            author = meta.get("authors")
            if not title or not author:
                continue

            words = clean_text(text_raw).split(" ")

            for length in TARGET_LENGTHS:
                for _ in range(PASSAGES_PER_BOOK_PER_LENGTH):
                    chunk = random_chunk(words, length)
                    if chunk:
                        cur.execute(
                            """INSERT INTO passages (title, author, text, length)
                               VALUES (%s, %s, %s, %s)""",
                            (title, author, chunk, length),
                        )
                        passages_inserted += 1

            processed += 1
            print(f"[{processed}/{MAX_BOOKS}] {title} — {author}")
            conn.commit()
            print(f"  Committed after: {title}")

            if processed >= MAX_BOOKS:
                break

        offset += BATCH_SIZE

    cur.close()
    conn.close()
    print(f"\nDone. Seeded {passages_inserted} passages from {processed} books.")


if __name__ == "__main__":
    main()