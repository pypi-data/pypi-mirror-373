import logging

logger = logging.getLogger(__name__)

from pixBoards.arguments import args
from pixBoards.config_loader import config

if args.upload:
    import psycopg2


def create_boards_table(conn):
    with conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS savedBoards (
                id SERIAL PRIMARY KEY,
                title TEXT,
                output_path TEXT,
                subfolders TEXT[],
                num_images INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )
        conn.commit()


def save_board(conn, board):
    with conn.cursor() as cur:
        # Convert nested_boards (list of board objects) to list of names or paths
        subfolders = [b.name for b in board.nested_boards]

        cur.execute(
            """
            INSERT INTO savedBoards (title, output_path, subfolders, num_images)
            VALUES (%s, %s, %s, %s)
        """,
            (
                board.name,
                str(board.output_file_loc),
                subfolders,  # Now a list of strings
                len(board.image_paths),
            ),
        )
        conn.commit()
        logger.info(f"inserted board {board.name}")


def create_conn():
    conn = psycopg2.connect(
        dbname=config["dbname"],
        user=config["user"],
        password=config["password"],
        host=config["host"],
    )
    return conn
