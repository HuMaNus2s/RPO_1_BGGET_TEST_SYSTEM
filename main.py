from config.log_config import logger

from classes.Category import Category
from classes.Question import Question


question1 = Question("Никита натурал?", correct=False, is_resolved=True, points=10)
question2 = Question("Никита2 натурал?", correct=False, is_resolved=True, points=10)
question3 = Question("Роберт натурал?", correct=False, is_resolved=False, points=13)
question4 = Question("Роберт2 натурал?", correct=False, is_resolved=False, points=13)
question5 = Question("Данил натурал?", correct=True, is_resolved=True, points=17)
question6 = Question("Данил2 натурал?", correct=True, is_resolved=True, points=17)
question7 = Question("Ильдар натурал?", correct=True, is_resolved=False, points=5)
question8 = Question("Ильдар2 натурал?", correct=True, is_resolved=False, points=5)

category = Category()

category.name = "Натуральность"
category.is_finished = True
category.is_active = False

category.addQuestion(question1)
category.addQuestion(question2)
category.addQuestion(question3)
category.addQuestion(question4)
category.addQuestion(question5)
category.addQuestion(question6)
category.addQuestion(question7)
category.addQuestion(question8)

category.saveInFile()

data_category = category.loadFromFile()

logger.info(data_category.toJSON)

logger.info("\n\n\n\n\n")
question = category.start()
logger.info(f"0: {question.toJSON}")

logger.info(f"9: {category.previousQuestion.toJSON}")
logger.info(f"1: {category.nextQuestion.toJSON}")
logger.info(f"2: {category.nextQuestion.toJSON}")
logger.info(f"3: {category.nextQuestion.toJSON}")
logger.info(f"4: {category.nextQuestion.toJSON}")
logger.info(f"5: {category.nextQuestion.toJSON}")
logger.info(f"6: {category.nextQuestion.toJSON}")
logger.info(f"7: {category.nextQuestion.toJSON}")
logger.info(f"8: {category.nextQuestion.toJSON}")
logger.info(f"9: {category.nextQuestion.toJSON}")
logger.info(f"10: {category.nextQuestion.toJSON}")
logger.info(f"9: {category.previousQuestion.toJSON}")

logger.info(category.points)
logger.info(category.end())