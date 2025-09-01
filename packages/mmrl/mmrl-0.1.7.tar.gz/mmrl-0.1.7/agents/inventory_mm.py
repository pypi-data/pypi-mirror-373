class InventoryAwareMarketMaker:
    def __init__(self, spread=0.01, inventory_sensitivity=0.01):
        self.spread = spread
        self.inventory_sensitivity = inventory_sensitivity

    def quote(self, mid_price, inventory):
        skew = self.inventory_sensitivity * inventory
        ask = mid_price + self.spread/2 - skew
        bid = mid_price - self.spread/2 + skew

        return bid, ask
