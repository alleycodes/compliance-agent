import sys
from anomaly import detect
from retriever import PolicyRetriever
from audit import AuditLog
from graph import build_graph

auto = "--auto-approve" in sys.argv

flagged = detect("ledger.csv")
print(len(flagged), "payments flagged by the rules")

audit = AuditLog()
app = build_graph(PolicyRetriever("policy.txt"), audit, auto)
final = app.invoke({"flagged": flagged, "idx": 0, "results": []})

print("\nDone.", len(final["results"]), "findings approved.")
print("Audit trail saved in audit.db")