from pixBoards.log_utils import setup_logger

logger = setup_logger()


def assign_nested_boards(boards):
    board_map = {b.name: b for b in boards}
    logger.debug("Board Map Keys:  %s", list(board_map.keys()))
    nested_set = set()

    for b in boards:
        parts = b.name.split("_~")
        if len(parts) > 1:
            for depth in range(len(parts) - 1, 0, -1):
                parent_name = "_~".join(parts[:depth])
                parent = board_map.get(parent_name)
                if parent:
                    parent.nested_boards.append(b)
                    nested_set.add(b)
                    break

    # Only boards that are not nested under any parent are roots
    root_boards = [b for b in boards if b not in nested_set]
    return root_boards
