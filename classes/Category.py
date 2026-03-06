from typing import List

from .Question import Question

class Category:
    name_: str
    points_: int
    questions_: List[Question]
    is_finished_: bool
    is_active_: bool

    def __init__(self, name: str = "", questions: List[Question] = [], 
                 is_finished: bool = False, is_active: bool = False):
        self.name_ = name
        self.points_ = 0
        self.questions_ = questions
        self.is_finished_ = is_finished
        self.is_active_ = is_active

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

    def start(self):
        pass

    def nextQuestion(self):
        pass

    def previousQuestion(self):
        pass

    def end(self) -> int:
        return self.points_
    
    def addQuestion(self, question):
        self.questions_.append(question)

    def removeQuestion(self, index):
        self.questions_.remove(index)

    def loadFromFile(self, filename): 
        pass

    def saveInFile(self, filename):
        pass

    @property
    def toJSON(self):
        questions = []
        for question in self.questions_:
            questions.append(question.toJSON)
        return {
            "name": self.name_,
            "point": self.points_,
            "is_finished": self.is_finished_,
            "is_active": self.is_active_,
            "questions": questions
        }