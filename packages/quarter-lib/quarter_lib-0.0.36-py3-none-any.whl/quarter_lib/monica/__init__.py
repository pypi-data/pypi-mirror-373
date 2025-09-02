from datetime import datetime
from uuid import uuid4

import pymysql.cursors

from ..database.mysql import (
    close_server_connection,
    create_monica_server_connection,
)
from ..todoist import get_default_offset
from ..logging import setup_logging

logger = setup_logging(__file__)

DEFAULT_ACCOUNT_ID = 1
INBOX_CONTACT_ID = 52
MICROJOURNAL_CONTACT_ID = 58

def add_to_journal(recognized_text, date, context="Meditation"):
    _, delta_str = get_default_offset()
    connection = create_monica_server_connection()
    try:
        with connection.cursor() as cursor:
            title = "{timestamp} - Im Kontext: {context}".format(timestamp=date.strftime("%H:%M:%S") + delta_str, context=context)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            happened_at = date.strftime("%Y-%m-%d")
            activities_values = tuple(
                (
                    uuid4(),
                    DEFAULT_ACCOUNT_ID,
                    title,
                    recognized_text,
                    happened_at,
                    timestamp,
                    timestamp,
                )
            )
            cursor.execute(
                "INSERT INTO activities (uuid, account_id, summary, description, happened_at, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                activities_values,
            )
            connection.commit()
            last_row_id = cursor.lastrowid

            activity_contact_values = tuple((last_row_id, MICROJOURNAL_CONTACT_ID, DEFAULT_ACCOUNT_ID))
            cursor.execute(
                "INSERT INTO activity_contact (activity_id, contact_id, account_id) VALUES (%s, %s, %s)",
                activity_contact_values,
            )
            connection.commit()
    except pymysql.err.IntegrityError as e:
        logger.error("IntegrityError: {error}".format(error=e))
    close_server_connection(connection)
