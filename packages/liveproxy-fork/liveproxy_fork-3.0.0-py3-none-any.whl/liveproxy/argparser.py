import argparse
from textwrap import dedent

from liveproxy import __version__ as liveproxy_version


def num(type, min=None, max=None):
    def func(value):
        value = type(value)
        if min is not None and not (value > min):
            raise argparse.ArgumentTypeError(
                "{0} value must be more than {1} but is {2}".format(
                    type.__name__, min, value
                )
            )
        if max is not None and not (value <= max):
            raise argparse.ArgumentTypeError(
                "{0} value must be at most {1} but is {2}".format(
                    type.__name__, max, value
                )
            )
        return value

    func.__name__ = type.__name__
    return func


parser = argparse.ArgumentParser(
    fromfile_prefix_chars="@",
    add_help=False,
    usage="%(prog)s --host [HOST] --port [PORT]",
    description=dedent("""
    LiveProxy is a local URL Proxy for Streamlink
    """),
    epilog=dedent("""
    For more in-depth documentation see:
      https://github.com/amjiddader/liveproxy/blob/master/README.md
    """)
)

general = parser.add_argument_group("General options")
general.add_argument(
    "-h", "--help",
    action="store_true",
    help="""
    Show this help message and exit.
    """
)
general.add_argument(
    "-V", "--version",
    action="version",
    version="%(prog)s {0}".format(liveproxy_version),
    help="""
    Show version number and exit.
    """
)
general.add_argument(
    "--loglevel",
    metavar="LEVEL",
    choices=("CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"),
    default="INFO",
    help="""
    Set the log message threshold.

    https://docs.python.org/3/library/logging.html#logging-levels

    Valid levels are: CRITICAL, ERROR, WARNING, INFO, DEBUG, NOTSET
    """
)

server = parser.add_argument_group("Server options")
server.add_argument(
    "--host",
    metavar="HOST",
    type=str,
    default="127.0.0.1",
    help="""
    A fixed IP to use as a HOST.

    Default is 127.0.0.1
    """
)
server.add_argument(
    "--port",
    metavar="PORT",
    type=num(int, min=0, max=65535),
    default=53422,
    help="""
    A fixed PORT to use for the HOST.

    Default is 53422
    """
)

__all__ = ["parser"]
