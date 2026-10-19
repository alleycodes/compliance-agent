from typing import TypedDict
from langgraph.graph import StateGraph, END
from llm import explain


class State(TypedDict):
    flagged: list      # all flagged payments
    idx: int           # which payment we are on
    current: dict      # the payment being processed
    context: list      # policy paragraphs found for it
    explanation: str   # the written explanation
    approved: bool     # did the human say yes?
    results: list      # finished, approved findings


def build_graph(retriever, audit, auto_approve):

    def pick_next(state):
        payment = state["flagged"][state["idx"]]
        audit.log(payment["txn_id"], "FLAGGED", "; ".join(payment["reasons"]))
        return {"current": payment}

    def retrieve(state):
        payment = state["current"]
        hits = retriever.search(" ".join(payment["reasons"]))
        ids = ", ".join(c.split()[0] for c, s in hits) or "none"
        audit.log(payment["txn_id"], "RETRIEVED", ids)
        return {"context": [c for c, s in hits]}

    def explain_step(state):
        text = explain(state["current"], state["context"])
        audit.log(state["current"]["txn_id"], "EXPLAINED", text)
        return {"explanation": text}

    def approve(state):
        print("\n" + state["explanation"])
        if auto_approve:
            ok = True
        else:
            ok = input("Approve this finding? (y/n): ").strip().lower() == "y"
        audit.log(state["current"]["txn_id"], "APPROVED" if ok else "REJECTED", "human decision")
        return {"approved": ok}

    def finalize(state):
        results = list(state["results"])
        if state["approved"]:
            results.append({"txn_id": state["current"]["txn_id"],
                            "finding": state["explanation"]})
        return {"results": results, "idx": state["idx"] + 1}

    def more_left(state):
        if state["idx"] < len(state["flagged"]):
            return "pick_next"
        return END

    g = StateGraph(State)
    g.add_node("pick_next", pick_next)
    g.add_node("retrieve", retrieve)
    g.add_node("explain", explain_step)
    g.add_node("approve", approve)
    g.add_node("finalize", finalize)

    g.set_entry_point("pick_next")
    g.add_edge("pick_next", "retrieve")
    g.add_edge("retrieve", "explain")
    g.add_edge("explain", "approve")
    g.add_edge("approve", "finalize")
    g.add_conditional_edges("finalize", more_left)
    return g.compile()