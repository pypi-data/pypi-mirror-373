import requests

from ...logging import setup_logging

logger = setup_logging(__file__)
BASE_URL = "http://localhost:8200"


async def add_timer(summary, start, end):
    timer = {
        "summary": summary,
        "start_datetime": start,
        "end_datetime": end}
    return requests.post(BASE_URL + "/timer/add", json=timer).json()
