import pandas as pd
import numpy as np
from datetime import timedelta
import os
import matplotlib.pyplot as plt

class TradeEngine:
    def __init__(self, starting_equity=1000, fees_pct=0.001, risk_per_trade=0.01):
        self.starting_equity = starting_equity
        self.fees_pct = fees_pct
        self.risk_per_trade = risk_per_trade
        self.equity = starting_equity
        self.equity_curve = [self.starting_equity]
        self.trade_log = []
        self.in_trade = False
        self.position_size = 0
        self.cooldown_end = None
        self.tp1_price = 0
        self.tp2_price = 0
        self.sl_price = 0
        self.high_since_entry = 0
        self.tp1_hit = False
        self.open_position_size = 0

    def run_backtest(self, df, strategy):
        df = strategy.prepare_indicators(df.copy())
        
        entry_price = 0
        start_index = 200 

        for i in range(start_index, len(df)):
            row = df.iloc[i]
            prev_row = df.iloc[i-1]

            if self.cooldown_end and row['time'] < self.cooldown_end:
                self.equity_curve.append(self.equity)
                continue

            signal = strategy.generate_signal(row, prev_row)
            if not self.in_trade and signal == 'BUY':
                entry_price = row['close']
                self.in_trade = True
                self.tp1_hit = False
                
                self.tp1_price, self.tp2_price, initial_sl_price = strategy.get_exit_levels(row, entry_price)
                self.sl_price = initial_sl_price
                
                risk_per_unit = entry_price - self.sl_price
                if risk_per_unit > 0:
                    equity_to_risk = self.equity * self.risk_per_trade
                    self.position_size = equity_to_risk / risk_per_unit
                    self.open_position_size = self.position_size
                else:
                    self.position_size = 0
                    self.open_position_size = 0

                self.high_since_entry = entry_price
                self.equity_curve.append(self.equity)
                continue
            
            if self.in_trade:
                self.high_since_entry = max(self.high_since_entry, row['high'])
                # This logic to calculate ATR at entry assumes tp2_atr exists in strategy.
                # It's better to calculate it once at entry and store it.
                atr_at_entry = (self.tp2_price - entry_price) / strategy.tp2_atr if strategy.tp2_atr > 0 else 0
                new_sl_price = self.high_since_entry - (atr_at_entry * strategy.trailing_sl_atr)
                self.sl_price = max(self.sl_price, new_sl_price)

                if not self.tp1_hit and row['high'] >= self.tp1_price:
                    exit_price = self.tp1_price
                    size_to_sell = self.position_size / 2
                    
                    gross_pnl_per_unit = exit_price - entry_price
                    total_gross_pnl = gross_pnl_per_unit * size_to_sell
                    trade_fee = (exit_price * size_to_sell) * self.fees_pct
                    net_gain_loss = total_gross_pnl - trade_fee
                    
                    self.equity += net_gain_loss
                    self.open_position_size -= size_to_sell
                    self.tp1_hit = True
                    self.sl_price = entry_price

                    self.trade_log.append({
                        'time': row['time'], 'type': 'win_tp1', 'entry': entry_price,
                        'exit': exit_price, 'gain': net_gain_loss, 'fee': trade_fee,
                        'position_size': size_to_sell
                    })

                exit_price_final = 0
                trade_type_final = ''
                if row['high'] >= self.tp2_price:
                    exit_price_final = self.tp2_price
                    trade_type_final = 'win_tp2'
                elif row['low'] <= self.sl_price:
                    exit_price_final = self.sl_price
                    trade_type_final = 'loss' if not self.tp1_hit else 'breakeven_sl'

                if trade_type_final:
                    gross_pnl_per_unit = exit_price_final - entry_price
                    total_gross_pnl = gross_pnl_per_unit * self.open_position_size
                    trade_fee = (exit_price_final * self.open_position_size) * self.fees_pct
                    net_gain_loss = total_gross_pnl - trade_fee
                    
                    self.equity += net_gain_loss

                    self.trade_log.append({
                        'time': row['time'], 'type': trade_type_final, 'entry': entry_price,
                        'exit': exit_price_final, 'gain': net_gain_loss, 'fee': trade_fee,
                        'position_size': self.open_position_size
                    })
                    self.in_trade = False
                    self.cooldown_end = row['time'] + timedelta(minutes=strategy.cooldown_minutes)

            self.equity_curve.append(self.equity)

        # The return value from run_backtest should be the final stats
        return self.get_final_stats()

    def get_final_stats(self):
        """Calculates and returns the final performance statistics."""
        df_log = pd.DataFrame(self.trade_log)
        # We consider a "trade" to be a full open-to-close cycle.
        # Since we log partials, we count unique entry times.
        total_trades = df_log['entry'].nunique()

        if total_trades == 0:
            return {'TotalTrades': 0, 'WinRate': 0, 'TotalPnL': 0, 'Sharpe': 0}

        # A trade is a "win" if its net PnL is positive.
        # We group by entry time to sum up partials.
        trade_pnl = df_log.groupby('entry')['gain'].sum()
        wins = len(trade_pnl[trade_pnl > 0])
        winrate = (wins / total_trades) * 100 if total_trades > 0 else 0
        pnl = self.equity - self.starting_equity
        
        diffs = np.diff(self.equity_curve)
        sharpe = np.mean(diffs) / (np.std(diffs) + 1e-9)

        stats = {
            'TotalTrades': total_trades,
            'WinRate': round(winrate, 2),
            'TotalPnL': round(pnl, 2),
            'Sharpe': round(sharpe, 2)
        }
        return stats

    def save_trade_log(self, filename):
        os.makedirs("logs", exist_ok=True)
        pd.DataFrame(self.trade_log).to_csv(filename, index=False)
        print(f"Trade log saved to {filename}")

    def plot_equity_curve(self, save_path='logs/equity_curve.png'):
        plt.figure(figsize=(12, 6))
        plt.plot(self.equity_curve)
        plt.title('Strategy Equity Curve')
        plt.xlabel('Time (in minutes)')
        plt.ylabel(f'Equity (starting from ${self.starting_equity})')
        plt.grid(True)
        
        plt.savefig(save_path)
        plt.close()
        print(f"Equity curve plot saved to {save_path}")