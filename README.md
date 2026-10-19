# AI Compliance Review & Anomaly Detection Agent

Reads a CSV ledger of payments, flags suspicious ones with rule-based checks,
retrieves the matching company policy using FAISS, writes a plain-language
explanation citing that policy, asks a human to approve each finding, and
logs every step to a SQLite audit trail. Built with Python and LangGraph.

## Run
    pip install -r requirements.txt
    python main.py                 # asks you to approve each finding (y/n)
    python main.py --auto-approve  # demo mode

Optional: set ANTHROPIC_API_KEY to have Claude write the explanations.
Without it, a template explanation is used.

## Files
- anomaly.py: rules (duplicate, round amount, no approver, high value)
- retriever.py: policy search with FAISS
- llm.py: explanation step
- audit.py: SQLite audit log
- graph.py: LangGraph workflow
- main.py: entry point

## Limitations
- TF-IDF vectors instead of neural embeddings
- Simple thresholds, so some false positives
- Small sample ledger and policy set
