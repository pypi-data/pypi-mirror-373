import pandas as pd
import matplotlib.pyplot as plt
import sys

# Usage: python analysis/plot_metrics.py [input_csv]
# Default: data/inventory_mm_run.csv

input_csv = sys.argv[1] if len(sys.argv) > 1 else 'data/inventory_mm_run.csv'

df = pd.read_csv(input_csv)
if df.empty:
    print('Input CSV is empty')
    sys.exit(0)

# Basic summary
pnl = df['pnl']
inv = df['inventory']
print(f"Final PnL: {pnl.iloc[-1]:.2f}")
print(f"Final Inventory: {inv.iloc[-1]}")
ret = pnl.diff().dropna()
sharpe = ret.mean() / ret.std() if ret.std() > 0 else 0.0
print(f"Sharpe (naive): {sharpe:.4f}")

# Plot
plt.figure(figsize=(12, 6))
plt.subplot(2, 1, 1)
plt.plot(df['time'], pnl)
plt.title('PnL over time')

plt.subplot(2, 1, 2)
plt.plot(df['time'], inv)
plt.title('Inventory over time')
plt.tight_layout()

out_path = 'results/inventory_mm_plot_from_csv.png'
plt.savefig(out_path)
print(f"Saved plot to {out_path}")
