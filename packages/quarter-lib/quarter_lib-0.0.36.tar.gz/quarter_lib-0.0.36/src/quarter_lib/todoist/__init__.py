import uuid
from datetime import timedelta, time, datetime
from typing import Dict
from urllib.parse import urljoin

import pandas as pd
import requests
from dateutil import parser
from todoist_api_python.api import TodoistAPI

from ..akeyless import get_secrets
from ..logging import setup_logging

logger = setup_logging(__file__)

TODOIST_TOKEN = get_secrets("todoist/token")

END_TIME = time(hour=6, minute=0, second=0)
TODOIST_API = TodoistAPI(TODOIST_TOKEN)

CONTENT_TYPE = ("Content-Type", "application/json; charset=utf-8")
AUTHORIZATION = ("Authorization", "Bearer %s")
X_REQUEST_ID = ("X-Request-Id", "%s")

BASE_URL = "https://api.todoist.com"
AUTH_BASE_URL = "https://todoist.com"
SYNC_VERSION = "v9"
REST_VERSION = "v2"

SYNC_API = urljoin(BASE_URL, f"/sync/{SYNC_VERSION}/")
REST_API = urljoin(BASE_URL, f"/rest/{REST_VERSION}/")

TASKS_ENDPOINT = "tasks"
PROJECTS_ENDPOINT = "projects"
COLLABORATORS_ENDPOINT = "collaborators"
SECTIONS_ENDPOINT = "sections"
COMMENTS_ENDPOINT = "comments"
LABELS_ENDPOINT = "labels"
SHARED_LABELS_ENDPOINT = "labels/shared"
SHARED_LABELS_RENAME_ENDPOINT = f"{SHARED_LABELS_ENDPOINT}/rename"
SHARED_LABELS_REMOVE_ENDPOINT = f"{SHARED_LABELS_ENDPOINT}/remove"
QUICK_ADD_ENDPOINT = "quick/add"

AUTHORIZE_ENDPOINT = "oauth/authorize"
TOKEN_ENDPOINT = "oauth/access_token"
REVOKE_TOKEN_ENDPOINT = "access_tokens/revoke"

def get_rest_url(relative_path: str) -> str:
    return urljoin(REST_API, relative_path)

def get_sync_url(relative_path: str) -> str:
    return urljoin(SYNC_API, relative_path)

def get_auth_url(relative_path: str) -> str:
    return urljoin(AUTH_BASE_URL, relative_path)

def create_headers(
    token: str | None = None,
    with_content: bool = False,
    request_id: str | None = None,
) -> Dict[str, str]:
    headers: Dict[str, str] = {}

    if token:
        headers.update([(AUTHORIZATION[0], AUTHORIZATION[1] % token)])
    if with_content:
        headers.update([CONTENT_TYPE])
    if request_id:
        headers.update([(X_REQUEST_ID[0], X_REQUEST_ID[1] % request_id)])

    return headers

HEADERS = create_headers(TODOIST_TOKEN)

def get_activity(**kwargs):
    return requests.post(get_sync_url("activity/get"), headers=HEADERS, data=kwargs).json()

def run_sync_commands(commands):
    return requests.post(
        get_sync_url("sync"),
        headers=HEADERS,
        json={"commands": commands},
    )

def get_user_state():
    return requests.post(
        get_sync_url("sync"), headers=HEADERS, json={"sync_token": "*", "resource_types": ["user"]}
    ).json()["user"]["tz_info"]

def get_user_karma_vacation():
    return requests.post(
        get_sync_url("sync"), headers=HEADERS, json={"sync_token": "*", "resource_types": ["user"]}
    ).json()["user"]["features"]["karma_vacation"]

def upload_file(file_path):
    return requests.post(
        get_sync_url("uploads/add"),
        headers=HEADERS,
        files={
            "file": open(file_path, "rb"),
        },
    ).json()

def add_note_with_attachement(task_id, file_path):
    file = upload_file(file_path)
    return requests.post(
        get_sync_url("sync"),
        headers=HEADERS,
        json={
            "commands": [
                {
                    "type": "note_add",
                    "temp_id": str(uuid.uuid4()),
                    "uuid": str(uuid.uuid4()),
                    "args": {
                        "item_id": task_id,
                        "content": "",
                        "file_attachment": {
                            "file_name": file["file_name"],
                            "file_size": file["file_size"],
                            "file_type": file["file_type"],
                            "file_url": file["file_url"],
                            "resource_type": "audio",
                        },
                    },
                },
            ]
        },
    ).json()

