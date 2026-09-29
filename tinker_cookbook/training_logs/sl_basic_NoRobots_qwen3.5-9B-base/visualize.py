import pandas
import matplotlib.pyplot as plt
df = pandas.read_json("metrics.jsonl", lines=True)
plt.plot(df['train_mean_nll'], label='train_loss')
plt.plot(df['test/nll'].dropna(), label='test_loss')
plt.legend()
plt.savefig('metrics.png')