import ccxt
import pandas as pd
import time
import os
from datetime import datetime

# === CONFIGURATION ===
symbol = 'ETH/USD'
timeframe = '1h'
days = 90
limit = 720
delay = 1.5
out_dir = "data"
log_file = "logs/fetch_log.txt"

# === INIT EXCHANGE ===
kraken = ccxt.kraken()
since = kraken.parse8601((pd.Timestamp.utcnow() - pd.Timedelta(days=days)).isoformat())
now = kraken.milliseconds()
os.makedirs(out_dir, exist_ok=True)
os.makedirs("logs", exist_ok=True)

output_path = f"{out_dir}/eth_usd_kraken_{days}d_{timeframe}.csv"

# === LOGGING FUNCTION ===
def log(msg):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    line = f"{timestamp} {msg}"
    print(line)
    with open(log_file, "a", encoding="utf-8", errors="ignore") as f:
        f.write(line + "\n")

# === FETCH LOOP ===
log(f"Starting fetch: {symbol}, {timeframe}, {days}d")
all_candles = []

while since < now:
    try:
        log(f"Fetching from: {pd.to_datetime(since, unit='ms')}")
        candles = kraken.fetch_ohlcv(symbol, timeframe=timeframe, since=since, limit=limit)
        if not candles:
            log("[WARN] No candles returned. Exiting loop.")
            break
        all_candles.extend(candles)
        since = candles[-1][0] + 60_000  # Skip forward 1 minute
        time.sleep(delay)
    except Exception as e:
        log(f"[ERROR] {str(e)}")
        time.sleep(delay + 1)

# === SAVE DATA ===
if all_candles:
    df = pd.DataFrame(all_candles, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
    df['time'] = pd.to_datetime(df['time'], unit='ms')
    df.to_csv(output_path, index=False)
    log(f"[OK] Saved to: {output_path}")
else:
    log("[FAIL] No data collected.")
