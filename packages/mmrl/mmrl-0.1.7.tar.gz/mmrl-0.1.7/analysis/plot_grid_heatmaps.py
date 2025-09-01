import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

df = pd.read_csv('data/grid_search_results.csv')
pivot_pnl  = df.pivot(index='spread', columns='sensitivity', values='final_pnl')
pivot_sharpe = df.pivot(index='spread', columns='sensitivity', values='sharpe')

plt.figure(figsize=(14, 6))

plt.subplot(1, 2, 1)
sns.heatmap(pivot_pnl, annot=True, cmap='YlGnBu')
plt.title("Final Pnl heatmap")

plt.subplot(1, 2, 2)
sns.heatmap(pivot_sharpe, annot=True, cmap='YlOrRd')
plt.title("Sharpe Ratio heatmap")

plt.tight_layout()
plt.savefig('results/grid_heatmaps.png')
plt.show()
