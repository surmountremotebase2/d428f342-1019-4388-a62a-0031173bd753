from surmount.base_class import Strategy, TargetAllocation
from surmount.data import ohlcv
from surmount.technical_indicators import MACD
import pandas as pd

class TradingStrategy(Strategy):
    @property
    def assets(self):
        # Implement logic to filter assets based on the price range specified ($2 to $40)
        # For the sake of example, we would manually list assets, though dynamic filtering based on price would typically be required.
        # return ["AAPL", "TSLA", "MSFT"]  # This should be dynamically generated based on the price criteria.
        self.assets = [asset for asset in Asset.list() if 2 <= asset.price <= 40] # Filter assets based on price criteria

    @property
    def interval(self):
        return "1min"  # Running the strategy every minute as specified

    def run(self, data):
        allocation_dict = {}
        for ticker in self.assets:
            current_data = data["ohlcv"][ticker]
            volume_series = pd.Series([x['volume'] for x in current_data])
            price_series = pd.Series([x['close'] for x in current_data])

            # 1. Check if the current relative volume's 50-day MA is 500% higher
            if volume_series.rolling(window=50).mean().iloc[-1] > 5 * volume_series.iloc[-1]:
                continue  # Skip current iteration if condition not met

            # 2. Price up 10% since the beginning of the day
            if not (price_series.iloc[-1] / price_series.iloc[0] - 1) >= 0.1:
                continue

            # 3. MACD above signal line
            macd_data = MACD(ticker, current_data, 12, 26)
            if macd_data["MACD"][-1] <= macd_data["signal"][-1]:
                continue

            # 4. Current candle makes a new high vs. the previous candle, and the previous candle makes a new low
            if not (current_data[-1]['high'] > current_data[-2]['high'] and current_data[-2]['low'] < current_data[-3]['low']):
                continue

            # 5. Price movement of 10 cents or more in the last 1 minute
            if not (price_series.iloc[-1] - price_series.iloc[-2] >= 0.1):
                continue

            # If all conditions met, allocate 100% to this asset (buy condition)
            allocation_dict[ticker] = 1.0

        return TargetAllocation(allocation_dict)

        # Note: Selling logic and stop loss conditions are not directly implementable via this strategy definition and might require real-time trading logic
        # implementation within the platform's execution management system, given the specifics of Surmount trading package limitations in defining sell and stop loss inside the strategy run method explicitly.