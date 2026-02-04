from backend.app.core.vector_bootstrap import vector_store

def run(state):
    if not vector_store.index:
        state["historical"] = []
        return state

    query = state["issue"]["short_description"]
    results = vector_store.search(query, k=5)

    state["historical"] = [
        {
            "number": r["number"],
            "resolution": r["text"],
            "assignment_group": r.get("assignment_group")
        }
        for r in results
    ]

    return state

