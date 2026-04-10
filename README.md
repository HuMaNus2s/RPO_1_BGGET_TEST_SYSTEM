# Система Тестирования

BGGET - веб-приложение для прохождения тестов по категориям с системой баллов и учётом результатов пользователей.

---

## Содержание

- [Возможности](#-возможности)
- [Требования](#-требования)
- [Установка](#-установка)
- [Настройка](#-настройка)
- [Запуск](#-запуск)
- [Структура проекта](#-структура-проекта)
- [Использование](#-использование)
- [Пример users.json](#-пример-usersjson)
- [Troubleshooting](#-troubleshooting)

---

## Возможности

- **Авторизация пользователей** с разными ролями (user/admin)
- **Категории вопросов** с загрузкой из JSON-файлов
- **Вопросы формата Да/Нет** с мгновенной проверкой
- **Система баллов** с сохранением в профиле пользователя
- **Экран результатов** после завершения категории
- **Автосохранение** прогресса в файлах
- **Адаптивный дизайн** с анимациями

---

## Требования

- Python 3.8 или выше
- pip (менеджер пакетов Python)
- Веб-браузер (Chrome, Firefox, Edge)

---

## Установка

### 1. Клонируйте репозиторий

```bash
git clone <URL_ВАШЕГО_РЕПОЗИТОРИЯ>
cd <ИМЯ_ПАПКИ_ПРОЕКТА>
```

### 2. Создайте виртуальное окружение

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Установите зависимости

```bash
pip install -r requirements.txt
```

### 4. Создайте необходимые папки

```bash
mkdir -p data/users
mkdir -p static/css
mkdir -p static/js
mkdir -p pages
mkdir -p config
mkdir -p classes
mkdir -p managers
```

---

## Настройка

### 1. Создайте файл конфигурации `config/config.py`

```python
# config/config.py
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, 'data', '')

class web:
    SECRET_KEY = 'ваш-секретный-ключ-здесь'
    DEBUG = True
```

### 2. Создайте файл логирования `config/log_config.py`

```python
# config/log_config.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('test_system')
```

### 3. Создайте файл пользователей `data/users/users.json`

```json
{
  "users": [
    {
      "username": "admin",
      "password": "admin123",
      "role": "admin",
      "points": 0
    },
    {
      "username": "user",
      "password": "user123",
      "role": "user",
      "points": 0
    }
  ]
}
```

### 4. Создайте категории вопросов

Пример: `data/Вопросы.json`

```json
{
  "name": "Вопросы",
  "points": 0,
  "is_finished": false,
  "is_active": true,
  "questions": [
    {
      "content": "Это вопрос?",
      "correct": true,
      "is_resolved": false,
      "points": 10
    },
    {
      "content": "Это ещё один вопрос?",
      "correct": false,
      "is_resolved": false,
      "points": 5
    }
  ]
}
```

---

## ▶️ Запуск

```bash
venv\Scripts\activate

python main.py
```

Откройте в браузере: **http://127.0.0.1:5000**

---

## Структура проекта

```
project/
├── app.py                      # Главный файл приложения
├── requirements.txt            # Зависимости Python
├── README.md                   # Этот файл
├── app.log                     # Файл логов (создаётся автоматически)
│
├── config/
│   ├── __init__.py
│   ├── config.py               # Конфигурация проекта
│   └── log_config.py           # Настройка логирования
│
├── classes/
│   ├── __init__.py
│   ├── Category.py             # Класс категории
│   └── Question.py             # Класс вопроса
│
├── managers/
│   ├── __init__.py
│   └── CategoryManager.py      # Менеджер категорий
│
├── data/
│   ├── users/
│   │   └── users.json          # Пользователи системы
│   ├── *.json                  # Файлы категорий вопросов
│   └── ...
│
├── pages/                      # HTML шаблоны
│   ├── index.html              # Главная страница
│   └── category.html           # Страница категории
│
└── static/
    ├── css/
    │   └── styles.css          # Стили приложения
    └── js/
        ├── main.js             # Скрипты главной страницы
        └── category.js         # Скрипты страницы категории
```

---

## Использование

### Для пользователя:

1. **Войдите в систему** (введите username и password из `users.json`)
2. **Выберите категорию** из списка доступных
3. **Отвечайте на вопросы** (Да/Нет)
4. **Получите результат** после завершения категории
5. **Вернитесь в меню** для выбора другой категории

### Для администратора:

- Доступ к маршруту `/admin`
- Возможность добавлять/изменять категории через редактирование JSON-файлов.
- Просмотр статистики пользователей в `data/users/users.json`

---

## Пример `requirements.txt`

```txt
Flask
```

---

## Troubleshooting

### Ошибка: `ModuleNotFoundError: No module named 'config'`

**Решение:** Убедитесь, что в папке `config/` есть файл `__init__.py` (может быть пустым).

### Ошибка: `FileNotFoundError: users.json`

**Решение:** Создайте файл `data/users/users.json` с хотя бы одним пользователем.

### Ошибка: `The view function did not return a valid response`

**Решение:** Проверьте, что все маршруты Flask заканчиваются оператором `return`.

### Ошибка: `CORS Policy` в браузере

**Решение:** Открывайте сайт через адрес Flask (http://127.0.0.1:5000), а не как файл.

### Баллы не сохраняются

**Решение:**
1. Проверьте права доступа к папке `data/`
2. Убедитесь, что в `users.json` есть поле `points` у пользователя
3. Проверьте логи в `app.log`

---

## Авторы

Газимянов Ильдар, Гладченко Никита, Тозлян Роберт