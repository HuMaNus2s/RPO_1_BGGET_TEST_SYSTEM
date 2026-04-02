# main.py
from web.app import app
from config.config import web
import subprocess
import sys

if __name__ == '__main__':
    result = subprocess.run([sys.executable, '-m', 'pytest', 'tests/', '-v', '--tb=short'], 
                          capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
        sys.exit(1)
    
    app.run(debug=True, host= web.SERVER_HOST, port=web.SERVER_PORT)
