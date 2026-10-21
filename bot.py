import yfinance as yf
import requests

NTFY_TOPIC = "nii-gold-forex-bot"

def send_ntfy(message, title="Gold Signal"):
    try:
        requests.post(
            f"https://ntfy.sh/{NTFY_TOPIC}",
            data=message.encode('utf-8'),
            headers={
                "Title": title,
                "Priority": "high",
                "Tags": "chart_with_upwards_trend"
            },
            timeout=10
        )
        print(f"Sent: {title} - {message}")
    except Exception as e:
        print(f"ntfy error: {e}")

def main():
    print("Fetching Gold data...")
    try:
        gold = yf.download("GC=F", period="5d", interval="15m", progress=False, auto_adjust=True)
        
        if gold.empty:
            gold = yf.download("XAUUSD=X", period="5d", interval="15m", progress=False, auto_adjust=True)
        
        if gold.empty:
            print("No gold data found")
            return

        close_price = float(gold['Close'].iloc[-1])
        open_price = float(gold['Open'].iloc[-1])
        
        change = ((close_price - open_price) / open_price) * 100
        
        if change > 0.2:
            signal = f"BUY Gold - Up {change:.2f}% | Price: {close_price:.2f}"
        elif change < -0.2:
            signal = f"SELL Gold - Down {change:.2f}% | Price: {close_price:.2f}"
        else:
            signal = f"HOLD Gold - {change:.2f}% | Price: {close_price:.2f}"
        
        print(signal)
        send_ntfy(signal, title="Nii Gold Bot")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        send_ntfy(f"Bot error: {e}", title="Bot Error")

if _name_ == "_main_":
    main()
