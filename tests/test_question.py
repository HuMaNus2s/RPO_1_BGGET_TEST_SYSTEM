from classes.Question import Question
def test_question_creation(): # Проверка вопроса
    q = Question("Тест?", correct=True, is_resolved=False, points=10)
    assert q.content == "Тест?"
    assert q.correct is True
    assert q.resolved is False
    assert q.points == 10


def test_question_to_json(): # Проверка JSON вопроса
    q = Question("Тест?", correct=False, is_resolved=True, points=7)
    data = q.toJSON
    assert isinstance(data, dict)
    assert data['content'] == "Тест?"
    assert data['correct'] is False
    assert data['points'] == 7