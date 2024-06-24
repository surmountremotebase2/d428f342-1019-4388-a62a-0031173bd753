from surmount.base_class import Strategy, TargetAllocation
from surmount.data import Asset, OHLCV

class TradingStrategy(Strategy):
    def __init__(self):
        # Define the ticker symbol for the asset you're interested in
        self.tickers = ["AAPL"]

    @property
    def interval(self):
        # Set the interval for the data points. "1day" for daily granularity
        return "1day"

    @property
    def assets(self):
        # Define which assets this strategy will apply to, based on initialized tickers
        return self.tickers

    def run(self, data):
        # Initialize the target allocation for the defined ticker with no allocation
        allocation_dict = {}
        
        for ticker in self.tickers:
            # Ensure there is data available for the current ticker
            if ticker in data["ohlcv"]:
                # Extract the Open and Close prices for the current day
                open_price = data["ohlcv"][ticker][0]["open"]
                current_close_price = data["ohlcv"][ticker][-1]["close"]
                
                # Check if the current Close price is higher than the Open price
                if currentcloseprice > open_price:
                    # If the price has increased, allocate 100% to this asset
                    allocation_dict[ticker] = 1.0
                else:
                    # If the price has not increased, allocate 0% to this asset
                    allocation_dict[ticker] = 0.0
            else:
                # If there is no data, do not allocate to this ticker
                allocation_dict[ticker] = 0.0

        # Return the target allocations as a TargetAllocation object
        return TargetAllocation(allocation_dict)