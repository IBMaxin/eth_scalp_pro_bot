import pandas as pd
import os

def list_data_files(prefix):
    return sorted([
        f for f in os.listdir("data") 
        if f.startswith(prefix) and f.endswith(".csv")
    ])

def load_market_data():
    print("📊 Select data source:")
    print("[1] Kraken OHLCV (for scalping)")
    print("[2] CoinGecko Price (for trend testing)")
    choice = input("Enter 1 or 2: ").strip()

    if choice == "1":
        files = list_data_files("eth_usd_kraken")
        print("\nAvailable Kraken files:")
    elif choice == "2":
        files = list_data_files("eth_usd_coingecko")
        print("\nAvailable CoinGecko files:")
    else:
        print("❌ Invalid choice.")
        return None

    for i, f in enumerate(files):
        print(f"[{i}] {f}")
    
    index = input("Select file number: ").strip()
    if not index.isdigit() or int(index) not in range(len(files)):
        print("❌ Invalid selection.")
        return None

    filepath = os.path.join("data", files[int(index)])
    print(f"\n📂 Loading: {filepath}")
    df = pd.read_csv(filepath, parse_dates=['time'])
    df.set_index('time', inplace=True)

    if "open" not in df.columns:
        # Assume CoinGecko price-only data
        df.rename(columns={"price": "close"}, inplace=True)
        df["open"] = df["close"]
        df["high"] = df["close"]
        df["low"] = df["close"]
        df["volume"] = 0.0  # filler

    return df
