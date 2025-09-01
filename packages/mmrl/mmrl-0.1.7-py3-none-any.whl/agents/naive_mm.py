class NaiveMarketMaker:
    def __init__(self, spread: float = 0.1):
        self.spread = spread

    def quote(self, mid_price: float, inventory: int):
        half = self.spread / 2.0
        bid = mid_price - half
        ask = mid_price + half
        return bid, ask
    