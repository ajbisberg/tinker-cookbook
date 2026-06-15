import pandas
import matplotlib.pyplot as plt

df = pandas.read_json("metrics.jsonl", lines=True)

fig, ax_left = plt.subplots()
ax_left.plot(df["train_mean_nll"], label="train_loss", color="tab:blue")
ax_left.plot(df["test/nll"].dropna(), label="test_loss", color="tab:orange")
ax_left.set_ylabel("NLL")
ax_left.set_xlabel("Step")

lines = list(ax_left.get_lines())

if "test/accuracy" in df.columns:
    ax_right = ax_left.twinx()
    ax_right.plot(df["test/accuracy"].dropna(), label="test_accuracy", color="tab:green")
    ax_right.set_ylabel("Accuracy")
    ax_right.set_ylim(0.0, 1.0)
    lines.extend(ax_right.get_lines())

ax_left.legend(lines, [line.get_label() for line in lines], loc="best")
fig.tight_layout()
fig.savefig("metrics.png")
