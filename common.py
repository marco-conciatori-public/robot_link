"""Small helpers shared by both robot computers. Kept dependency-free (standard library only)."""


def pretty_print_dict(data, _level: int = 0) -> None:
    """Print a (possibly nested) dict with indentation, one key per line."""
    if isinstance(data, dict):
        if _level > 0:
            print()
        for key in data:
            print('\t' * (_level + 1), end='')
            print(f'{key}: ', end='')
            pretty_print_dict(data[key], _level=_level + 1)
    else:
        print(data)


def print_exception(exception: Exception, message: str = None) -> None:
    """
    Print an exception with an optional context message.

    (This is the corrected version: the Jetson's old copy had the message/None branches
    inverted, so it always printed the wrong line.)
    """
    if message is not None:
        print(f'{message}:\n\t{exception}\n\t{exception.__traceback__}')
    else:
        print(f'Error:\n\t{exception}\n\t{exception.__traceback__}')
