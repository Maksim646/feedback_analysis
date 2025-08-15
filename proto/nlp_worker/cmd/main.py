import logging
import argparse
import sys

from config.config import load_config
from server.grpc_server import serve


def init_logger(level=logging.DEBUG):
    logger = logging.getLogger("NlpWorkerService")
    logger.setLevel(level)
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        '{"time": "%(asctime)s", "level": "%(levelname)s", "name": "%(name)s", "message": "%(message)s"}'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def main():
    parser = argparse.ArgumentParser(description="NLP Worker Service")
    parser.add_argument("--config", default="config/config.yaml", help="Path to config file")
    args = parser.parse_args()

    config = load_config(args.config)

    log_level = logging.DEBUG if config.logger.level == "debug" else logging.INFO
    logger = init_logger(level=log_level)
    logger.info("Logger initialized")

    try:
        serve(config, logger)
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
