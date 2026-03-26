from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from pathlib import Path
import json
import os

from config.config import web
from config.config import DATA_PATH
from config.log_config import logger

from managers.CategoryManager import CategoryManager

manager = CategoryManager()

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

@app.route('/category/<name>')
def category_page(name):
    return render_template('category.html', category_name=name)


@app.route('/api/categories', methods=['GET'])
def get_all_categories():
    """Получить упрощённый список категорий для главной"""
    try:
        manager.load_all_categories()
        categories = []
        
        for cat in manager.categories:
            categories.append({
                'name': cat.name,
                'is_finished': cat.is_finished,
                'questions_count': len(cat.questions_),
                'points': cat.points_
            })
        
        return jsonify({
            'categories': categories,
            'total': len(categories)
        }), 200
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        return jsonify({'error': str(e)}), 500
    

@app.route('/api/category/<name>', methods=['GET'])
def get_category(name):
    """Получить полную информацию о категории с вопросами"""
    try:
        # Ищем категорию по имени
        category = None
        for cat in manager.categories:
            if cat.name == name:
                category = cat
                break
        
        # Если не найдена в памяти - пробуем загрузить
        if not category:
            temp_cat = manager.categories.__class__()
            temp_cat = type('TempCategory', (), {'name_': name, 'loadFromFile': lambda self: None})()
            from Category import Category
            temp_category = Category(name=name)
            category = temp_category.loadFromFile()
        
        if not category:
            return jsonify({'error': 'Категория не найдена'}), 404
        
        return jsonify({
            'name': category.name,
            'is_finished': category.is_finished,
            'is_active': category.is_active,
            'points': category.points_,
            'questions': [
                {
                    'id': idx,
                    'content': q.content_,
                    'points': q.points_,
                    'is_resolved': q.is_resolved_
                }
                for idx, q in enumerate(category.questions_)
            ],
            'total_questions': len(category.questions_)
        }), 200
        
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        return jsonify({'error': str(e)}), 500
    
@app.route('/api/category/<name>/answer', methods=['POST'])
def answer_question(name):
    """Принять ответ на вопрос (Да/Нет)"""
    try:
        data = request.get_json()
        question_id = data.get('question_id')
        answer = data.get('answer')  # True/False
        
        # Находим категорию
        category = None
        for cat in manager.categories:
            if cat.name == name:
                category = cat
                break
        
        if not category:
            return jsonify({'error': 'Категория не найдена'}), 404
        
        if question_id < 0 or question_id >= len(category.questions_):
            return jsonify({'error': 'Неверный ID вопроса'}), 400
        
        # Проверяем ответ
        question = category.questions_[question_id]
        is_correct = (answer == question.correct_)
        
        # Обновляем статус вопроса
        question.is_resolved_ = True
        
        # Сохраняем изменения
        category.saveInFile()
        
        return jsonify({
            'correct': is_correct,
            'points': question.points_ if is_correct else 0,
            'message': 'Правильно!' if is_correct else 'Неправильно!'
        }), 200
        
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        return jsonify({'error': str(e)}), 500
    
@app.route('/api/category/<name>/finish', methods=['POST'])
def finish_category(name):
    """Завершить категорию и подсчитать баллы"""
    try:
        category = None
        for cat in manager.categories:
            if cat.name == name:
                category = cat
                break
        
        if not category:
            return jsonify({'error': 'Категория не найдена'}), 404
        
        total_points = category.end()
        category.is_finished_ = True
        category.saveInFile()
        
        return jsonify({
            'points': total_points,
            'is_finished': True
        }), 200
        
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)