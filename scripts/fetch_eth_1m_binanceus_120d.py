import ccxt
import pandas as pd
import time
import os
from datetime import datetime

# === CONFIG ===
exchange = ccxt.binanceus()
symbol = 'ETH/USD'
timeframe = '1m'
limit = 1000

# --- CHANGE 1: Set days to 60 ---
days = 60 

# --- CHANGE 2: Set a new output path ---
output_path = f'data/eth_usd_binanceus_{days}d_1m.csv' 
log_file = f'logs/binanceus_1m_{days}d_log.txt'

os.makedirs("data", exist_ok=True)
os.makedirs("logs", exist_ok=True)

def log(msg):
    line = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    print(line)
    with open(log_file, "a", encoding="utf-8", errors="ignore") as f:
        f.write(line + "\n")

# === FETCH LOOP ===
since = exchange.parse8601((pd.Timestamp.utcnow() - pd.Timedelta(days=days)).isoformat())
now = exchange.milliseconds()
all_candles = []

log(f"Starting fetch: {symbol}, {timeframe}, {days}d")

while since < now:
    try:
        log(f"Fetching from: {pd.to_datetime(since, unit='ms')}")
        candles = exchange.fetch_ohlcv(symbol, timeframe=timeframe, since=since, limit=limit)
        if not candles:
            log("[WARN] No candles returned. Exiting.")
            break
        all_candles.extend(candles)
        since = candles[-1][0] + 60_000
        time.sleep(1.25)
    except Exception as e:
        log(f"[ERROR] {e}")
        time.sleep(3)

# === SAVE ===
if all_candles:
    df = pd.DataFrame(all_candles, columns=["time", "open", "high", "low", "close", "volume"])
    df['time'] = pd.to_datetime(df['time'], unit='ms')
    df.to_csv(output_path, index=False)
    log(f"[SUCCESS] Saved {len(df)} rows to: {output_path}")
else:
    log("[FAILED] No data collected.")