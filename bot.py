import yfinance as yf
import pandas as pd
import requests
from datetime import datetime

NTFY_TOPIC = "nii-gold-forex-bot"

def send_push(title, message):
    try:
        requests.post(
            f"https://ntfy.sh/{NTFY_TOPIC}",
            data=message.encode('utf-8'),
            headers={"Title": title, "Priority": "high"}
        )
        print(f"PUSH SENT: {title}")
    except Exception as e:
        print(e)

SYMBOLS = {
    "EURUSD=X": "EURUSD",
    "GBPUSD=X": "GBPUSD", 
    "GC=F": "GOLD",
    "BTC-USD": "BTC",
    "ETH-USD": "ETH"
}

def get_signal(symbol):
    df = yf.download(symbol, period="3d", interval="15m", progress=False, auto_adjust=True)
    if len(df) < 200:
        return None, None
    df['EMA50'] = df['Close'].ewm(span=50).mean()
    df['EMA200'] = df['Close'].ewm(span=200).mean()
    df['ATR'] = (df['High'] - df['Low']).rolling(14).mean()
    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = -delta.where(delta < 0, 0).rolling(14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    last = df.iloc[-1]
    atr_val = float(last['ATR']) if not pd.isna(last['ATR']) else float(last['Close']*0.002)
    price = float(last['Close'])
    if last['Close'] > last['EMA50'] > last['EMA200'] and 55 < last['RSI'] < 70:
        return "BUY NOW", f"{symbol} BUY at {price:.2f} SL {price - atr_val*1.5:.2f} TP {price + atr_val*3:.2f}"
    if last['Close'] < last['EMA50'] < last['EMA200'] and 30 < last['RSI'] < 45:
        return "SELL NOW", f"{symbol} SELL at {price:.2f} SL {price + atr_val*1.5:.2f} TP {price - atr_val*3:.2f}"
    return None, None

print("Scanning...")
for sym in SYMBOLS:
    title, msg = get_signal(sym)
    if title:
        send_push(f"{title} - {SYMBOLS[sym]}", msg)

# send test once per day at 8AM
now = datetime.utcnow()
if now.hour == 8 and now.minute < 15:
    send_push("Bot Active", "Nii, Gold+Forex scanner running 8-11AM Ghana time")
