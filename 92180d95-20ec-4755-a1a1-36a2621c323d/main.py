from surmount.base_class import Strategy, TargetAllocation
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        # Initialize with an empty list of tickers assuming dynamic fetching of tickers
        self.tickers = []

    @property
    def interval(self):
        # Strategy evaluation frequency
        return "1day"

    @property
    def assets(self):
        # Dynamically list all available/interested assets
        return self.tickers

    @property
    def data(self):
        # Define required data sources (e.g., OHLCV for price data)
        return []

    def run(self, data):
        allocation_dict = {}
        
        for ticker in self.tickers:
            # Fetch the OHLCV data for the ticker
            ohlcv = data["ohlcv"].get(ticker, {})
            
            if ohlcv:
                # Calculate the percentage change from open to close
                percentage_change = (ohlcv["close"] - ohlcv["open"]) / ohlcv["open"] * 100
                
                # Buy Strategy: Buy if stock is up 10% from the open
                if percentage_change >= 10:
                    allocation_dict[ticker] = 0.1  # Example allocation, adjust based on your strategy & risk management
                
                # Assuming there's a method to check if the stock is already owned
                # owned = check_if_owned(ticker)  you'd need to implement this logic
                
                # Example sell condition: if owned & stock drops 1% from purchase price
                # This will require tracking purchase price and current price, which 
                # isn't directly provided in this snippet. This is a conceptual example.
                # if owned and percentage_change < -1:
                #     allocation_dict[ticker] = 0

        # Making sure to handle empty allocations logically, perhaps by keeping current allocations
        if not allocation_Checker(RS_allocation_dict):
            return TargetAllocation({})  # Example to maintain current allocations
        
        return TargetAllocation(allocation_dict)