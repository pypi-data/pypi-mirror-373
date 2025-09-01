import sys, os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Usage: python analysis/plot_multi_asset.py <csv_export_from_env>
# Expect a history CSV with columns: time, pnl, and numpy-like arrays for mid and inventory saved as strings

path = sys.argv[1] if len(sys.argv) > 1 else None
if path is None:
    print("Usage: python analysis/plot_multi_asset.py <history.csv>")
    sys.exit(1)

df = pd.read_csv(path)
# If arrays were saved as strings, attempt to parse
for col in ["mid", "inventory"]:
    if col in df.columns and df[col].dtype == object:
        df[col] = df[col].apply(lambda s: np.array(eval(s)) if isinstance(s, str) and s.startswith('[') else s)

# Determine number of assets
num_assets = len(df['mid'].iloc[0]) if isinstance(df['mid'].iloc[0], np.ndarray) else 1

plt.figure(figsize=(12, 8))

# Total PnL
plt.subplot(3, 1, 1)
plt.plot(df['time'], df['pnl'])
plt.title('Total PnL over time')

# Mid-prices per asset
plt.subplot(3, 1, 2)
for a in range(num_assets):
    series = [row[a] for row in df['mid'].values]
    plt.plot(df['time'], series, label=f'mid_{a}')
plt.legend()
plt.title('Mid-prices per asset')

# Inventory per asset
plt.subplot(3, 1, 3)
for a in range(num_assets):
    series = [row[a] for row in df['inventory'].values]
    plt.plot(df['time'], series, label=f'inv_{a}')
plt.legend()
plt.title('Inventory per asset')

plt.tight_layout()
out = os.path.join(os.path.dirname(path), 'multi_asset_plot.png')
plt.savefig(out)
print('Saved', out)