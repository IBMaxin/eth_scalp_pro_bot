import os
import sys
import pandas as pd
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.trade_engine import TradeEngine
from strategies.strategy import EthScalpStrategyOHLCV

print("--- Starting Optimization Process (Partial Take-Profit) ---")

data_path = 'data/eth_usd_binanceus_60d_1m.csv'
df = pd.read_csv(data_path, parse_dates=['time'])
print(f"Data loaded successfully from: {data_path}")

print("\n--- Splitting data into Training and Testing sets ---")
split_point = int(len(df) * 0.8)
df_train = df.iloc[:split_point].copy()
df_test = df.iloc[split_point:].copy()
print(f"Training set size: {len(df_train)} data points")
print(f"Testing set size: {len(df_test)} data points")

# --- Grid Search including the new TP1 parameter ---
rsi_values = [10, 15]
tp2_atr_values = [4.0, 6.0] # This is our final target (TP2)
sl_atr_values = [1.5, 2.0]
cooldowns = [10, 20]
atr_threshold_values = [0.1, 0.2]
# NEW: Add values for our first, closer take-profit (TP1)
tp1_atr_values = [1.5, 2.0]
results = []
print("\n--- Running optimization on TRAINING data... ---")

for rsi in rsi_values:
    for tp2 in tp2_atr_values:
        for sl in sl_atr_values:
            for cooldown in cooldowns:
                for atr_thresh in atr_threshold_values:
                    for tp1 in tp1_atr_values: # New inner loop for TP1
                        # Ensure TP1 is always less than TP2
                        if tp1 >= tp2:
                            continue

                        engine = TradeEngine(starting_equity=1000, fees_pct=0.001)
                        strategy = EthScalpStrategyOHLCV(
                            rsi_threshold=rsi,
                            tp_atr=tp2, # Pass the final target
                            sl_atr=sl,
                            cooldown_minutes=cooldown,
                            atr_threshold=atr_thresh,
                            tp1_atr=tp1 # Pass the new partial target
                        )
                        metrics = engine.run_backtest(df_train, strategy)
                        # Log all parameters
                        results.append({
                            "RSI": rsi, "TP_ATR": tp2, "SL_ATR": sl,
                            "Cooldown": cooldown, "ATR_Thresh": atr_thresh,
                            "TP1_ATR": tp1, **metrics
                        })

df_result = pd.DataFrame(results).sort_values(by="TotalPnL", ascending=False)

if not df_result.empty:
    best_params = df_result.iloc[0].to_dict()
    print("\n--- Best parameters found during training ---")
    print(best_params)

    best_config = {
        "rsi_threshold": int(best_params["RSI"]),
        "tp_atr": float(best_params["TP_ATR"]),
        "sl_atr": float(best_params["SL_ATR"]),
        "cooldown_minutes": int(best_params["Cooldown"]),
        "atr_threshold": float(best_params["ATR_Thresh"]),
        "tp1_atr": float(best_params["TP1_ATR"]) # Save the best TP1
    }
    with open('configs/best_config.json', 'w') as f:
        json.dump(best_config, f, indent=2)
    print("\nBest settings automatically saved to 'configs/best_config.json'")

    print("\n--- Running a final validation test on UNSEEN data... ---")
    final_engine = TradeEngine(starting_equity=1000, fees_pct=0.001)
    final_strategy = EthScalpStrategyOHLCV(
        rsi_threshold=best_config["rsi_threshold"],
        tp_atr=best_config["tp_atr"],
        sl_atr=best_config["sl_atr"],
        cooldown_minutes=best_config["cooldown_minutes"],
        atr_threshold=best_config["atr_threshold"],
        tp1_atr=best_config["tp1_atr"] # Use the best TP1
    )
    final_stats = final_engine.run_backtest(df_test, final_strategy)

    print("\n\n--- FINAL VALIDATION PERFORMANCE ---")
    print(pd.Series(final_stats).to_string())
    print("-------------------------------------------------")

    final_engine.plot_equity_curve(save_path='logs/final_validation_equity_curve.png')
else:
    print("\n--- No trades were executed during the optimization. ---")