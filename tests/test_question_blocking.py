import pytest
import json
import os
import sys
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web.app import app
from classes.Category import Category
from classes.Question import Question


@pytest.fixture
def client(tmp_path):
    app.config['TESTING'] = True
    app.secret_key = 'test_secret_key'
    
    data_path = str(tmp_path) + '/'
    os.makedirs(tmp_path, exist_ok=True)
    
    users_file = os.path.join(data_path, 'users', 'users.json')
    os.makedirs(os.path.dirname(users_file), exist_ok=True)
    with open(users_file, 'w', encoding='utf-8') as f:
        json.dump({'users': [
            {'username': 'testuser', 'password': 'test', 'role': 'admin', 'points': 0},
            {'username': 'admin', 'password': 'admin', 'role': 'admin', 'points': 0}
        ]}, f)
    
    with patch('web.app.DATA_PATH', data_path):
        with patch('config.config.DATA_PATH', data_path):
            with patch('classes.Category.DATA_PATH', data_path):
                with patch('web.app.USERS_FILE', users_file):
                    from managers.CategoryManager import CategoryManager
                    real_manager = CategoryManager(data_path)
                    
                    with patch('web.app.manager', real_manager):
                        with app.test_client() as client:
                            yield client


@pytest.fixture
def admin_session(client):
    with client.session_transaction() as sess:
        sess['username'] = 'admin'
        sess['role'] = 'admin'
        sess['points'] = 0
    return client


@pytest.fixture
def user_session(client):
    with client.session_transaction() as sess:
        sess['username'] = 'testuser'
        sess['role'] = 'admin'
        sess['points'] = 0
    return client


@pytest.fixture
def category_with_questions(user_session):
    response = user_session.post('/api/admin/category',
        json={'name': 'Тест блокировки'},
        content_type='application/json')
    
    user_session.post('/api/admin/category/Тест блокировки/questions',
        json={'content': 'Вопрос 1?', 'correct': True, 'points': 5},
        content_type='application/json')
    
    user_session.post('/api/admin/category/Тест блокировки/questions',
        json={'content': 'Вопрос 2?', 'correct': False, 'points': 7},
        content_type='application/json')
    
    return response


def test_question_blocked_after_answer(user_session, tmp_path, category_with_questions):
    response = user_session.post('/api/category/Тест блокировки/answer',
        json={'question_id': 0, 'answer': True},
        content_type='application/json')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['correct'] is True
    
    response = user_session.post('/api/category/Тест блокировки/answer',
        json={'question_id': 0, 'answer': False},
        content_type='application/json')
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'уже был дан ответ' in data['error']


def test_category_finish_counts_only_answered(user_session, tmp_path, category_with_questions):
    user_session.post('/api/category/Тест блокировки/answer',
        json={'question_id': 0, 'answer': True},
        content_type='application/json')
    
    response = user_session.post('/api/category/Тест блокировки/finish')
    assert response.status_code == 200
    data = json.loads(response.data)
    
    assert data['answered_count'] == 1
    assert data['correct_count'] == 1
    assert data['category_points'] == 5


def test_category_finish_with_wrong_answer(user_session, tmp_path, category_with_questions):
    user_session.post('/api/category/Тест блокировки/answer',
        json={'question_id': 0, 'answer': True},
        content_type='application/json')
    
    user_session.post('/api/category/Тест блокировки/answer',
        json={'question_id': 1, 'answer': False},
        content_type='application/json')
    
    response = user_session.post('/api/category/Тест блокировки/finish')
    assert response.status_code == 200
    data = json.loads(response.data)
    
    assert data['answered_count'] == 2
    assert data['correct_count'] == 2
    assert data['category_points'] == 12


def test_start_category_resets_blocking(user_session, tmp_path, category_with_questions):
    user_session.post('/api/category/Тест блокировки/answer',
        json={'question_id': 0, 'answer': True},
        content_type='application/json')
    
    response = user_session.post('/api/category/Тест блокировки/start')
    assert response.status_code == 200
    
    response = user_session.post('/api/category/Тест блокировки/answer',
        json={'question_id': 0, 'answer': True},
        content_type='application/json')
    
    assert response.status_code == 200


def test_user_points_not_updated_on_wrong_answer(user_session, tmp_path, category_with_questions):
    response = user_session.post('/api/category/Тест блокировки/answer',
        json={'question_id': 0, 'answer': False},
        content_type='application/json')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['points'] == 0
    assert data['user_points'] == 0