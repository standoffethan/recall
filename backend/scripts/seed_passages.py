import os
import time
import re
import json
import random
import psycopg2
import unicodedata
from datasets import load_dataset

# Database URL from environment variable
DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://appuser:apppass@localhost:5433/appdb"
)

# Hugging Face dataset info
DATASET = "sedthh/gutenberg_english"
CONFIG = "default"
SPLIT = "train"

# Processing parameters
MAX_BOOKS = 200
TARGET_LENGTHS = [100, 150, 200, 250, 300, 350, 400, 500, 600]
PASSAGES_PER_BOOK_PER_LENGTH = 1


def clean_text(text):
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("\r\n", " ").replace("\r", " ").replace("\n", " ")
    text = re.sub(r"[\x00-\x1f\x7f]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def split_sentences(text):
    return re.split(r"(?<=[.!?])\s+", text)


def build_passage(sentences, target_length):
    if not sentences:
        return None

    start = random.randint(0, len(sentences) - 1)
    chosen = []
    word_count = 0

    for sentence in sentences[start:]:
        chosen.append(sentence)
        word_count += len(sentence.split())
        if word_count >= target_length:
            break

    if word_count < target_length * 0.5:
        return None

    return " ".join(chosen), word_count


def main():
    print("Loading dataset from Hugging Face...")
    dataset = load_dataset(DATASET, CONFIG, split="train[:5%]") #download 5% of the dataset for speed

    print("Connecting to Postgres...")
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    processed = 0
    passages_inserted = 0

    for entry in dataset:
        if processed >= MAX_BOOKS:
            break

        # HF dataset rows are direct dicts
        meta_raw = entry.get("METADATA")
        text_raw = entry.get("TEXT")

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

        cleaned = clean_text(text_raw)
        sentences = split_sentences(cleaned)

        for target_length in TARGET_LENGTHS:
            for _ in range(PASSAGES_PER_BOOK_PER_LENGTH):
                result = build_passage(sentences, target_length)
                if result:
                    passage_text, actual_length = result
                    cur.execute(
                        """INSERT INTO passages (title, author, text, length)
                           VALUES (%s, %s, %s, %s)""",
                        (title, author, passage_text, actual_length),
                    )
                    passages_inserted += 1

        processed += 1
        print(f"[{processed}/{MAX_BOOKS}] {title} — {author}")
        conn.commit()
        print(f"  Committed after: {title}")

    cur.close()
    conn.close()
    print(f"\nDone. Seeded {passages_inserted} passages from {processed} books.")


if __name__ == "__main__":
    main()
