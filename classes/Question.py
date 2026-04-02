
# 
class Question:
    content_: str
    correct_: bool
    is_resolved_: bool
    points_: int
    user_correct_: bool
    
    def __init__(self, content: str = "", correct: bool = False, 
                 is_resolved: bool = False, points: int = 0, user_correct: bool = False):
        self.content_ = content
        self.correct_ = correct
        self.is_resolved_ = is_resolved
        self.points_ = points
        self.user_correct_ = user_correct
    
    @property # Декоратор/геттер, получение значения content_
    def content(self):
        return self.content_
    
    @content.setter # Устанавливает значение для content
    def content(self, value: str):
        self.content_ = value

    @property # Декоратор/геттер, получение значения correct_
    def is_correct(self):
        return self.correct_
    
    @is_correct.setter 
    def is_correct(self, value: bool):
        self.correct_ = value    
    
    @property # Декоратор/геттер, получение значения is_resolved_
    def is_resolved(self):
        return self.is_resolved_
    
    @is_resolved.setter
    def is_resolved(self, value: bool):
        self.is_resolved_ = value

    @property # Декоратор/геттер, получение значения points_
    def points(self):
        return self.points_
    
    @points.setter
    def points(self, value: int):
        self.points_ = value

    @property
    def toJSON(self):
        return {
            "content": self.content_, 
            "correct": self.correct_,
            "is_resolved": self.is_resolved_,
            "points": self.points_,
            "user_correct": self.user_correct_
        }
