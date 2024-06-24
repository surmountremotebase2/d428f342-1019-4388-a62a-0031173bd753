from surmount.base_class import Strategy, TargetAllocation, Order, OrderType
from surmount.data import Asset
from surmount.technical_indicators import MACD, SMA
import pandas as pd

class TradingStrategy(Strategy):
    def __init__(self):
        self.interval = "1min" # Set data interval to 1 minute for high-frequency trading conditions
        self.assets = [asset for asset in Asset.list() if 2 <= asset.price <= 40] # Filter assets based on price criteria

    def rel_volume_ma(self, stock, ohlcv, length=50):
        """
        Calculate 50-day moving average of the relative volume for a given stock.
        Relative volume is today’s volume / average volume for the past length days.
        """
        volumes = pd.Series([d[stock]["volume"] for d in ohlcv])
        avg_volume = volumes[-length:].mean() # 50-day average volume
        rel_volume = volumes.iloc[-1] / avg_volume # Today's relative volume
        return rel_volume

    def is_price_up(self, stock, ohlcv, percent=10):
        """
        Checks if the price has moved up by a certain percentage since open.
        """
        current_price = ohlcv[-1][stock]["close"]
        previous_price = ohlcv[0][stock]["open"]
        return (current_price - previous_price) / previous_price * 100 >= percent

    def is_macd_above_signal(self, stock, ohlcv):
        """
        Checks if the MACD line is above the signal line.
        """
        macd = MACD(stock, ohlcv, fast=12, slow=26)
        return macd["MACD"][-1] > macd["signal"][-1]

    def candle_pattern(self, stock, ohlcv):
        """
        Checks for a specific candle pattern: current candle makes a new high vs. the previous candle,
        and the previous candle makes a new low vs. the candle before that.
        """
        last_close = ohlcv[-1][stock]["close"]
        last_high = ohlcv[-1][stock]["high"]
        prev_close = ohlcv[-2][stock]["close"]
        prev_low = ohlcv[-2][stock]["low"]
        prev_prev_low = ohlcv[-3][stock]["low"]

        new_high = last_close > last_high
        new_low = prev_close < prev_low and prev_low < prev_prev_low
        return new_high and new_low

    def price_move(self, stock, ohlcv, cents=0.10):
        """
        Checks if the price moves up by a certain amount in cents within 1 minute.
        """
        current_price = ohlcv[-1][stock]["close"]
        previous_price = ohlcv[-2][stock]["close"]
        return (current_price - previous_price) >= cents

    def run(self, data):
        orders = []
        for stock in self.assets:
            ohlcv = data["ohlcv"]
            rel_vol_ma_500 = self.rel_volume_ma(stock, ohlcv) > 5  # 500% higher check
            price_up_10_percent = self.is_price_up(stock, ohlcv)
            macd_above_signal = self.is_macd_above_signal(stock, ohlcv)
            valid_candle_pattern = self.candle_pattern(stock, ohlcv)
            price_movement = self.price_move(stock, ohlcv)

            # Buy conditions
            if rel_vol_ma_500 and price_up_10_percent and \
               macd_above_signal and valid_candle_pattern and \
               price_movement:
                orders.append(Order(stock, OrderType.BUY, None, trailing_stop=0.01, stop_loss=0.01))

            # Sell conditions
            current_low = ohlcv[-1][stock]["low"]
            previous_low = ohlcv[-2][stock]["low"]
            price_drop = ohlcv[-1][stock]["close"] - ohlcv[-2][stock]["close"] <= -0.10
            if current_low < previous_low or price_drop:
                orders.append(Order(stock, OrderType.SELL))

        # Handle 2 minutes before market close
        if self.time_to_market_close <= pd.Timedelta(minutes=2):
            for stock in self.assets:
                # Close any open positions
                orders.append(Order(stock, OrderType.SELL))

        return orders