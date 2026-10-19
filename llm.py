import os

PROMPT = """You are a compliance reviewer. In 2-3 plain sentences, explain why this
payment was flagged. Use ONLY the policy text below and mention the policy ID
(for example POL-2). If the policy text does not cover the case, say so.

Payment: {payment}
Reasons it was flagged: {reasons}
Policy text:
{policy}
"""


def explain(payment, policy_chunks):
    policy = "\n".join(policy_chunks) if policy_chunks else "(no relevant policy found)"

    # Option A: use Claude if an API key is set
    if os.getenv("ANTHROPIC_API_KEY"):
        import anthropic
        client = anthropic.Anthropic()
        reply = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=300,
            messages=[{"role": "user", "content": PROMPT.format(
                payment=f"{payment['txn_id']}, {payment['vendor']}, Rs {payment['amount']}",
                reasons="; ".join(payment["reasons"]),
                policy=policy)}],
        )
        return reply.content[0].text

    # Option B: no key, so build the sentence ourselves
    ids = [c.split()[0] for c in policy_chunks]
    cite = "See " + ", ".join(ids) + "." if ids else "No matching policy found."
    return (f"Payment {payment['txn_id']} ({payment['vendor']}, Rs {payment['amount']:,}) "
            f"was flagged: {'; '.join(payment['reasons'])}. {cite}")


if __name__ == "__main__":
    from anomaly import detect
    from retriever import PolicyRetriever
    r = PolicyRetriever("policy.txt")
    for item in detect("ledger.csv"):
        hits = r.search(" ".join(item["reasons"]))
        print(explain(item, [c for c, s in hits]))
        print()