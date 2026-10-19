from sklearn.feature_extraction.text import TfidfVectorizer
import faiss

MIN_SCORE = 0.05   # below this, we say "no relevant policy found"


class PolicyRetriever:
    def __init__(self, policy_path):
        text = open(policy_path).read()
        self.chunks = [c.strip() for c in text.split("\n\n") if c.strip()]
        self.vectorizer = TfidfVectorizer(stop_words="english")
        numbers = self.vectorizer.fit_transform(self.chunks).toarray().astype("float32")
        faiss.normalize_L2(numbers)
        self.index = faiss.IndexFlatIP(numbers.shape[1])
        self.index.add(numbers)

    def search(self, query, k=2):
        q = self.vectorizer.transform([query]).toarray().astype("float32")
        faiss.normalize_L2(q)
        scores, ids = self.index.search(q, k)
        results = []
        for score, i in zip(scores[0], ids[0]):
            if i != -1 and score >= MIN_SCORE:
                results.append((self.chunks[i], float(score)))
        return results


if __name__ == "__main__":
    from anomaly import detect
    r = PolicyRetriever("policy.txt")
    for item in detect("ledger.csv"):
        query = " ".join(item["reasons"])
        hits = r.search(query)
        print(item["txn_id"], "->", [c.split()[0] for c, s in hits])