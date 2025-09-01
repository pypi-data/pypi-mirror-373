from __future__ import annotations
from typing import Iterator, Dict, Any
import pandas as pd


class MarketReplay:
    """
    Minimal adapter to replay L2 snapshots or trades from a CSV/parquet for env consumption.
    Users can implement `.iter_ticks()` to yield market states compatible with env expectations.
    """

    def __init__(self, path: str, fmt: str = 'csv'):
        self.path = path
        self.fmt = fmt
        if fmt == 'csv':
            self.df = pd.read_csv(path)
        elif fmt == 'parquet':
            self.df = pd.read_parquet(path)
        else:
            raise ValueError('Unsupported format')

    def iter_ticks(self) -> Iterator[Dict[str, Any]]:
        for _, row in self.df.iterrows():
            # Example mapping: users should adapt this to their schema
            yield {
                'time': row.get('time'),
                'mid_price': row.get('mid'),
                'best_bid': row.get('best_bid'),
                'best_ask': row.get('best_ask'),
                'volume': row.get('volume', 0),
            }