import ccxt
import pandas as pd
import time
from datetime import datetime, timedelta

# Prompt user for number of days
try:
    days = int(input("How many days of 1-minute ETH/USD data would you like to fetch? (e.g. 7, 30, 90): "))
except ValueError:
    print("Invalid input. Please enter a number.")
    exit()

print(f"\n📦 Fetching {days} days of 1-minute OHLCV data from Kraken...")

exchange = ccxt.kraken()
symbol = 'ETH/USD'
timeframe = '1m'
limit = 720  # Kraken max per call (12 hours)
ms_per_candle = 60_000

# Define start and end time
end_time = int(time.time() * 1000)  # now
since = exchange.parse8601(
    (pd.Timestamp.utcnow() - timedelta(days=days)).strftime('%Y-%m-%dT%H:%M:%S')
)

all_candles = []

# Paginate until full range is fetched
while since < end_time:
    print(f"🔄 Fetching from {datetime.utcfromtimestamp(since / 1000)}...")
    try:
        candles = exchange.fetch_ohlcv(symbol, timeframe, since=since, limit=limit)
    except Exception as e:
        print(f"⚠️ Error fetching data: {e}")
        break

    if not candles:
        break

    all_candles.extend(candles)
    since = candles[-1][0] + ms_per_candle

    if len(candles) < limit:
        break

    time.sleep(1.2)  # Respect Kraken rate limits

# Process into DataFrame
df = pd.DataFrame(all_candles, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
df['time'] = pd.to_datetime(df['timestamp'], unit='ms')
df.set_index('time', inplace=True)
df.drop(columns=['timestamp'], inplace=True)

# Save to file
output_path = f"data/eth_usd_kraken_{days}d.csv"
df.to_csv(output_path)

print(f"\n✅ Done. Saved {len(df)} rows covering {df.index.min()} to {df.index.max()}")
