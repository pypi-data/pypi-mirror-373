import logging

from xiaozhi_sdk.cli import main

logger = logging.getLogger("xiaozhi_sdk")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.debug("Stopping...")
