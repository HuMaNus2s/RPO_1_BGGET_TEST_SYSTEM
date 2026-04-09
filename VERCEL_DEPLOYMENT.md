# Развертывание на Vercel

## Подготовка

1. **Установка зависимостей**
   ```bash
   npm install
   pip install -r requirements.txt
   ```

2. **Создание необходимых файлов**
   ```bash
   mkdir -p data/users
   ```

3. **Создание файла пользователей**
   ```json
   {
     "users": [
       {
         "username": "admin",
         "password": "admin",
         "role": "admin",
         "points": 0
       }
     ]
   }
   ```

## Развертывание

### 1. Ручное развертывание через веб-интерфейс

1. **Перейдите на сайт Vercel:**
   ```
   https://vercel.com
   ```

2. **Войдите или зарегистрируйтесь:**
   - Нажмите "Sign Up" или "Log In"
   - Выберите способ входа (GitHub, GitLab, Bitbucket или email)

3. **Импортируйте проект:**
   - Нажмите "Import Project"
   - Выберите "From Git Repository"
   - Подключите ваш репозиторий (GitHub, GitLab или Bitbucket)

4. **Настройте проект:**
   - Выберите папку с проектом
   - Установите "Framework Preset" в "Other"
   - Добавьте переменные окружения:
     - `PYTHON_API_URL` = `http://localhost:5000` (или ваш URL)
   - Нажмите "Deploy"

5. **Дождитесь завершения развертывания**

### 2. Альтернативный способ - через CLI (если установлен)
```bash
npm i -g vercel
vercel login
vercel --prod
```

### 3. Настройка переменных окружения
В Vercel необходимо настроить переменные окружения:
- `PYTHON_API_URL` - URL Python-сервера (например, `http://localhost:5000`)

## Локальная разработка

### Запуск Python-сервера
```bash
python run.py
```

### Запуск через Docker
```bash
docker build -t rpo-test-system .
docker run -p 5000:5000 rpo-test-system
```

## Структура проекта для Vercel

- `package.json` - Зависимости Node.js
- `vercel.json` - Конфигурация Vercel
- `server.js` - Прокси-сервер
- `Dockerfile` - Контейнеризация
- `run.py` - Production-режим Flask