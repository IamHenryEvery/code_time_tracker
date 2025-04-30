# Track Coding Time

## Описание

Этот проект представляет собой скрипт на Python, который отслеживает время, проведенное в Visual Studio Code (VSCode) и\или PyCharm, и добавляет это время в ваш Google Calendar. Скрипт работает в фоновом режиме и автоматически завершает отслеживание времени при закрытии иконки. Логи работы скрипта сохраняются в файл `logs.txt`

## Установка

1. **Создайте виртуальное окружение:**

    ```bash
    python -m venv venv
    ```

2. **Активируйте виртуальное окружение:**

    **Windows:**

    ```bash
    .\venv\Scripts\activate
    ```

    **macOS/Linux:**

    ```bash
    source venv/bin/activate
    ```

3. **Установите необходимые библиотеки:**

    ```bash
    pip install pywin32 psutil google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client arrow pillow pystray loguru
    ```

4. **Скачайте файл `credentials.json` из Google Cloud Console:**

    - Перейдите в [Google Cloud Console](https://console.cloud.google.com/).
    - Создайте проект и включите Google Calendar API.
    - Создайте учетные данные OAuth 2.0 и скачайте файл `credentials.json`.

5. **Добавьте свою учетную запись Google в список тестировщиков:**

    - Перейдите в раздел "API и сервисы" -> "Консоль OAuth 2.0".
    - В разделе "Тестовые пользователи" добавьте свою учетную запись Google.

## Запуск

1. **Запуск скрипта:**
	```bash
	uv run google_calendar_script.py
	```
	Для удобства можно добавить его в автозагрузку. Для этого надо создать .bat файл со следующим содержимым:
	```bash
	@echo off
	"Путь до интерпретора в виртуальном окружении" "Путь до файла google_calendar_script.py"
	```
2. **Скрипт будет работать в фоновом режиме и отслеживать время, проведенное в VSCode и\или PyCharm.**

