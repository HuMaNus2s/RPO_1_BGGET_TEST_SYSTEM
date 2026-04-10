from typing import List
import json

from config.config import DATA_PATH
from config.log_config import logger
from .Question import Question

class Category:
    name_: str
    points_: int
    questions_: List[Question]
    is_finished_: bool
    is_active_: bool

    def __init__(self, name: str = "", questions: List[Question] = None, 
                 is_finished: bool = False, is_active: bool = False, points: int = 0):
        self.name_ = name
        self.points_ = points
        self.questions_ = questions if questions is not None else []
        self.is_finished_ = is_finished
        self.is_active_ = is_active
        self.active_question_id: int = 0

    @property
    def name(self):
        return self.name_
    
    @name.setter
    def name(self, value: str):
        self.name_ = value
    
    @property
    def points(self):
        return self.points_

    @points.setter
    def points(self, value: int):
        self.points_ = value

    @property
    def is_finished(self):
        return self.is_finished_
    
    @is_finished.setter
    def is_finished(self, value: bool):
        self.is_finished_ = value
    
    @property
    def is_active(self):
        return self.is_active_
    
    @is_active.setter
    def is_active(self, value: bool):
        self.is_active_ = value

    def start(self) -> Question:
        self.active_question_id = 0
        self.points_ = 0
        question = self.questions_[self.active_question_id]
        return question

    @property
    def nextQuestion(self) -> Question:
        if not self.questions_:
            return None
        self.active_question_id += 1
        if self.active_question_id >= len(self.questions_):
            self.active_question_id = len(self.questions_) - 1
        return self.questions_[self.active_question_id]

    @property
    def previousQuestion(self) -> Question:
        if not self.questions_:
            return None
        self.active_question_id -= 1
        if self.active_question_id < 0:
            self.active_question_id = 0
        return self.questions_[self.active_question_id]

    def end(self) -> int:
        self.active_question_id = 0
        self.is_finished_ = True
        return 0
    
    def reset_questions(self):
        for question in self.questions_:
            question.is_resolved_ = False
            question.user_correct_ = False
        self.is_finished_ = False
        self.points_ = 0
        self.active_question_id = 0
        self.saveInFile()
    
    def addQuestion(self, question):
        self.questions_.append(question)


    def removeQuestion(self, index: int):
        try:
            self.questions_.pop(index)
        except IndexError:
            logger.error(f'Индекс {index} не найден')

    def loadFromFile(self): 
        try:
            filename = self.name_.replace(' ', '_')
            with open(f'{DATA_PATH}/{filename}.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            questions = []
            for q_data in data.get('questions', []):
                question = Question(
                    content=q_data.get('content', ''),
                    correct=q_data.get('correct', False),
                    is_resolved=q_data.get('is_resolved', False),
                    points=q_data.get('points', 0),
                    user_correct=q_data.get('user_correct', False)
                )
                questions.append(question)
            
            return Category(
                name=data.get('name', self.name_),
                is_finished=data.get('is_finished', False),
                is_active=data.get('is_active', False),
                points=data.get('points', 0),
                questions=questions
            )
        except FileNotFoundError as e:
            logger.error(f'Файл не найден')
            return None
        except Exception as e:
            logger.error(f'Ошибка загрузки: {e}')
            return None

    @property
    def toJSON(self):
        questions = []
        for question in self.questions_:
            questions.append(question.toJSON)
        return {
            "name": self.name_,
            "points": self.points_,
            "is_finished": self.is_finished_,
            "is_active": self.is_active_,
            "questions": questions
        }
    
    def saveInFile(self) -> bool:
        data = self.toJSON
        try:
            filename = self.name_.replace(' ', '_')
            with open(f'{DATA_PATH}{filename}.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            logger.error(f'Ошибка сохранения: {e}')
            return False