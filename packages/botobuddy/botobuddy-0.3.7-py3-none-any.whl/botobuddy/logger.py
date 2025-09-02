import logging as lg
from rich.logging import RichHandler


logger = lg.getLogger('botobuddy')


def setup_logging(verbose: bool = False):
    handler = RichHandler(rich_tracebacks=False, show_path=False)
    logger.addHandler(handler)
    logger.setLevel(lg.INFO if not verbose else lg.DEBUG)
