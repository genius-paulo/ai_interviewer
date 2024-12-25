import certifi
from gigachat import GigaChat


# TODO: Нужно создать модель запроса и сделать метод отправки запроса внутри класса интервьюера

class AIInterviewer:
    def __init__(self, api_token):
        self.model = GigaChat(
            credentials=api_token,
            ca_bundle_file=certifi.where(),
            scope="GIGACHAT_API_PERS",
            model="GigaChat",
        )
