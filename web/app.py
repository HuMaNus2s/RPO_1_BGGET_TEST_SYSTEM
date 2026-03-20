from flask import Flask, render_template, request, redirect, url_for, session, flash
import json
import os

from config.config import web
from config.config import DATA_PATH
from config.log_config import logger

app = Flask(__name__,
            template_folder='pages',
            static_folder='static')

app.secret_key = web.SECRET_KEY

USERS_FILE = os.path.join(DATA_PATH, 'users', 'users.json')

from functools import wraps

def admin_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'admin':
            flash("Доступ только для администратора", "danger")
            return redirect(url_for('index'))
        return func(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip().lower()
        password = request.form.get('password', '').strip()

        if not username or not password:
            flash("Введите имя пользователя и пароль", "warning")
            return render_template('index.html')

        try:
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)

            users = data.get("users", [])

            for user in users:
                if user.get("username", "").lower() == username:
                    if user.get("password") == password:
                        session['username'] = user["username"]
                        session['role'] = user.get("role", "user")
                        flash(f"Добро пожаловать, {user['username']}!", "success")
                        return redirect(url_for('index'))
                    else:
                        flash("Неверный пароль", "danger")
                        return render_template('index.html')

            flash("Пользователь не найден", "danger")

        except FileNotFoundError:
            flash("Файл с пользователями не найден", "danger")
        except json.JSONDecodeError:
            flash("Файл users.json повреждён", "danger")
        except Exception as e:
            flash(f"Ошибка: {str(e)}", "danger")

    return render_template('index.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('До встречи!', 'info')
    return redirect(url_for('index'))

@app.route('/admin')
@admin_required
def admin_dashboard():
    return "Админ-панель (только для role: admin)"


if __name__ == '__main__':
    app.run(debug=True)