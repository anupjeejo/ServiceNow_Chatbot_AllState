from collections import Counter

DEFAULT_GROUP = "Service Desk"

def run(state):
    groups = [
        i["assignment_group"]
        for i in state.get("historical", [])
        if i.get("assignment_group")
    ]

    if not groups:
        state["assignment_group"] = DEFAULT_GROUP
        return state

    # Most common assignment group
    most_common = Counter(groups).most_common(1)[0][0]
    state["assignment_group"] = most_common
    return state
