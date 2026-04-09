import logging
import sys
from pathlib import Path

def setup_logger():
    logger = logging.getLogger('test_system')
    logger.setLevel(logging.DEBUG)

    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

# Path('logs').mkdir(exist_ok=True) - Отключено для Vercel
# file_handler = logging.FileHandler('logs/app.log', encoding='utf-8') - Отключено для Vercel
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger

logger = setup_logger()