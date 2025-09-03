import logging
import sys

logger = logging.getLogger("p9customtheme")
logger.setLevel(logging.WARNING)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)
