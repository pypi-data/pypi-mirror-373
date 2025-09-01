import os
import random
from pathlib import Path

import psycopg2

from pixBoards.arguments import args
from pixBoards.classes import board
from pixBoards.imgchest import append_sidecar_links, process_images
# append_sidecar_links not working properly rn. a future me problem.
from pixBoards.log_utils import setup_logger

from pixBoards.config_loader import config, outputDir



# import yaml


logger = setup_logger(__name__)


# from pixBoards.config_loader import config


def boardsForImglist(imgList_List, listDir, paginate):
    # Now I might need to sanitise the ( image list )list
    # so that there aren't instances with the same name.
    # But as the imagelist files are in the same folder,
    # they won't have the same name, so I leave this for the future me.
    os.makedirs(listDir, exist_ok=True)

    boards = []

    for idx, imgListFile in enumerate(imgList_List):
        boardName = os.path.splitext(os.path.basename(imgListFile))[0]
        with open(imgListFile, "r", encoding="utf-8") as f:
            images = [line.strip() for line in f if line.strip()]

        outputFile = listDir
        logger.info(f"output file = {outputFile}")

        b = board(
            name=boardName,
            output_file_loc=outputFile,
            image_paths=images,
            paginate=paginate,
            # images_per_page=config["page_size"] if paginate else 10000,
            img_list_status=True,
        )
        b.paginate_board()
        boards.append(b)

    return boards


def standardBoards(directories, outputDir, paginate, upload):
    boards = []
    # outputDir = Path(outputDir)
    # outputDir.mkdir(parents=True, exist_ok=True)

    media_extensions = (
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".bmp",
        ".webp",
        # ".heic",  # i will possibly add support to convert these to normal imgs
        # before using them.
        ".mp4",
        ".avi",
        ".webm",
        ".mov",
    )

    for d in directories:
        # normalize to a Path
        src_dir = Path(d)

        if not src_dir.exists():
            logger.warning(f"Skipping non-existent directory: {src_dir}")
            continue

        for root, dirs, files in os.walk(src_dir):
            image_paths = []

            for fname in sorted(files):
                if fname.lower().endswith(media_extensions):
                    abs_path = Path(root) / fname
                    image_paths.append(abs_path.resolve().as_uri())

            logger.debug(f"Processing {root} with {len(image_paths)} images.")

            rel = Path(root).relative_to(os.path.dirname(src_dir))

            board_name = str(rel).replace(os.sep, "_~")
            output_path = outputDir  # everything writes into this one folder
            # collect local files
            local_files = [
                Path(root) / f
                for f in sorted(files)
                if f.lower().endswith(media_extensions)
            ]
            if not local_files:
                logger.debug(f"No media in {root}, creating empty board.")
                b = board(
                    name=board_name,
                    output_file_loc=str(outputDir),
                    image_paths=[],
                    paginate=paginate,
                    upload=upload,
                    dummy_status=True,
                )
            else:
                # create a Board object and paginate it
                b = board(
                    name=board_name,
                    output_file_loc=str(output_path),
                    image_paths=image_paths,
                    paginate=paginate,
                    upload=upload,
                    dummy_status=False,
                )

            b.paginate_board()
            boards.append(b)

            logger.debug(f"Board created: {board_name} ({len(image_paths)} images)")

    return boards


def uploadBoards(directories, outputDir, paginate, upload=True):
    def connect_db():
        return psycopg2.connect(
            dbname=config['dbname'],
            user=config['user'],
            password=config['password'],
            host=config['host'],
        )

    conn = connect_db()
    boards = []
    outputDir = Path(outputDir)
    outputDir.mkdir(parents=True, exist_ok=True)

    media_extensions = (
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".bmp",
        ".webp",
        ".mp4",
        ".avi",
        ".webm",
    )

    for d in directories:
        src_dir = Path(d)
        if not src_dir.exists():
            logger.warning(f"Skipping non-existent directory: {src_dir}")
            continue

        for root, _, files in os.walk(src_dir):
            rel = Path(root).relative_to(os.path.dirname(src_dir))
            board_name = (
                src_dir.name if rel == Path(".") else str(rel).replace(os.sep, "_~")
            )

            local_files = [
                Path(root) / f
                for f in sorted(files)
                if f.lower().endswith(media_extensions)
            ]

            if not local_files:
                logger.debug(f"No media in {root}, creating empty board.")
                boards.append(
                    board(
                        name=board_name,
                        output_file_loc=str(outputDir),
                        image_paths=[],
                        paginate=paginate,
                        upload=upload,
                        dummy_status=True,
                    )
                )
                continue

            logger.debug(f"Uploading {len(local_files)} images from {root}…")
            try:
                # local_files = append_sidecar_links(local_files, conn) # fix this function.
                #  this function has problems in the images not being counted in the index maker or the randomiser.
                http_links, hash_map = process_images(local_files, conn)
            except Exception as e:
                logger.error(f"Failed to upload images in {root}: {e}")
                continue

            b = board(
                name=board_name,
                output_file_loc=str(outputDir),
                image_paths=http_links,
                paginate=paginate,
                # images_per_page=(config["page_size"] if paginate else 10000),
                upload=upload,
                # no_of_imgs=len(http_links),
                # outputDir=outputDir
            )
            b.link_hash_map = hash_map
            b.paginate_board()
            boards.append(b)
            logger.debug(
                f"Uploaded board created: {board_name} ({len(http_links)} images)"
            )

    conn.close()
    return boards


def randomBoard(boards, count, outputDir, paginate, upload):
    images = []
    for b in boards:
        images.extend(b.image_paths)

    try:
        ran_images = random.sample(images, count)
    except:
        random.shuffle(images)
        ran_images = images

    ranBoard = board(
        name="randomised_set",
        output_file_loc=outputDir,
        image_paths=ran_images,
        paginate=paginate,
        upload=upload,
        dummy_status=False,
    )

    ranBoard.paginate_board()

    return ranBoard
