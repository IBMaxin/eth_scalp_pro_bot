import pandas as pd
import matplotlib.pyplot as plt

def load_trade_log(file_path='logs/trade_log.csv'):
    try:
        return pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"[!] Trade log not found: {file_path}")
        return pd.DataFrame()

def plot_cumulative_pnl(trade_log_df):
    if trade_log_df.empty:
        print("[!] No trade data to plot.")
        return

    trade_log_df['cumulative_gain'] = trade_log_df['gain'].cumsum()
    trade_log_df['time'] = pd.to_datetime(trade_log_df['time'])
    plt.figure(figsize=(10, 5))
    plt.plot(trade_log_df['time'], trade_log_df['cumulative_gain'])
    plt.title('Cumulative PnL Over Time')
    plt.xlabel('Time')
    plt.ylabel('Cumulative Gain')
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def summarize_trades(trade_log_df):
    if trade_log_df.empty:
        print("[!] No trade data to summarize.")
        return {}

    total_trades = len(trade_log_df)
    wins = len(trade_log_df[trade_log_df['gain'] > 0])
    losses = len(trade_log_df[trade_log_df['gain'] <= 0])
    win_rate = round((wins / total_trades) * 100, 2) if total_trades else 0
    total_pnl = round(trade_log_df['gain'].sum(), 2)

    summary = {
        'Total Trades': total_trades,
        'Wins': wins,
        'Losses': losses,
        'Win Rate (%)': win_rate,
        'Total PnL': total_pnl
    }

    return summary
