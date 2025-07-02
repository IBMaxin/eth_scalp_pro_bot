import pandas as pd
from ta.momentum import RSIIndicator
from ta.volatility import AverageTrueRange
from ta.trend import SMAIndicator

class EthScalpStrategyOHLCV:
    def __init__(self, rsi_threshold=15, tp_atr=4.0, sl_atr=1.5, cooldown_minutes=0, atr_threshold=0.1, tp1_atr=2.0):
        self.rsi_threshold = rsi_threshold
        # tp_atr is now our second, final take-profit (TP2)
        self.tp2_atr = tp_atr
        self.trailing_sl_atr = sl_atr 
        self.cooldown_minutes = cooldown_minutes
        self.atr_threshold = atr_threshold
        # NEW: The first, closer take-profit (TP1)
        self.tp1_atr = tp1_atr

    def prepare_indicators(self, df):
        df['RSI'] = RSIIndicator(close=df['close'], window=3).rsi()
        df['ATR'] = AverageTrueRange(high=df['high'], low=df['low'], close=df['close'], window=14).average_true_range()
        df['SMA200'] = SMAIndicator(close=df['close'], window=200).sma_indicator()
        return df

    def generate_signal(self, row, prev_row):
        is_volatile_enough = row['ATR'] > self.atr_threshold
        is_uptrend = row['close'] > row['SMA200']
        rsi_crossed_up = prev_row['RSI'] < self.rsi_threshold and row['RSI'] >= self.rsi_threshold

        if is_uptrend and rsi_crossed_up and is_volatile_enough:
            return 'BUY'
        
        return 'HOLD'

    def get_exit_levels(self, row, entry_price):
        atr = row['ATR']
        # Define both TP1 and TP2 levels
        take_profit_1_price = entry_price + (atr * self.tp1_atr)
        take_profit_2_price = entry_price + (atr * self.tp2_atr)
        stop_loss_price = entry_price - (atr * self.trailing_sl_atr)
        return take_profit_1_price, take_profit_2_price, stop_loss_price