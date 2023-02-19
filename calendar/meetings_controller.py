from __future__ import print_function

import datetime
import os.path
from uuid import uuid4
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']


class Google_controller:
    def __init__(self):
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        try:
            self.service = build('calendar', 'v3', credentials=creds)
        except HttpError as error:
            print('An error occurred: %s' % error)

    @staticmethod
    def generate_event_body(title, description, date, person1, person2):
        hours, minutes = int(date.split(':')[0]), int(date.split(':')[1])
        dateISO = datetime.datetime(2022, 3, 10, hours, minutes).isoformat()

        event = {
            'summary': title,
            'description': description,
            "conferenceData": {"createRequest": {"requestId": f"{uuid4().hex}",
                                                 "conferenceSolutionKey": {"type": "hangoutsMeet"}}},
            'start': {
                'dateTime': dateISO,
                'timeZone': "Europe/Moscow"
            },
            'end': {
                'dateTime': dateISO,
                'timeZone': "Europe/Moscow"
            },
            'attendees': [
                {'email': person1},
                {'email': person2},
            ],
            'reminders': {
                'useDefault': True,
            },
        }
        return event

    def new_event(self, event):
        try:
            self.event = self.service.events().insert(calendarId='primary', sendNotifications=True, body=event,
                                                      conferenceDataVersion=1).execute()
            return self.event.get('htmlLink')

        except HttpError as error:
            print('An error occurred: %s' % error)

    def print_events(self):
        try:
            now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
            print('Getting the upcoming 10 events')
            events_result = self.service.events().list(calendarId='primary', timeMin=now,
                                                       maxResults=10, singleEvents=True,
                                                       orderBy='startTime').execute()
            events = events_result.get('items', [])

            if not events:
                print('No upcoming events found.')
                return

            # Prints the start and name of the next 10 events
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                print(start, event['summary'])

        except HttpError as error:
            print('An error occurred: %s' % error)


if __name__ == '__main__':
    gc = Google_controller()
    r = gc.generate_event_body('Пробное собеседование между Иваном и иваном', 'Это пробное собес', '11:45',
                               'ivannewest@gmail.com', 'ivanthesmartest@gmail.com')
    gc.new_event(r)
