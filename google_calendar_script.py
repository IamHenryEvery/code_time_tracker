import os.path
import threading
import time

import arrow
import psutil
import pystray
import win32gui
import win32process
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from loguru import logger
from PIL import Image


def enum_windows_callback(hwnd, processes_with_windows: set):
    """Колбек функция для добавления названия процессов с окнами в множество

    Args:
        hwnd: Идентификатор окна
        processes_with_windows (set): Множество процессов с открытыми окнами
    """
    try:
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        process_name = get_process_name_by_pid(pid)
        if process_name:
            processes_with_windows.add(process_name)
    except (
        psutil.NoSuchProcess,
        psutil.AccessDenied,
        psutil.ZombieProcess,
    ):
        pass


def get_processes_with_windows() -> set[str]:
    """Функция для создания множества названий процессов с открытыми окнами

    Returns:
        set[str]: Множество процессов с открытыми окнами
    """
    processes_with_windows = set()
    win32gui.EnumWindows(enum_windows_callback, processes_with_windows)
    return processes_with_windows


def get_process_name_by_pid(pid: int) -> str:
    """Фукнция для определения названия процесса по его идентификатору

    Args:
        pid (int): Идентификатор процесса

    Returns:
        str: Название процесса
    """
    try:
        process = psutil.Process(pid)
        return process.name().lower()
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        return ""


def is_programming(processes_with_windows: set[str]) -> bool:
    """Фукнция, которая определяет, открыт ли VsCode или PyCharm

    Args:
        processes_with_windows (set[str]): Множество процессов с открытыми
        окнами

    Returns:
        bool: True, если открыт VsCode или PyCharm
        False, если нет
    """
    return (
        "code.exe" in processes_with_windows
        or "pycharm64.exe" in processes_with_windows
    )


def connect_to_calendar():
    """Функция для подключения к Google календарю, используя учетные данные
    из файла credentials.json и/или токен из файла token.json

    Returns:
        service: Сервис для поключения к API Google календаря
    """
    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    service = build("calendar", "v3", credentials=creds)
    logger.info("Подключение к календарю установлено")
    return service



def on_exit(icon, item):
    icon.stop()


def run_tray_icon():
    icon.run()


def add_calendar_event(stop_event):
    """Главная функция для добавления событий в календарь

    Args:
        service: Сервис для поключения к API Google календаря
    """

    preriod_started = True
    count_periods = 0
    start = arrow.now()
    while not stop_event.is_set():
        prog_state = is_programming(get_processes_with_windows())
        if not prog_state and preriod_started:
            end = arrow.now()
            if (end - start).seconds > 120:
                event = {
                    "summary": "Программирование",
                    "start": {"dateTime": start.isoformat()},
                    "end": {"dateTime": end.isoformat()},
                }
                event = (
                    service.events()
                    .insert(calendarId="primary", body=event)
                    .execute()
                )
                logger.success(
                    f"Событие создано: {event.get('htmlLink')}.\
                            Время: с {start} до {end}"
                )
                count_periods += 1
            preriod_started = False
        elif prog_state and (not preriod_started):
            start = arrow.now()
            preriod_started = True
        time.sleep(10)
    logger.info("Скрипт завершен")


if __name__ == "__main__":
    SCOPES = ["https://www.googleapis.com/auth/calendar"]
    logger.remove()
    logger.add(
        sink="logs.txt",
        format="<level>{time:MMMM D, YYYY HH:mm:ss} {level} --- {message}</level>",
        colorize=True,
    )
    logger.level("INFO", color="<cyan>")
    logger.level("SUCCESS", color="<green>")

    icon_image = Image.open("icon.png")
    menu = pystray.Menu(pystray.MenuItem("Выход", on_exit))
    icon = pystray.Icon(
        "name",
        icon_image,
        "Скрипт для контроля времени за программированием",
        menu,
    )
    stop_event = threading.Event()

    service = connect_to_calendar()
    logger.info("Скрипт запущен")

    tray_thread = threading.Thread(target=run_tray_icon, daemon=True)
    tray_thread.start()

    event_thread = threading.Thread(
        target=add_calendar_event, args=(stop_event,), daemon=True
    )
    event_thread.start()

    try:
        tray_thread.join()
    finally:
        stop_event.set()
        event_thread.join()
