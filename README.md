# PC Assembly System - SQLite

## Установка
```bash
pip install sqlalchemy bcrypt pytest
```

## Инициализация БД
```bash
sqlite3 pc_assembly.db < server/schema.sql
```

## Запуск
```bash
# Сервер
python server/main.py

# Клиент (другое окно)
python client/main.py
```

## Тесты
```bash
pytest tests/ -v
```