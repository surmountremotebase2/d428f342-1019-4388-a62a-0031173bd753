from surmount.base_class import Strategy, TargetAllocation
from surmount.data import OHLCV

class TradingStrategy(Strategy):
    def __init__(self):
        self.assets = ["SPY", "AAPL", "GOOGL", "QQQ"]  # Example assets, customize as needed

    @property
    def interval(self):
        # Using a 1-minute interval as we need to track price drops within a minute
        return "1min"

    def run(self, data):
        allocation_dict = {}
        market_close = "15:58:00"  # Adjust as per market's close time and timezone
        
        for ticker in self.assets:
            last_data = data["ohlcv"][ticker][-2:]  # Getting the last two data points for comparison
            current_price = last_data[-1]['close']
            previous_close = last_data[-2]['close']
            current_time = last_data[-1]['date'][-8:]  # Extracting the HH:MM:SS part
            
            # Setting allocations to zero (selling) if conditions met or it's 2 minutes to close
            if (current_price < previous_close and (previous_close - current_price) >= 0.10) or current_time >= market_answer:
                allocation_dict[ticker] = 0  # Sell signal
            else:
                allocation_dict[ticker] = None  # No change in position
            
            # Implementing stop loss and trailing stop logic (simplistic example, needs customization)
            # For simplicity, using fixed percentage change calculation instead of referencing holding costs
            if (current_price / previous_close - 1) <= -0.01:  # A simple 1% stop loss check
                allocation_dict[ticker] = 0  # Sell signal to stop loss
            elif (current_price / previous_close - 1) >= 0.01:  # If profit is more than or equal to 1%
                # Adjust allocation based on trailing stop (one could adjust the allocation to reduce the position instead of selling all)
                if (current_price / previous_close - 1) < 0.01:  # Trailing stop condition
                    allocation_dict[ticker] = 0  # Trailing stop triggered

        return TargetAllocation(allocation_dict)