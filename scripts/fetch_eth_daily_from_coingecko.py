import requests
import pandas as pd
from datetime import datetime

# Settings
vs_currency = 'usd'
days = 90  # You can change this to 7, 30, 180, 365, or 'max'

url = f'https://api.coingecko.com/api/v3/coins/ethereum/market_chart?vs_currency={vs_currency}&days={days}'

print(f"🔄 Fetching ETH/USD daily prices for last {days} days from CoinGecko...")
r = requests.get(url)
data = r.json()

# Convert timestamps + prices
prices = data['prices']
df = pd.DataFrame(prices, columns=['timestamp', 'price'])
df['time'] = pd.to_datetime(df['timestamp'], unit='ms')
df.set_index('time', inplace=True)
df.drop(columns=['timestamp'], inplace=True)

# Save
filename = f"data/eth_usd_coingecko_{days}d.csv"
df.to_csv(filename)

print(f"✅ Saved {len(df)} rows to {filename}")
