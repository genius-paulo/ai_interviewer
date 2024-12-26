# Используем официальный образ Python в качестве базового образа
FROM python:3.10-bookworm

ADD src /usr/src/ai_interviwer/src

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /usr/src/ai_interviwer/

COPY poetry.lock pyproject.toml ./

ENV PYTHONPATH=/usr/src/ai_interviwer/

RUN pip --no-cache-dir install poetry

RUN poetry export --without-hashes -f requirements.txt -o requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

RUN curl -k "https://gu-st.ru/content/Other/doc/russian_trusted_root_ca.cer" -w "\n" >> $(python -m certifi)