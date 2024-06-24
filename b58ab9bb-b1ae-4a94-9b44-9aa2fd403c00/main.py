from surmount.base_class import Strategy, TargetAllocation
from surmount.data import OHLCV, RelativeVolume
from surmount.technical_indicators import MACD
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        # Define the tickers we are interested in
        self.tickers = ["AAPL", "GOOGL", "MSFT"]
        # Volume and price data for the tickers
        self.data_list = [OHLCV(i) for i in self.tickers] + [RelativeVolume(i, 50) for i in self.tickers]

    @property
    def assets(self):
        # Assets that the strategy will trade
        return self.tickers

    @property
    def interval(self):
        # Using minute data for the MACD and trading timing
        return "1min"

    @property
    def data(self):
        # Data required by the strategy
        return self.data_list

    def run(self, data):
        allocation_dict = {}

        for ticker in self.tickers:
            ohlcv_data = data["ohlcv"][ticker]
            relvol_data = data["relative_volume"][ticker]
            if not ohlcv_data or not relvol_data:
                continue  # Skip if data is missing

            # Check if the relative volume 50-day MA is 500% higher than usual
            if relvol_data[-1] < 5:
                continue

            # Check if the price is up 10% for the day
            current_price = ohlcv_data[-1]["close"]
            opening_price = ohlcv_data[-1]["open"]
            if ((current_price - opening_price) / opening_price) * 100 < 10:
                continue

            # MACD above the signal line
            macd_data = MACD(ticker, ohlcv_data, 12, 26)
            if macd_data is None or macd_data["MACD"][-1] <= macd_data["signal"][-1]:
                continue

            # Buy logic: Current candle makes a new high vs. previous, and previous candle makes a new low vs. the one before that
            if len(ohlcv_data) >= 3 and ohlcv_data[-1]["high"] > ohlcv_data[-2]["high"] and ohlcv_data[-2]["low"] < ohlcv_data[-3]["low"]:
                allocation_dict[ticker] = 0.33  # Allocate a third of the capital to each stock

            # Sell logic: Current candle makes a new low compared to previous candle
            elif len(ohlcv_data) >= 2 and ohlcv_data[-1]["low"] < ohlcv_data[-2]["low"]:
                allocation_dict[ticker] = 0  # Sell off the position if any
            else:
                allocation_dict[ticker] = 0  # Default to no position if none of the conditions are met

        return TargetAllocation(allocation_dict)