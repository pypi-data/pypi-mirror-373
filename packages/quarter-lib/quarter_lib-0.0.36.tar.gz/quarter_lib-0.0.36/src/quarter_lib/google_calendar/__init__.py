import json
from datetime import datetime, timedelta

import pytz
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from loguru import logger
from quarter_lib.akeyless import get_secrets

from ..logging import setup_logging

logger = setup_logging(__file__)

SCOPES = [
    "https://www.googleapis.com/auth/calendar",
]

DEFAULT_GERMAN_OFFSET = 7200
GOOGLE_TOKEN = get_secrets("google/token.json")



def build_calendar_service():
    creds = Credentials.from_authorized_user_info(GOOGLE_TOKEN, SCOPES)
    return build("calendar", "v3", credentials=creds)

def timezone_from_datetime(dt: datetime):
    offset_in_seconds = dt.tzinfo.utcoffset(dt).seconds
    if offset_in_seconds == DEFAULT_GERMAN_OFFSET:
        return "Europe/Berlin"
    else:
        utc_offset = timedelta(seconds=offset_in_seconds)
        now = datetime.now(pytz.utc)
        return [
            tz.zone for tz in map(pytz.timezone, pytz.all_timezones_set) if now.astimezone(tz).utcoffset() == utc_offset
        ][0]

def add_event_to_calendar(summary, start: datetime, end: datetime):
    desc = {"start": start.strftime("%Y-%m-%dT%H:%M:%S%z"), "end": end.strftime("%Y-%m-%dT%H:%M:%S%z"), "app": summary}
    event = {
        "summary": summary,
        "description": json.dumps(desc, indent=4),
        "start": {
            "dateTime": start.strftime("%Y-%m-%dT%H:%M:%S"),
            "timeZone": timezone_from_datetime(start),
        },
        "end": {
            "dateTime": end.strftime("%Y-%m-%dT%H:%M:%S"),
            "timeZone": timezone_from_datetime(end),
        },
    }
    service = build_calendar_service()
    event = (
        service.events().insert(calendarId="8j088igutfd3bkcant6at54d9g@group.calendar.google.com", body=event).execute()
    )
    logger.info("Event created: %s" % (event.get("htmlLink")))

def get_dict(calendar_service):
    calendar_dict = {}
    page_token = None
    while True:
        calendar_list = calendar_service.calendarList().list(pageToken=page_token).execute()
        for calendar_list_entry in calendar_list["items"]:
            calendar_dict[calendar_list_entry["summary"]] = calendar_list_entry
        page_token = calendar_list.get("nextPageToken")
        if not page_token:
            break
    return calendar_dict

def get_events_from_calendar(calendar_name, calendar_dict, calendar_service):
    event_list = []
    page_token = None
    while True:
        events = (
            calendar_service.events()
            .list(
                calendarId=calendar_dict[calendar_name]["id"],
                pageToken=page_token,
            )
            .execute()
        )
        for event in events["items"]:
            event_list.append(event)
        page_token = events.get("nextPageToken")
        if not page_token:
            break
    return event_list
