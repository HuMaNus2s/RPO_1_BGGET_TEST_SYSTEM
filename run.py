from web.app import app
from config.config import web
from managers.CategoryManager import CategoryManager

if __name__ == '__main__':
    manager = CategoryManager()
    manager.load_all_categories()
    app.run(debug=False, host='0.0.0.0', port=web.SERVER_PORT)