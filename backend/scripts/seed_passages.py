import os
import re
import json
import random
import psycopg2
from datasets import load_dataset

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://appuser:apppass@localhost:5433/appdb"
)

TARGET_LENGTHS = [100, 150, 200, 250, 300, 500, ]   # word counts you want to support
PASSAGES_PER_BOOK_PER_LENGTH = 2
MAX_BOOKS = 200                                # bump this up later for more variety
SHUFFLE_BUFFER_SIZE = 100
SHUFFLE_SEED = 42


def clean_text(text):
    """Collapse whitespace/newlines into single spaces."""
    return re.sub(r"\s+", " ", text).strip()


def random_chunk(words, length):
    """Pick a random contiguous slice of `length` words from a word list."""
    if len(words) < length:
        return None
    start = random.randint(0, len(words) - length)
    return " ".join(words[start:start + length])


def main():
    print("Connecting to Postgres...")
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    print("Loading dataset (streaming)...")
    ds = load_dataset("sedthh/gutenberg_english", split="train", streaming=True)
    ds = ds.shuffle(seed=SHUFFLE_SEED, buffer_size=SHUFFLE_BUFFER_SIZE)

    processed = 0
    passages_inserted = 0

    for row in ds:
        meta_raw = row.get("METADATA")
        text_raw = row.get("TEXT")
        if not meta_raw or not text_raw:
            continue

        try:
            meta = json.loads(meta_raw)
        except (json.JSONDecodeError, TypeError):
            continue

        title = meta.get("title")
        author = meta.get("author")
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

        if processed % 10 == 0:
            conn.commit()

        if processed >= MAX_BOOKS:
            break

    conn.commit()
    cur.close()
    conn.close()

    print(f"\nDone. Seeded {passages_inserted} passages from {processed} books.")


if __name__ == "__main__":
    main()