import os.path

import arrow
import win32gui
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def get_active_window_title():
    hwnd = win32gui.GetForegroundWindow()
    title = win32gui.GetWindowText(hwnd)
    return title


def is_vscode_focused():
    title = get_active_window_title()
    return "Visual Studio Code" in title


SCOPES = ["https://www.googleapis.com/auth/calendar"]


def main():
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

    try:
        service = build("calendar", "v3", credentials=creds)
        start = arrow.now().shift(hours=-5).isoformat()
        end = arrow.now().shift(hours=-2).isoformat()
        event = {
            "summary": "Created via API event",
            "start": {"dateTime": start},
            "end": {"dateTime": end},
        }
        event = (
            service.events().insert(calendarId="primary", body=event).execute()
        )
        print(f"Event created: {event.get('htmlLink')}")
    except HttpError as error:
        print(f"An error occurred: {error}")


if __name__ == "__main__":
    main()