def add_note_with_attachement_and_content(task_id, content, file_path):
    """Enhanced version from todoist_notes module"""
    file = upload_file(file_path)
    return requests.post(
        get_sync_url("sync"),
        headers=HEADERS,
        json={
            "commands": [
                {
                    "type": "note_add",
                    "temp_id": str(uuid.uuid4()),
                    "uuid": str(uuid.uuid4()),
                    "args": {
                        "item_id": task_id,
                        "content": content,
                        "file_attachment": {"file_url": file["file_url"]},
                    },
                }
            ]
        },
    ).json()

def add_task_to_todoist(task, project_id, description=None):
    """Enhanced task creation from todoist_notes module"""
    command = {
        "type": "item_add",
        "temp_id": str(uuid.uuid4()),
        "uuid": str(uuid.uuid4()),
        "args": {
            "content": task,
            "project_id": project_id,
        },
    }
    if description:
        command["args"]["description"] = description
    return requests.post(
        get_sync_url("sync"),
        headers=HEADERS,
        json={"commands": [command]},
    ).json()

def update_due(task_id, due, add_reminder=False):
    commands = [
        {
            "type": "item_update",
            "uuid": str(uuid.uuid4()),
            "args": {
                "id": task_id,
                "due": due,
            },
        }
    ]
    if add_reminder:
        commands.append(
            {
                "type": "reminder_add",
                "temp_id": str(uuid.uuid4()),
                "uuid": str(uuid.uuid4()),
                "args": {
                    "item_id": task_id,
                    "due": due,
                },
            }
        )
    return requests.post(
        get_sync_url("sync"),
        headers=HEADERS,
        json={"commands": commands},
    ).json()

def add_reminder(task_id, due):
    return requests.post(
        get_sync_url("sync"),
        headers=HEADERS,
        json={
            "commands": [
                {
                    "type": "reminder_add",
                    "temp_id": str(uuid.uuid4()),
                    "uuid": str(uuid.uuid4()),
                    "args": {
                        "item_id": task_id,
                        "due": due,
                    },
                }
            ]
        },
    ).json()

def move_item_to_project(task_id, project_id):
    return requests.post(
        get_sync_url("sync"),
        headers=HEADERS,
        json={
            "commands": [
                {
                    "type": "item_move",
                    "uuid": str(uuid.uuid4()),
                    "args": {
                        "id": task_id,
                        "project_id": project_id,
                    },
                }
            ]
        },
    ).json()

def move_item_to_section(task_id, section_id):
    return requests.post(
        get_sync_url("sync"),
        headers=HEADERS,
        json={
            "commands": [
                {
                    "type": "item_move",
                    "uuid": str(uuid.uuid4()),
                    "args": {
                        "id": task_id,
                        "section_id": section_id,
                    },
                }
            ]
        },
    ).json()

def add_to_todoist(text, project_id=None):
    item = TODOIST_API.add_task(text)
    if project_id:
        move_item_to_project(item.id, project_id)
    return item

def get_default_offset():
    tz_info = get_user_state()
    delta = timedelta(hours=tz_info["hours"], minutes=tz_info["minutes"])
    return delta, tz_info["gmt_string"]

def get_items_by_label(label_id):
    label = TODOIST_API.get_label(label_id)
    return TODOIST_API.get_tasks(label=label.name)

def get_items_by_project(project_id):
    items = TODOIST_API.get_tasks(project_id=project_id)
    return [item for item in items if item.is_completed == False]

async def complete_task_by_title(selected_service):
    df_items = pd.DataFrame([item.__dict__ for item in TODOIST_API.get_tasks()])
    item = df_items[df_items.content == selected_service].sample(1).iloc[0]
    logger.info(item)

    TODOIST_API.close_task(str(item["id"]))
    api_item = TODOIST_API.get_task(str(item["id"]))
    if parser.parse(api_item.due.date).date() >= (datetime.today() + timedelta(days=1)).date():
        due = {
            "date": (datetime.today() + timedelta(days=1)).strftime("%Y-%m-%d"),
            "is_recurring": True,
            "lang": "en",
            "string": "every day",
            "timezone": None,
        }
        update_due(item["id"], due=due)

    if END_TIME > datetime.now().time():
        due = {
            "date": datetime.today().strftime("%Y-%m-%d"),
            "is_recurring": True,
            "lang": "en",
            "string": "every day",
            "timezone": None,
        }
        update_due(item["id"], due=due)
