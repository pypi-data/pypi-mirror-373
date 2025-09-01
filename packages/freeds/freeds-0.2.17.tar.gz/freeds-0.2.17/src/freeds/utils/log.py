import logging
import sys


def setup_logging(
    name: str,
    freeds_level: int = logging.INFO,
    global_level: int = logging.WARNING,
) -> logging.Logger:
    root_logger = logging.getLogger()

    if not root_logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="[%(asctime)s] %(levelname)s %(name)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        root_logger.addHandler(handler)

    # other packages
    root_logger.setLevel(global_level)

    # our packages
    for n in [name, "freeds"]:
        logging.getLogger(n).setLevel(freeds_level)

    return logging.getLogger(name)
