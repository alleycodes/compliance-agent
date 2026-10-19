import pandas as pd

APPROVAL_LIMIT = 25000   # payments above this need an approver
ROUND_STEP = 10000       # "round" means an exact multiple of this
HIGH_VALUE = 100000      # payments above this always get a look


def detect(csv_path):
    df = pd.read_csv(csv_path)
    df["approved_by"] = df["approved_by"].fillna("")
    flagged = {}   # txn_id -> the payment plus the reasons it was flagged

    def flag(row, rule, reason):
        if row["txn_id"] not in flagged:
            item = row.to_dict()
            item["rules"] = []
            item["reasons"] = []
            flagged[row["txn_id"]] = item
        flagged[row["txn_id"]]["rules"].append(rule)
        flagged[row["txn_id"]]["reasons"].append(reason)

    # Rule 1: same vendor + same amount + same date = duplicate
    dups = df[df.duplicated(subset=["vendor", "amount", "date"], keep=False)]
    for _, row in dups.iterrows():
        flag(row, "DUPLICATE", "duplicate payment: same vendor, same amount, same day")

    # Rule 2: large round-number payment
    round_rows = df[(df["amount"] % ROUND_STEP == 0) & (df["amount"] >= ROUND_STEP)]
    for _, row in round_rows.iterrows():
        flag(row, "ROUND_AMOUNT", "large round-number payment, exact multiple of 10,000")

    # Rule 3: above the approval limit and nobody approved it
    no_approver = df[(df["amount"] > APPROVAL_LIMIT) & (df["approved_by"] == "")]
    for _, row in no_approver.iterrows():
        flag(row, "NO_APPROVER", "above approval limit with no approver recorded")

    # Rule 4: very high value payment
    high = df[df["amount"] > HIGH_VALUE]
    for _, row in high.iterrows():
        flag(row, "HIGH_VALUE", "very high value payment")

    return list(flagged.values())


if __name__ == "__main__":
    for item in detect("ledger.csv"):
        print(item["txn_id"], item["vendor"], item["amount"], "->", item["reasons"])