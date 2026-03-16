import requests
from app.core.config import settings


def _servicenow_auth():
    settings.validate_servicenow()
    return settings.SN_USER, settings.SN_PASSWORD


def get_similar_incidents(query: str):
    url = f"{settings.SN_INSTANCE}/api/now/table/incident"
    params = {
        "sysparm_query": f"short_descriptionLIKE{query}^state=7",
        "sysparm_limit": 5,
        "sysparm_fields": "number,close_notes"
    }
    r = requests.get(url, auth=_servicenow_auth(), params=params)
    return [
        {"number": i["number"], "resolution": i.get("close_notes", "")}
        for i in r.json()["result"] if i.get("close_notes")
    ]

def create_incident(issue: dict, assignment_group: str, workaround: str | None = None) -> str:
    work_notes = ""
    if workaround:
        work_notes = (
            "Suggested workaround generated from similar resolved incidents:\n"
            f"{workaround}"
        )

    payload = {
        "short_description": issue["short_description"],
        "description": issue["description"],
        "category": issue.get("category", "software"),
        "priority": issue.get("priority", "3"),
        "assignment_group": assignment_group,
        "work_notes": work_notes,
    }

    r = requests.post(
        f"{settings.SN_INSTANCE}/api/now/table/incident",
        auth=_servicenow_auth(),
        json=payload
    )

    return r.json()["result"]["number"]


def get_incident_by_number(incident_number: str) -> dict | None:
    url = f"{settings.SN_INSTANCE}/api/now/table/incident"
    params = {
        "sysparm_query": f"number={incident_number}",
        "sysparm_limit": 1,
        "sysparm_fields": "number,short_description,description,close_notes,state,assignment_group.name"
    }

    r = requests.get(
        url,
        auth=_servicenow_auth(),
        params=params
    )
    r.raise_for_status()

    results = r.json().get("result", [])
    if not results:
        return None

    incident = results[0]
    assignment_group = incident.get("assignment_group") or {}
    return {
        "number": incident.get("number", ""),
        "short_description": incident.get("short_description", ""),
        "description": incident.get("description", ""),
        "close_notes": incident.get("close_notes", ""),
        "state": incident.get("state", ""),
        "assignment_group": assignment_group.get("name", "") if isinstance(assignment_group, dict) else assignment_group,
    }


def get_closed_incidents_for_index(limit=50):
    url = f"{settings.SN_INSTANCE}/api/now/table/incident"
    params = {
        "sysparm_query": "state=7",
        "sysparm_limit": limit,
        "sysparm_fields": "number,short_description,close_notes"
    }

    r = requests.get(
        url,
        auth=_servicenow_auth(),
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
        auth=_servicenow_auth(),
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
