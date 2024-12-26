# Первый этап: сборка зависимостей и создание требований
FROM python:3.10-slim-buster as builder

# Копируем исходный код приложения
WORKDIR /usr/src/ai_interviwer/
COPY src /usr/src/ai_interviwer/src
COPY poetry.lock pyproject.toml .

# Устанавливаем Poetry и экспортируем зависимости в файл requirements.txt
RUN pip install --no-cache-dir poetry \
 && poetry export --without-hashes -f requirements.txt -o requirements.txt

# Второй этап: создание финального образа
FROM python:3.10-slim-buster

# Копируем требования из первого этапа
COPY --from=builder /usr/src/ai_interviwer/requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходники без лишних файлов
COPY src /usr/src/ai_interviwer/src

# Устанавливаем рабочую директорию
WORKDIR /usr/src/ai_interviwer/

# Устанавливаем переменную окружения
ENV PYTHONPATH=/usr/src/ai_interviwer/

# Обновляем систему и устанавливаем curl
RUN apt-get update && apt-get install -y curl

# Загружаем сертификат для взаимодействия с GigaChatAPI
RUN curl -k "https://gu-st.ru/content/Other/doc/russian_trusted_root_ca.cer" -w "\n" >> $(python -m certifi)