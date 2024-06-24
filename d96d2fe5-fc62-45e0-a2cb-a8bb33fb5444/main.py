from surmount.base_class import Strategy, TargetAllocation
from surmount.data import ohlcv

class TradingStrategy(Strategy):
    def __init__(self):
        self.ticker = "AAPL"  # Example stock ticker; change as needed

    @property
    def assets(self):
        return [self.ticker]

    @property
    def interval(self):
        return "1day"  # Using 1day interval to get the day's open and current price

    def run(self, data):
        d = data["ohlcv"]
        
        if self.ticker in d:
            # Ensure there's enough data
            if len(d[self.ticker]) > 0:
                open_price = d[self.ticker][0]["open"]  # Today's opening price
                current_price = d[self.ticker][-1]["close"]  # Latest available price, which can be considered current
                
                increase_percentage = (current_price - open_price) / open_price * 100
                
                # Check if the increase is 10% or more
                if increase_percentage >= 10:
                    # Allocate 100% to this stock
                    return TargetAllocation({self.ticker: 1})
                else:
                    # No allocation if the condition is not met
                    return TargetAllocation({self.ticker: 0})
        else:
            # Return empty allocation if ticker data not available
            return TargetAllocation({})