import os.path
import time

import arrow
import psutil
import win32gui
import win32process
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


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
    """Фукнция, которая определит, открыт ли VsCode или PyCharm

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


SCOPES = ["https://www.googleapis.com/auth/calendar"]


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
    return service



def main(service):
    """Главная функция для добавления событий в календарь

    Args:
        service: Сервис для поключения к API Google календаря
    """
    start = arrow.now().isoformat()
    while True:
        # TODO Добавить обработку случая с повторным открытием окна
        if not is_programming(get_processes_with_windows()):
            end = arrow.now().isoformat()
            event = {
                "summary": "Программирование",
                "start": {"dateTime": start},
                "end": {"dateTime": end},
            }
            event = (
                service.events()
                .insert(calendarId="primary", body=event)
                .execute()
            )
            print(f"Event created: {event.get('htmlLink')}")

        time.sleep(60)


if __name__ == "__main__":
    service = connect_to_calendar()
    main(service)
