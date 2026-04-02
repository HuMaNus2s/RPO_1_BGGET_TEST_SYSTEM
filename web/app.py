from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from pathlib import Path
import json
import os
from functools import wraps

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

def admin_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'admin':
            flash("Доступ только для администратора", "danger")
            return redirect(url_for('index'))
        return func(*args, **kwargs)
    return decorated_function

def login_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not session.get('username'):
            flash("Пожалуйста, войдите в систему", "warning")
            return redirect(url_for('index'))
        return func(*args, **kwargs)
    return decorated_function

def load_users():
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('users', [])
    except FileNotFoundError:
        logger.error("Файл пользователей не найден")
        return []
    except json.JSONDecodeError:
        logger.error("Файл пользователей повреждён")
        return []

def save_users(users):
    try:
        os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump({'users': users}, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        logger.error(f"Ошибка сохранения пользователей: {e}")
        return False

def get_user_by_username(username):
    """Найти пользователя по имени"""
    users = load_users()
    for user in users:
        if user.get('username', '').lower() == username.lower():
            return user
    return None

def update_user_points(username, points_to_add):
    """Обновить баллы пользователя в файле"""
    users = load_users()
    for user in users:
        if user.get('username', '').lower() == username.lower():
            current_points = user.get('points', 0)
            user['points'] = current_points + points_to_add
            save_users(users)
            return user['points']
    return None

def sync_session_points(username):
    user = get_user_by_username(username)
    if user:
        session['points'] = user.get('points', 0)
        return session['points']
    return 0

@app.route('/')
def index():
    if session.get('username'):
        sync_session_points(session['username'])
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
            users = load_users()

            for user in users:
                if user.get("username", "").lower() == username:
                    if user.get("password") == password:
                        session['username'] = user["username"]
                        session['role'] = user.get("role", "user")
                        session['points'] = user.get('points', 0)  # Загружаем баллы из файла
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
    session.pop('points', None)
    session.pop('role', None)
    flash('До встречи!', 'info')
    return redirect(url_for('index'))

@app.route('/admin')
@admin_required
def admin_dashboard():
    return render_template('admin.html')

@app.route('/api/admin/categories', methods=['GET'])
@admin_required
def admin_get_categories():
    """Получить все категории для админа"""
    try:
        manager.load_all_categories()
        categories = []
        
        for cat in manager.categories:
            categories.append({
                'name': cat.name,
                'is_finished': cat.is_finished,
                'is_active': cat.is_active,
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

@app.route('/api/admin/category', methods=['POST'])
@admin_required
def admin_create_category():
    """Создать новую категорию"""
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        
        if not name:
            return jsonify({'error': 'Название категории обязательно'}), 400
        
        from classes.Category import Category
        new_category = Category(name=name)
        
        if new_category.saveInFile():
            manager.load_all_categories()
            return jsonify({
                'message': 'Категория создана',
                'category': {
                    'name': new_category.name,
                    'is_finished': new_category.is_finished,
                    'is_active': new_category.is_active,
                    'questions_count': len(new_category.questions_),
                    'points': new_category.points_
                }
            }), 201
        else:
            return jsonify({'error': 'Ошибка сохранения категории'}), 500
            
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/category/<name>', methods=['PUT'])
@admin_required
def admin_update_category(name):
    """Обновить категорию"""
    try:
        data = request.get_json()
        new_name = data.get('name', '').strip()
        
        if not new_name:
            return jsonify({'error': 'Название категории обязательно'}), 400
        
        logger.info(f"Ищем категорию '{name}' в manager.categories: {[c.name for c in manager.categories]}")
        
        category = None
        for cat in manager.categories:
            if cat.name == name:
                category = cat
                break
        
        if not category:
            return jsonify({'error': 'Категория не найдена'}), 404
        
        old_filename = name.replace(' ', '_')
        new_filename = new_name.replace(' ', '_')
        
        import os
        old_path = os.path.join(DATA_PATH, f'{old_filename}.json')
        new_path = os.path.join(DATA_PATH, f'{new_filename}.json')
        
        if old_filename != new_filename and os.path.exists(old_path):
            os.remove(old_path)
        
        category.name_ = new_name
        category.saveInFile()
        manager.load_all_categories()
        
        return jsonify({
            'message': 'Категория обновлена',
            'category': {
                'name': category.name,
                'is_finished': category.is_finished,
                'is_active': category.is_active,
                'questions_count': len(category.questions_),
                'points': category.points_
            }
        }), 200
            
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/category/<name>', methods=['DELETE'])
@admin_required
def admin_delete_category(name):
    """Удалить категорию"""
    try:
        import os
        filename = name.replace(' ', '_')
        filepath = os.path.join(DATA_PATH, f'{filename}.json')
        
        if os.path.exists(filepath):
            os.remove(filepath)
            manager.load_all_categories()
            return jsonify({'message': 'Категория удалена'}), 200
        else:
            return jsonify({'error': 'Категория не найдена'}), 404
            
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/category/<name>/questions', methods=['POST'])
@admin_required
def admin_add_question(name):
    """Добавить вопрос в категорию"""
    try:
        data = request.get_json()
        content = data.get('content', '').strip()
        correct = data.get('correct', False)
        points = data.get('points', 5)
        
        if not content:
            return jsonify({'error': 'Текст вопроса обязателен'}), 400
        
        category = None
        for cat in manager.categories:
            if cat.name == name:
                category = cat
                break
        
        if not category:
            from classes.Category import Category
            temp_category = Category(name=name)
            category = temp_category.loadFromFile()
        
        if not category:
            return jsonify({'error': 'Категория не найдена'}), 404
        
        from classes.Question import Question
        new_question = Question(content=content, correct=correct, points=points)
        category.addQuestion(new_question)
        category.saveInFile()
        manager.load_all_categories()
        
        return jsonify({
            'message': 'Вопрос добавлен',
            'question': {
                'id': len(category.questions_) - 1,
                'content': new_question.content_,
                'correct': new_question.correct_,
                'points': new_question.points_,
                'is_resolved': new_question.is_resolved_
            }
        }), 201
            
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/category/<name>/questions/<int:question_id>', methods=['DELETE'])
@admin_required
def admin_delete_question(name, question_id):
    """Удалить вопрос из категории"""
    try:
        category = None
        for cat in manager.categories:
            if cat.name == name:
                category = cat
                break
        
        if not category:
            return jsonify({'error': 'Категория не найдена'}), 404
        
        if question_id < 0 or question_id >= len(category.questions_):
            return jsonify({'error': 'Неверный ID вопроса'}), 400
        
        category.removeQuestion(question_id)
        category.saveInFile()
        manager.load_all_categories()
        
        return jsonify({'message': 'Вопрос удален'}), 200
            
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/category/<name>')
@login_required
def category_page(name):
    return render_template('category.html', category_name=name)

@app.route('/api/user/points', methods=['GET'])
@login_required
def get_user_points():
    """Получить текущие баллы пользователя"""
    username = session['username']
    points = sync_session_points(username)
    return jsonify({'points': points, 'username': username}), 200

@app.route('/api/categories', methods=['GET'])
@login_required
def get_all_categories():
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
@login_required
def get_category(name):
    """Получить полную информацию о категории с вопросами"""
    try:
        manager.load_all_categories()
        category = None
        for cat in manager.categories:
            if cat.name == name:
                category = cat
                break

        if not category:
            from classes.Category import Category
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
                    'correct': q.correct_,
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
@login_required
def answer_question(name):
    """Принять ответ на вопрос (Да/Нет)"""
    try:
        data = request.get_json()
        question_id = data.get('question_id')
        answer = data.get('answer')

        manager.load_all_categories()
        category = None
        for cat in manager.categories:
            if cat.name == name:
                category = cat
                break
        
        if not category:
            return jsonify({'error': 'Категория не найдена'}), 404
        
        if question_id < 0 or question_id >= len(category.questions_):
            return jsonify({'error': 'Неверный ID вопроса'}), 400
        
        question = category.questions_[question_id]
        
        # ✅ ПРОВЕРЯЕМ, НЕ БЫЛ ЛИ УЖЕ ОТВЕЧЕН ВОПРОС
        if question.is_resolved_:
            return jsonify({'error': 'На этот вопрос уже был дан ответ'}), 400
        
        is_correct = (answer == question.correct_)
        logger.info(f"Ответ: {answer}, Правильный: {question.correct_}, Результат: {is_correct}")
        question.is_resolved_ = True
        question.user_correct_ = is_correct
        category.saveInFile()
        
        points_earned = question.points_ if is_correct else 0
        
        # ✅ НАЧИСЛЯЕМ БАЛЛЫ ПОЛЬЗОВАТЕЛЮ ТОЛЬКО ПРИ ОТВЕТЕ
        if is_correct and points_earned > 0:
            username = session['username']
            new_total = update_user_points(username, points_earned)
            session['points'] = new_total
        
        return jsonify({
            'correct': is_correct,
            'points': points_earned,
            'message': 'Правильно!' if is_correct else 'Неправильно!',
            'user_points': session['points']
        }), 200
        
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        return jsonify({'error': str(e)}), 500
    
@app.route('/api/category/<name>/start', methods=['POST'])
@login_required
def start_category(name):
    try:
        manager.load_all_categories()
        category = None
        for cat in manager.categories:
            if cat.name == name:
                category = cat
                break
        
        if not category:
            return jsonify({'error': 'Категория не найдена'}), 404
        
        category.reset_questions()

        session.pop(f'answered_{name}', None)
        session.pop(f'category_points_{name}', None)
        
        return jsonify({
            'message': 'Категория начата заново',
            'questions_count': len(category.questions_)
        }), 200
        
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/category/<name>/finish', methods=['POST'])
@login_required
def finish_category(name):
    """Завершить категорию и подсчитать баллы"""
    try:
        manager.load_all_categories()
        category = None
        for cat in manager.categories:
            if cat.name == name:
                category = cat
                break
        
        if not category:
            return jsonify({'error': 'Категория не найдена'}), 404
        
        # ✅ ПОДСЧИТЫВАЕМ БАЛЛЫ КАТЕГОРИИ (не начисляем пользователю повторно!)
        category_points = 0
        answered_count = 0
        correct_count = 0
        
        for q in category.questions_:
            if q.is_resolved_:
                answered_count += 1
                if q.user_correct_:
                    category_points += q.points_
                    correct_count += 1
        
        category.is_finished_ = True
        category.points_ = category_points
        category.saveInFile()
        
        return jsonify({
            'category_points': category_points,
            'answered_count': answered_count,
            'correct_count': correct_count,
            'total_questions': len(category.questions_),
            'is_finished': True,
            'user_points': session['points']
        }), 200
        
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    manager.load_all_categories()
    app.run(debug=True)