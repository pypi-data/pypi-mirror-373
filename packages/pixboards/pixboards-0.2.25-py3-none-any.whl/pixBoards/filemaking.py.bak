import os

from pixBoards.arguments import args
from pixBoards.config_loader import outputDir
from pixBoards.create import (
    create_css_file,
    create_html_file,
    create_index_file,
    create_js_file,
)
from pixBoards.db import save_board


def create_output_files(root_boards, boards, conn):
    def create_semi_indexes(boards):
        for b in boards:
            if b.dummy_status is True:
                create_index_file(b.nested_boards, outputDir, b.name, sub_index=True)
                # print("board name is")
                # print(b.name)

    if not args.saveBoards:
        for b in boards:
            for p in b.pages:
                create_html_file(p)
    else:
        for b in boards:
            save_board(conn, b)
            for p in b.pages:
                create_html_file(p)

    os.makedirs(outputDir, exist_ok=True)
    create_index_file(root_boards, outputDir)
    create_semi_indexes(boards)
    create_css_file(outputDir)
    create_js_file(outputDir)
