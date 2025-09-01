import hashlib
import logging
import os

import requests
import yaml
from dotenv import load_dotenv

from pixBoards.arguments import args


def load_config(yml_path="config.yml"):
    with open(yml_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


config = load_config()
tableName = config["tableName"]

logger = logging.getLogger(__name__)

# Load the .env file
load_dotenv()

IMG_CHEST_API_KEY = os.getenv("IMG_CHEST_API_KEY")
HEADERS = {"Authorization": f"Bearer {IMG_CHEST_API_KEY}"}


# def connect_db():
#     return psycopg2.connect(
#         dbname="boards",
#         user="postgres",
#         password="password",
#         host="localhost"
#     )


def create_table_if_not_exists(cursor):
    cursor.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {tableName} (
            hash TEXT PRIMARY KEY,
            link TEXT NOT NULL,
            filename TEXT  
        )
    """
    )


def compute_hash(filepath, chunk_size=8192):
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def load_link_by_hash(cursor, hash_val):
    cursor.execute(f"SELECT link FROM {tableName} WHERE hash = %s", (hash_val,))
    row = cursor.fetchone()
    return row[0] if row else None


def save_link(cursor, hash_val, link):
    cursor.execute(
        f"""
        INSERT INTO {tableName} (hash, link)
        VALUES (%s, %s)
        ON CONFLICT (hash) DO NOTHING
    """,
        (hash_val, link),
    )


# Based loosely on keikazuki's approach
def upload_image(image_path):
    with open(image_path, "rb") as f:
        files = {"images[]": (os.path.basename(image_path), f, "image/jpeg")}
        data = {"title": os.path.basename(image_path)}
        resp = requests.post(
            "https://api.imgchest.com/v1/post",
            headers=HEADERS,
            files=files,
            data=data,
        )

    resp.raise_for_status()
    post_id = resp.json()["data"]["id"]

    # Now get the image info
    info = requests.get(f"https://api.imgchest.com/v1/post/{post_id}", headers=HEADERS)
    info.raise_for_status()

    image_list = info.json()["data"]["images"]
    if not image_list:
        raise Exception("No images returned in response")

    return image_list[0]["link"]


import os
import re
from pathlib import Path


def get_link_from_sidecar(sidecar_file):
    # Ensure image_path is a Path object
    # image_path = Path(image_path)
    try:
        with sidecar_file.open("r", encoding="utf-8") as f:
            first_line = f.readline().strip()
            if first_line:
                match = re.match(r"url:\s*(\S+)", first_line, re.IGNORECASE)
                if match:
                    return match.group(1)
                return first_line
    except Exception as e:
        logger.warning(f"Failed to read sidecar file {sidecar_file}: {e}")


def append_sidecar_links(image_paths, conn, missing_log="missing_sidecar_links.log"):
    """
    - Collects links from all .txt files in the same directory as image_paths
    - Appends them to image_paths (deduped)
    - Checks DB for their presence
    - Prints missing ones
    """
    import glob

    if not image_paths:
        return image_paths

    # Directory of current set
    base_dir = os.path.dirname(image_paths[0])

    # Gather all .txt files
    txt_files = glob.glob(os.path.join(base_dir, "*.txt"))

    sidecar_links = []
    for txt in txt_files:
        try:
            with open(txt, "r", encoding="utf-8") as f:
                for line in f:
                    link = line.strip()
                    if link and link.startswith("http"):
                        sidecar_links.append(link)
        except Exception as e:
            logger.warning(f"Could not read {txt}: {e}")

    # Deduplicate
    sidecar_links = list(set(sidecar_links))

    if not sidecar_links:
        return image_paths

    logger.info(f"Found {len(sidecar_links)} sidecar links in {base_dir}")

    # Check against DB
    cur = conn.cursor()
    cur.execute(
        f"SELECT link FROM {tableName} WHERE link = ANY(%s)",
        (sidecar_links,),
    )
    existing_links = {row[0] for row in cur.fetchall()}
    cur.close()

    missing_links = [l for l in sidecar_links if l not in existing_links]

    if missing_links:
        with open(missing_log, "a", encoding="utf-8") as f:
            for l in missing_links:
                f.write(l + "\n")
        logger.warning(f"Appended {len(missing_links)} missing links to {missing_log}")

    # Merge into image_paths
    combined_paths = image_paths + sidecar_links
    return combined_paths


def process_images(image_paths, conn):
    import os

    link_hash_map = {}

    try:
        cur = conn.cursor()
        create_table_if_not_exists(cur)

        results = []
        for image_path in image_paths:
            filename = os.path.basename(image_path)
            sidecar_link = None

            if args.sidecar:
                # sidecar_link = get_link_from_sidecar(image_path)
                sidecar_file = Path(image_path).with_suffix(Path(image_path).suffix + ".txt")
                if sidecar_file.exists():
                    sidecar_link = get_link_from_sidecar(sidecar_file)
                # print(sidecar_link)

            if sidecar_link:
                logger.debug(
                    f"🔗 Using link from sidecar file: {image_path} → {sidecar_link}"
                )
                results.append(sidecar_link)
                cached_link = sidecar_link

                try:
                    # with conn.cursor() as cur:
                    cur.execute(
                            f"SELECT hash FROM {tableName} WHERE link = %s",
                            (sidecar_link,),
                            )
                    hash_val = cur.fetchone()
                    logger.info("hash used from table")
                    
                except:
                    hash_val = compute_hash(image_path)
                    logger.info("hash computed")

                link_hash_map[hash_val] = sidecar_link

                try:
                    cur.execute(
                        f"""INSERT INTO {tableName} (hash, link, filename)
                            VALUES (%s, %s, %s)
                            ON CONFLICT (hash) DO UPDATE SET
                                link = EXCLUDED.link,
                                filename = COALESCE({tableName}.filename, EXCLUDED.filename)""",
                        (hash_val, sidecar_link, filename),
                    )
                    logger.debug(
                        f" Saved sidecar link to DB: {hash_val[:10]} → {sidecar_link}"
                    )
                except Exception as e:
                    logger.warning(f" Failed saving sidecar link for {image_path}: {e}")

                continue

            # --- filename lookup ---
            cur.execute(
                f"SELECT link FROM {tableName} WHERE filename = %s",
                (filename,),
            )
            result = cur.fetchone()
            if result:
                cached_link = result[0]
                logger.debug(f" Cached by filename: {image_path} → {cached_link}")
                results.append(cached_link)
                continue

            # --- hash lookup ---
            hash_val = compute_hash(image_path)
            cached_link = load_link_by_hash(cur, hash_val)

            if cached_link:
                logger.debug(f" Cached by hash: {image_path} → {cached_link}")
                results.append(cached_link)
                link_hash_map[hash_val] = cached_link

                # Backfill filename if missing
                cur.execute(
                    f"UPDATE {tableName} SET filename = %s WHERE hash = %s AND (filename IS NULL OR filename = '')",
                    (filename, hash_val),
                )
                continue

            # --- upload if not cached ---
            if not args.useSaved:
                try:
                    direct_link = upload_image(image_path)
                    logger.debug(f" Uploaded {image_path} → {direct_link}")

                    cur.execute(
                        f"""INSERT INTO {tableName} (hash, link, filename)
                            VALUES (%s, %s, %s)
                            ON CONFLICT DO NOTHING""",
                        (hash_val, direct_link, filename),
                    )
                    logger.debug(f" Saved to DB: {hash_val[:10]} → {direct_link}")
                    results.append(direct_link)
                    link_hash_map[hash_val] = direct_link

                except Exception as e:
                    logger.warning(f" Upload error for {image_path}: {e}")

        conn.commit()
        dir = os.path.dirname(image_paths[0])
        logger.info(f"Commit successful for {dir}")
        cur.close()
        return results, link_hash_map

    except Exception as e:
        logger.info(f" Critical DB error: {e}")
        return [], {}
