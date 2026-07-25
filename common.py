"""Small helpers shared by both robot computers. Kept dependency-free (standard library only)."""

import traceback


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
    Print an exception with an optional context message, followed by its full traceback.

    The traceback is rendered with the traceback module. Interpolating exception.__traceback__ into a
    string (which this used to do) only prints "<traceback object at 0x...>": you get the error message
    but no indication of where it came from, which is the one thing these logs exist to tell you.

    The three-argument call is deliberate: it is the form supported on every Python this runs on. The
    robot computers are on 3.6 / 3.8, where the single-argument form added in 3.10 does not exist yet.

    An exception that was never raised carries no traceback, in which case only the header and the
    exception itself are printed.

    :param exception: the exception to report.
    :param message: optional context line printed above it. Defaults to a plain "Error".
    """
    print(f'{message if message is not None else "Error"}:')
    if exception.__traceback__ is None:
        print(f'\t{exception!r}')
        return
    formatted = traceback.format_exception(type(exception), exception, exception.__traceback__)
    # indent every line so a multi-line traceback stays visually grouped under its message, which matters
    # on both computers because several threads print to the same console
    for line in ''.join(formatted).rstrip().splitlines():
        print(f'\t{line}')
