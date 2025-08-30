import time
from datetime import date

from pixBoards.arguments import args
from pixBoards.boardmakers import (
    boardsForImglist,
    randomBoard,
    standardBoards,
    uploadBoards,
)
from pixBoards.log_utils import setup_logger

logger = setup_logger(__name__)


from pixBoards.config_loader import config, outputDir
from pixBoards.db import create_boards_table, create_conn


def main():

    start_time = time.time()
    today = date.today()
    logger.info(f"Today is {today}, Starting ...")

    conn = None
    if args.upload or args.saveBoards:
        conn = create_conn()

    if args.saveBoards:
        create_boards_table(conn)

    paginate = config.get("paginate", True) is True
    boards = []

    # Handle imagelist mode
    if args.useLists or args.imageLists:
        usingLists = True
        imgList_List = (
            args.imageLists if args.imageLists else config.get("imageLists", [])
        )
        boards.extend(boardsForImglist(imgList_List, outputDir, paginate))

        if args.includeLocal:
            usingLists = False
    else:
        usingLists = False

    # Handle upload
    if args.upload:
        logger.info("Upload case")
        upload = True
    else:
        upload = False

    if args.dir:
        directories = [args.dir]
        logger.debug("Using --dir → %s", directories)
    elif config.get("directories"):
        directories = config["directories"]
        logger.debug(f"Using config.directories → %s", directories)
    else:
        directories = []

    # board generation standar case
    if directories and not usingLists:
        if upload:
            boards.extend(uploadBoards(directories, outputDir, paginate, upload=True))
        else:
            boards.extend(
                standardBoards(directories, outputDir, paginate, upload=False)
            )

    if args.random:
        rancount = args.random

    # for random case
    if args.random:
        boards.append(randomBoard(boards, rancount, outputDir, paginate, upload))

    from pixBoards.nest_boards import assign_nested_boards

    root_boards = assign_nested_boards(boards)
    logger.debug(root_boards)

    # Group boards by output directory and create output
    logger.info(f"Total boards to generate HTML for: {len(boards)}")
    from pixBoards.filemaking import create_output_files

    create_output_files(root_boards, boards, conn)

    # Print nested board tree
    def print_board_tree(boards, depth=0):
        for b in boards:
            print("  " * depth + f"- {b.clean_name}")
            print_board_tree(b.nested_boards, depth + 1)

    print("Boards structure - ")
    print_board_tree(root_boards)

    logger.debug(root_boards)
    print(f"browse boards at - {outputDir}")

    elapsed_time = time.time() - start_time
    logger.info(f"Finished in {elapsed_time:.2f} seconds.")


if __name__ == "__main__":
    main()
