import yfinance as yf
import requests
from concurrent.futures import ThreadPoolExecutor

NTFY_TOPIC = "nii-gold-forex-bot"

SYMBOLS = {
    # FOREX + GOLD
    "GOLD": "GC=F",
    "EURUSD": "EURUSD=X",
    "GBPUSD": "GBPUSD=X",
    "USDJPY": "USDJPY=X",
    "USDCHF": "USDCHF=X",
    "AUDUSD": "AUDUSD=X",
    "NZDUSD": "NZDUSD=X",
    "USDCAD": "USDCAD=X",
    "EURJPY": "EURJPY=X",
    # CRYPTO
    "BTC": "BTC-USD",
    "ETH": "ETH-USD",
    "SOL": "SOL-USD",
    "BNB": "BNB-USD",
    "XRP": "XRP-USD",
    "DOGE": "DOGE-USD",
    "ADA": "ADA-USD"
}

def send_ntfy(message, title):
    try:
        requests.post(
            f"https://ntfy.sh/{NTFY_TOPIC}",
            data=message.encode('utf-8'),
            headers={"Title": title, "Priority": "high"},
            timeout=10
        )
    except Exception as e:
        print(f"ntfy error: {e}")

def fetch_one(item):
    name, ticker = item
    try:
        data = yf.download(ticker, period="1d", interval="15m", progress=False, auto_adjust=True, threads=False)
        if data.empty:
            return f"{name}: No data"
        close = float(data['Close'].iloc[-1])
        open_p = float(data['Open'].iloc[-1])
        change = ((close - open_p) / open_p) * 100
        
        if change > 0.3:
            icon = "🟢 BUY"
        elif change < -0.3:
            icon = "🔴 SELL"
        else:
            icon = "⚪ HOLD"
        
        return f"{icon} {name}: {change:+.2f}% @ {close:.2f}"
    except Exception as e:
        return f"{name}: Error"

def main():
    print(f"Fetching {len(SYMBOLS)} symbols fast...")
    with ThreadPoolExecutor(max_workers=8) as executor:
        results = list(executor.map(fetch_one, SYMBOLS.items()))
    
    for r in results:
        print(r)
    
    final_msg = "\n".join(results)
    
    # Split into 2 messages if too long for ntfy
    send_ntfy(final_msg, title=f"Nii Bot: {len(results)} Markets")
    print("Done - sent to ntfy")

if _name_ == "_main_":
    main()
