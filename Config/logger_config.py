import sys
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s", # Убрали %(name)s, так как логгер будет один
    handlers=[
        logging.StreamHandler(sys.stdout)
    ],
)

log = logging.getLogger("App")