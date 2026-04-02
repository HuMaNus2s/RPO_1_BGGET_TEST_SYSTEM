import pytest
import json
import os
import sys
from unittest.mock import patch, MagicMock

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
    
    with patch('web.app.DATA_PATH', data_path):
        with patch('config.config.DATA_PATH', data_path):
            with patch('classes.Category.DATA_PATH', data_path):
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
        sess['username'] = 'user'
        sess['role'] = 'user'
        sess['points'] = 0
    return client


def test_admin_create_category(admin_session):
    response = admin_session.post('/api/admin/category',
        json={'name': 'Тестовая категория'},
        content_type='application/json')
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['message'] == 'Категория создана'
    assert data['category']['name'] == 'Тестовая категория'


def test_admin_create_category_empty_name(admin_session):
    response = admin_session.post('/api/admin/category',
        json={'name': ''},
        content_type='application/json')
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data


def test_admin_update_category(admin_session):
    response = admin_session.post('/api/admin/category',
        json={'name': 'Для обновления'},
        content_type='application/json')
    assert response.status_code == 201
    
    response = admin_session.put('/api/admin/category/Для обновления',
        json={'name': 'Обновленная'},
        content_type='application/json')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['message'] == 'Категория обновлена'


def test_admin_delete_category(admin_session):
    response = admin_session.post('/api/admin/category',
        json={'name': 'Для удаления'},
        content_type='application/json')
    assert response.status_code == 201
    
    response = admin_session.delete('/api/admin/category/Для удаления')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['message'] == 'Категория удалена'


def test_admin_delete_nonexistent_category(admin_session):
    response = admin_session.delete('/api/admin/category/Несуществующая123')
    assert response.status_code == 404


def test_admin_add_question(admin_session):
    response = admin_session.post('/api/admin/category',
        json={'name': 'Тест вопросы'},
        content_type='application/json')
    assert response.status_code == 201
    
    response = admin_session.post('/api/admin/category/Тест вопросы/questions',
        json={'content': 'Новый вопрос?', 'correct': True, 'points': 10},
        content_type='application/json')
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['message'] == 'Вопрос добавлен'


def test_admin_add_question_empty_content(admin_session):
    response = admin_session.post('/api/admin/category',
        json={'name': 'Тест пустой'},
        content_type='application/json')
    assert response.status_code == 201
    
    response = admin_session.post('/api/admin/category/Тест пустой/questions',
        json={'content': '', 'correct': True, 'points': 5},
        content_type='application/json')
    
    assert response.status_code == 400


def test_admin_delete_question(admin_session):
    response = admin_session.post('/api/admin/category',
        json={'name': 'Тест удаление'},
        content_type='application/json')
    assert response.status_code == 201
    
    response = admin_session.post('/api/admin/category/Тест удаление/questions',
        json={'content': 'Удалить?', 'correct': True, 'points': 5},
        content_type='application/json')
    assert response.status_code == 201
    
    response = admin_session.delete('/api/admin/category/Тест удаление/questions/0')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['message'] == 'Вопрос удален'


def test_admin_access_denied_for_user(user_session):
    response = user_session.get('/api/admin/categories')
    assert response.status_code == 302


def test_admin_access_denied_without_session(client):
    response = client.get('/api/admin/categories')
    assert response.status_code == 302