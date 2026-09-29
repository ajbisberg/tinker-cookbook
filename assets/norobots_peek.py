import datasets, collections, random
ds = datasets.load_dataset("HuggingFaceH4/no_robots")
print(ds)
tr = ds["train"]
print("columns:", tr.column_names)
print("categories:", collections.Counter(tr["category"]).most_common())
turns = collections.Counter(len(m) for m in tr["messages"])
print("messages per example:", sorted(turns.items())[:8])
print("with system msg:", sum(m[0]["role"] == "system" for m in tr["messages"]))
random.seed(1)
for cat in sorted(set(tr["category"])):
    rows = [r for r in tr if r["category"] == cat and sum(len(m["content"]) for m in r["messages"]) < 700]
    for r in random.sample(rows, 2):
        print(f"\n===== [{cat}] {r['prompt_id'][:8]}")
        for m in r["messages"]:
            print(f"  {m['role'].upper()}: {m['content'][:400]}")
