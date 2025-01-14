from pydantic import BaseModel
from src.bot.bot_content import skills
from loguru import logger


class MiddlePythonInterviewerChat(BaseModel):
    question: str = None
    context_questions: str = ("Ты Senior Python-разработчик и проводишь собеседование на Middle Python-разработчика. "
                              "Ты задал кандидату вопрос «{question}», ответ на который рекомендуется от 200 "
                              "до 700 символов. Кандидат ответил так: «{answer}». "
                              "Оцени ответ кандидата в следующем формате:"
                              "\n1. «Оценка: 10/10» — оцени ответ от 1 до 10,"
                              "в оценке 2 — ответ плохой; 5 — ответ по теме, но содержит ошибки и неполный; "
                              "10 — ответ по теме, не содержит ошибок, может быть не полным, "
                              "но для Middle Python-разработчика вполне хороший."
                              "\n\n2. Опиши плюсы и минусы ответа."
                              "\n\n3. Опиши навыки, которые затрагивает понимание заданного вопроса. "
                              "В ответе не используй знаки форматирования текста. "
                              "Чаще ставь 10/10 и хвали кандидата, если он заслуживает."
                              "Если ответ не соответствует вопросу или он полностью неверный, "
                              "напиши «Оценка: 1/10. Попробуем другой вопрос?», "
                              "не продолжай диалог и не задавай других вопросов.")
    answer: str = None
    skill: skills.Skills = None
    score: float = 0
    help_answer: str = ("Ты Senior Python-разработчик и проводишь собеседование на Middle Python-разработчика. "
                        "Ты задал кандидату вопрос «{question}» и собираешься оценить его по 10-бальной шкале."
                        "Расскажи правильный ответ на вопрос так, чтобы он заслужил оценку 10/10. "
                        "Постарайся ответить кратко и уложиться в 1000 символов.")

    def get_final_prompt(self) -> str:
        if self.question is None or self.answer is None:
            raise AttributeError
        else:
            return self.context_questions.format(question=self.question, answer=self.answer)


if __name__ == '__main__':
    history_chat = MiddlePythonInterviewerChat(question='Вот такой вопрос', answer='Вот такой ответ')
    print(history_chat.get_final_prompt())
