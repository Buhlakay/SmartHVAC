from __future__ import print_function
import datetime
import time
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

""" Modified from starter code provided from Google developers at 
https://developers.google.com/calendar/quickstart/python """

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


def get_event_list():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=9000)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    # Call the Calendar API
    # now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time

    before = datetime.datetime.utcfromtimestamp(float(datetime.datetime(2019, 4, 28, 0, 0).strftime('%s')))
    before_timestamp = before.isoformat('T') + 'Z'

    after = datetime.datetime.utcfromtimestamp(float(datetime.datetime(2019, 5, 4, 23, 59).strftime('%s')))
    after_timestamp = after.isoformat('T') + 'Z'

    print('Getting events for the upcoming week')
    events_result = service.events().list(calendarId='primary', timeMin=before_timestamp,
                                        timeMax=after_timestamp,
                                        singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])

    event_list = list()
    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        start_date = datetime.datetime.strptime(start, "%Y-%m-%dT%H:%M:%S-04:00")
        # print(start_date)

        end = event['end'].get('dateTime', event['end'].get('date'))
        end_date = datetime.datetime.strptime(end, "%Y-%m-%dT%H:%M:%S-04:00")
        # print(end_date)

        event_list.append([start_date, end_date])
        # print(start, end, event['summary'])
    return event_list


def check_user_event(event_list, event_date):
    for event in event_list:
        if event[0] <= event_date <= event[1]:
            return True
    return False


def main():
    date = datetime.datetime(2019, 4, 16, 19, 30)
    decision = check_user_event(date)
    print(decision)


if __name__ == '__main__':
    main()
