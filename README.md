AI-помощник для подготовки к интервью Middle Python-разработчика. Работает на основе GigaChat.

### Инструкция для быстрого запуска в контейнере
1. Скачать исходники из репозитория
2. Создать файл `.env` из шаблона `template.env`
3. Запустить `docker compose up --build` для сборки образа 
4. Написать `/get_question` в боте или воспользоваться кнопками

### Инструкция для быстрого запуска локально
1.  Запустить контейнер базы данных:
`docker run --name pg-container -e POSTGRES_DB=inter_db -e POSTGRES_USER=inter_user -e POSTGRES_PASSWORD=inter_password -p 5432:5432 -d postgres:15`