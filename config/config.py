import os
from pathlib import Path

# ====== WEB ======

class web:
    SERVER_HOST = '127.0.0.1'
    SERVER_PORT = 5000
    SECRET_KEY = 'vfyh473g-f387x2cg-63tfr34u438'

ON_RENDER = os.environ.get('RENDER') == 'true'

BASE_DIR = Path(__file__).resolve().parent.parent

if ON_RENDER:
    DATA_PATH = BASE_DIR / 'data'
else:
    DATA_PATH = BASE_DIR / 'data'