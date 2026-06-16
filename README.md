# Система сборки компьютеров на заказ (PC Assembly System)

## Описание
Информационная система для автоматизации процессов сборки компьютеров на заказ. Клиент-серверное приложение с TCP-протоколом, поддержкой ORM и Raw SQL, авторизацией с bcrypt.

## Структура проекта
```
PCAssemblyApp/
├── server/           # Серверная часть (Python 3.14)
│   ├── repositories/ # Repository Pattern (ORM + SQL)
│   ├── main.py       # TCP-сервер
│   ├── auth.py       # Авторизация с bcrypt
│   ├── database.py   # Подключение к PostgreSQL
│   ├── factory.py    # Factory Pattern
│   ├── models.py     # SQLAlchemy ORM модели
│   └── schema.sql    # Схема БД
├── client/           # Клиентская часть (Tkinter)
│   └── main.py       # GUI приложение
├── tests/            # Модульные тесты (pytest)
│   ├── conftest.py   # Фикстуры
│   ├── test_auth.py  # Тесты авторизации
│   └── test_repositories.py # Тесты CRUD
└── docs/             # Документация и диаграммы
    ├── diagrams/     # IDEF0, IDEF3, DFD, UML, ER
    └── screenshots/  # Скриншоты тестов
```

## Установка

```bash
# Клонирование
git clone <repo_url>
cd PCAssemblyApp

# Создание виртуального окружения
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate   # Windows

# Установка зависимостей
pip install sqlalchemy psycopg2-binary bcrypt pytest

# Настройка PostgreSQL
# 1. Создать БД: createdb pc_assembly
# 2. Выполнить: psql pc_assembly < server/schema.sql
```

## Запуск

```bash
# Сервер
python server/main.py

# Клиент (в новом терминале)
python client/main.py
```

## Тестирование

```bash
pytest tests/ -v
```

## Технологический стек
| Компонент | Технология |
|-----------|-----------|
| Сервер | Python 3.14 |
| БД | SQLite |
| ORM | SQLAlchemy 2.x |
| Raw SQL | psycopg2-binary |
| GUI | Tkinter |
| Хеширование | bcrypt |
| Тесты | pytest |
| Диаграммы | Draw.io |

## Паттерны проектирования
- **Repository** — абстракция доступа к данным
- **Strategy** — переключение ORM/SQL
- **Factory** — создание репозиториев

## Git-репозиторий
```bash
git init
git checkout -b develop
git add .
git commit -m "Initial commit"
git checkout -b feature/auth
# ... разработка ...
git merge feature/auth
```
