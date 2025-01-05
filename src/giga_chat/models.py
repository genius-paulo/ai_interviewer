from pydantic import BaseModel


class ChatRequest(BaseModel):
    model: str
    messages: list
    temperature: float = 0.7
    max_tokens: int = 100
    top_p: float = 1.0
    frequency_penalty: float = 0.0


class MiddlePythonInterviewerChat(BaseModel):
    context_questions: str = ("Ты опытный Senior Python-разработчик. "
                              "Пользователь — кандидат на позицию «Middle Python-разработчик». "
                              "Ты проводишь собеседование. "
                              "Задай 1 вопрос на проверку навыков Python уровня Middle и оцени ответ."
                              "\n Проверять нужно навык: {skill}.")
    skill: None | str = None
    make_action: str = "Задай вопрос собеседнику"
    question: None | str = None
    user_answer: str = ("Кандидат ответил так: «{answer}». Оцени ответ в следующем формате:"
                        "\n1. Обязательно оставь баллы за ответ в формате «Оценка: 1/10», "
                        "где 1 — ответ не соответствует вопросу или содержит непонятные символы вместо ответа, "
                        "10 — ответ хорош для Middle Python-разработчика. "
                        "Если ответ не соответствует вопросу, напиши «Оценка: 1/10. Может попробуем другой вопрос?», "
                        "не продолжай диалог и не задавай других вопросов."
                        "\n2. Плюсы и минусы ответа."
                        "\n3. Какие навыки затрагивает понимание заданного вопроса.")
    score: int = 0
