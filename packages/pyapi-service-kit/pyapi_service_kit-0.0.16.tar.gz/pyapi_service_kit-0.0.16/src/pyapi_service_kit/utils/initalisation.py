import argparse
import asyncio
import logging
import logging.config
import signal
import sys
import yaml


def parse_args(default_config_file: str, default_log_config: str) -> argparse.Namespace:
    argv = sys.argv[1:]
    parser = argparse.ArgumentParser(add_help=True)

    parser.add_argument(
        "-f", "--config", help="Path to config file", default=None, dest="CONFIG_FILE"
    )

    parser.add_argument(
        "-l",
        "--log-config",
        help="Path to logger config",
        default=default_log_config,
        action="store",
        dest="CONFIG_LOG",
    )

    args = parser.parse_args(argv)

    if not args.CONFIG_FILE:
        args.CONFIG_FILE = default_config_file

    return args


def initialise_logging(filename: str) -> None:
    try:
        with open(filename, "r") as file:
            logging_dict = yaml.safe_load(file)
        logging.config.dictConfig(logging_dict)
    except FileNotFoundError:
        print(f"Logger config file not found at {filename}")
    except Exception as e:
        logger = logging.getLogger("UNCAUGHT_EXCEPTION")
        logger.fatal("", exc_info=e)

    # Set up exception hook
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        logger = logging.getLogger("UNCAUGHT_EXCEPTION")
        logger.fatal("", exc_info=(exc_type, exc_value, exc_traceback))

    sys.excepthook = handle_exception


def create_stop_event():
    stop = asyncio.Future()

    for sig in (signal.SIGINT, signal.SIGTERM):
        asyncio.get_event_loop().add_signal_handler(sig, lambda: stop.set_result(None))

    return stop
