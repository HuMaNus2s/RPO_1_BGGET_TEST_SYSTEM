import pytest
from unittest.mock import patch

from classes.Category import Category
from classes.Question import Question


@pytest.fixture
def fresh_question(): # Создание вопроса
    return Question("Тест вопрос?", correct=True, is_resolved=False, points=5)

@pytest.fixture
def fresh_category(): # Создание категории
    cat = Category()
    cat.name = "Тест категория"
    cat.is_active = True
    return cat


@pytest.fixture
def mock_data_path(tmp_path): # Проверяет путь для тестов
    """Мокает DATA_PATH для тестов"""
    with patch('config.config.DATA_PATH', str(tmp_path) + '/'):
        yield tmp_path