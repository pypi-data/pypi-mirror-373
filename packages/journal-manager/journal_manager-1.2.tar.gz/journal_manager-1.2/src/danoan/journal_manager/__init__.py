import logging

logger = logging.getLogger("danoan.journal_manager")
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(levelname)s: %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)
