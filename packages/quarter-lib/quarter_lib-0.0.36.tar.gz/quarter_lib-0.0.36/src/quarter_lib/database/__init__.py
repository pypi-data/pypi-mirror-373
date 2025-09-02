import requests

BASE_URL = "http://localhost:8100"


async def get_events(days):
    if days:
        return requests.get(BASE_URL + "/events/{days}").json()
    else:
        return requests.get(BASE_URL + "/events").json()


async def add_event(summary, start, end):
    event = {
        "summary": summary,
        "start_datetime": start,
        "end_datetime": end}
    return requests.post(BASE_URL + "/event", json=event).json()
