import os
import sys
import json
import pandas as pd

# This line helps Python find your other code files, like strategy.py.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from strategies.strategy import EthScalpStrategyOHLCV

def run_backtest_with_best_config():
    """
    This function loads the best configuration and runs a single backtest.
    """
    print("--- Running Backtest with Best Found Parameters ---")

    # --- 1. Load the Best Configuration ---
    # This is the core of our "smart" system. We read the settings that
    # 'optimize.py' automatically saved for us.
    config_path = 'configs/best_config.json'
    try:
        with open(config_path, 'r') as f:
            best_config = json.load(f)
    except FileNotFoundError:
        print(f"Error: Configuration file not found at {config_path}")
        print("Please run 'optimize.py' first to generate the configuration.")
        return # Exit the function if the file doesn't exist.

    print("\nLoaded Best Configuration:")
    print(best_config)

    # --- 2. Load the Data ---
    # The data path is now also stored in the config, but we will hardcode
    # it here for simplicity in this script. For a more advanced system,
    # you would also read the data_path from the config.
    data_path = 'data/eth_usd_binanceus_120d_1m.csv'
    try:
        df = pd.read_csv(data_path, parse_dates=['time'])
        print(f"\nData loaded successfully from: {data_path}")
    except FileNotFoundError:
        print(f"Error: Data file not found at {data_path}")
        print("Please run a data fetching script first.")
        return

    # --- 3. Initialize and Run the Strategy ---
    # We create an instance of our strategy, passing in the best settings
    # that we loaded from the JSON file.
    strategy = EthScalpStrategyOHLCV(
        rsi_threshold=best_config["rsi_threshold"],
        tp_atr=best_config["tp_atr"],
        sl_atr=best_config["sl_atr"],
        cooldown_minutes=best_config["cooldown_minutes"]
    )

    # Run the backtest on the full dataset.
    print("\n--- Running backtest on the full dataset... ---")
    trade_log, final_stats = strategy.run_backtest(df.copy())

    # --- 4. Display Results and Save Log ---
    print("\n\n--- BACKTEST PERFORMANCE (Full Dataset) ---")
    print(pd.Series(final_stats).to_string())
    print("-------------------------------------------------")

    # Save the detailed log of all trades for analysis.
    log_filename = 'logs/best_strategy_full_backtest_log.csv'
    strategy.save_trade_log(log_filename)


if __name__ == '__main__':
    # This line means the 'run_backtest_with_best_config' function will
    # only be executed when you run this script directly from the command line.
    run_backtest_with_best_config()