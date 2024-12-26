from pydantic import BaseModel


class ChatRequest(BaseModel):
    model: str
    messages: list
    temperature: float = 0.7
    max_tokens: int = 100
    top_p: float = 1.0
    frequency_penalty: float = 0.0


class MiddlePythonInterviewerChat(BaseModel):
    context_questions: str = ("Ты опытный Senior Python-разработчик. Твоя задача — провести собеседование с "
                              "кандидатом на позицию Middle Python-разработчика. Задай вопрос средней сложности на "
                              "проверку"
                              "навыков Python уровня Middle и оцени ответ.\n\nОценку ответа пришли в следующем "
                              "формате:\n1."
                              "Баллы за ответ в формате 1/10, где 1 — ответ не соответствует вопросу или ответа "
                              "вообще не было, 10 — ответ хорош для Middle Python-разработчика.\n2. Плюсы и "
                              "минусы ответа.\n3. Какие навыки затрагивает понимание заданного вопроса.\nЕсли ответ "
                              "вообще не соответствует вопросу, оцени ответ на 1/10 и предложи "
                              f"запросить еще вопрос.")
    make_action: str = "Сгенерируй вопрос"
    question: None | str = None
    user_answer: None | str = None
