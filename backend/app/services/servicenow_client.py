import requests
from backend.app.core.config import settings

def get_similar_incidents(query: str):
    url = f"{settings.SN_INSTANCE}/api/now/table/incident"
    params = {
        "sysparm_query": f"short_descriptionLIKE{query}^state=7",
        "sysparm_limit": 5,
        "sysparm_fields": "number,close_notes"
    }
    r = requests.get(url, auth=(settings.SN_USER, settings.SN_PASSWORD), params=params)
    return [
        {"number": i["number"], "resolution": i.get("close_notes", "")}
        for i in r.json()["result"] if i.get("close_notes")
    ]

def create_incident(issue: dict, assignment_group: str) -> str:
    payload = {
        "short_description": issue["short_description"],
        "description": issue["description"],
        "category": issue.get("category", "software"),
        "priority": issue.get("priority", "3"),
        "assignment_group": assignment_group
    }

    r = requests.post(
        f"{settings.SN_INSTANCE}/api/now/table/incident",
        auth=(settings.SN_USER, settings.SN_PASSWORD),
        json=payload
    )

    return r.json()["result"]["number"]


def get_closed_incidents_for_index(limit=50):
    url = f"{settings.SN_INSTANCE}/api/now/table/incident"
    params = {
        "sysparm_query": "state=7",
        "sysparm_limit": limit,
        "sysparm_fields": "number,short_description,close_notes"
    }

    r = requests.get(
        url,
        auth=(settings.SN_USER, settings.SN_PASSWORD),
        params=params
    )

    incidents = []
    for i in r.json()["result"]:
        if i.get("close_notes"):
            incidents.append({
                "number": i["number"],
                "text": f"{i['short_description']} {i['close_notes']}"
            })

    return incidents

def get_closed_incidents_for_index(limit=50):
    url = f"{settings.SN_INSTANCE}/api/now/table/incident"
    params = {
        "sysparm_query": "state=7",
        "sysparm_limit": limit,
        "sysparm_fields": "number,short_description,close_notes,assignment_group.name"
    }

    r = requests.get(
        url,
        auth=(settings.SN_USER, settings.SN_PASSWORD),
        params=params
    )

    incidents = []
    for i in r.json()["result"]:
        if i.get("close_notes"):
            incidents.append({
                "number": i["number"],
                "text": f"{i['short_description']} {i['close_notes']}",
                "assignment_group": i.get("assignment_group", {}).get("name")
            })

    return incidents
