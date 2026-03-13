from typing import List
import os
from classes.Question import Question
from classes.Category import Category
from config.config import DATA_PATH

def test_category_init(): # Тест на инициализацию категории
    cat = Category()
    cat.name = "Новая"
    assert cat.name == "Новая"
    assert cat.is_finished is False
    assert len(cat.questions_) == 0


def test_add_question(fresh_category, fresh_question): # Тест на добавление вопроса
    fresh_category.addQuestion(fresh_question)
    assert len(fresh_category.questions_) == 1
    assert fresh_category.questions_[0].content == "Тест вопрос?"


def test_remove_question(): # Тест на удаление вопроса
    cat = Category()
    q1 = Question("Q1", correct=True, is_resolved=False, points=5)
    q2 = Question("Q2", correct=False, is_resolved=True, points=10)
    cat.addQuestion(q1)
    cat.addQuestion(q2)
    assert len(cat.questions_) == 2
    
    cat.removeQuestion(0)
    assert len(cat.questions_) == 1
    assert cat.questions_[0].content == "Q2"


def test_remove_question_invalid_index(fresh_category): # Тест на удаление несущ. вопроса
    fresh_category.removeQuestion(99)


def test_to_json(fresh_category): # Тест на проверку JSON
    q = Question("Тест?", correct=True, is_resolved=False, points=5)
    fresh_category.addQuestion(q)
    
    data = fresh_category.toJSON
    assert data['name'] == "Тест категория"
    assert len(data['questions']) == 1
    assert data['questions'][0]['content'] == "Тест?"


def test_save_and_load_file(): # тест сохранение и чтение JSON
    cat = Category()
    cat.name = "ФайлТест"
    cat.is_active = True
    q = Question("Сохранить?", correct=True, is_resolved=False, points=15)
    cat.addQuestion(q)
    
    result = cat.saveInFile()
    assert result is True
    
    loaded = cat.loadFromFile()
    assert loaded is not None
    assert loaded.name == "ФайлТест"
    assert len(loaded.questions_) == 1
    assert loaded.questions_[0].content == "Сохранить?"

    os.remove(f"{DATA_PATH}{loaded.name}.json")