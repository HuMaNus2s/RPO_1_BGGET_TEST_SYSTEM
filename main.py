# main.py
from web.app import app
from config.config import web

if __name__ == '__main__':
    app.run(debug=True, host= web.SERVER_HOST, port=web.SERVER_PORT)