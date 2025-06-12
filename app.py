import streamlit as st
import requests
import sqlite3
from datetime import datetime

# ---------------------- SETTINGS ----------------------

TOP_CHAINS = ["BSC", "Polygon", "Solana", "Arbitrum", "Optimism", "Base", "Sonic", "Sui", "Sei", "Mantle"]

TOP_TOKENS = [
    "USDT", "USDC", "WBTC", "WETH", "AVAX", "MATIC", "SHIB", "PEPE",
    "DOGE", "LINK", "UNI", "DAI", "CAKE", "ARBI", "SUI", "SEI",
    "OP", "FTM", "SOL", "BNB"
]

# 🔐 Telegram Bot Settings — fill these in
TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN"
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID"

# ---------------------- FUNCTIONS ----------------------

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print("Telegram alert failed:", e)

def save_to_db(data):
    conn = sqlite3.connect("arbitrage_logs.db")
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS logs (timestamp TEXT, chain TEXT, token TEXT, profit REAL)")
    c.execute("INSERT INTO logs VALUES (?, ?, ?, ?)", (data["timestamp"], data["chain"], data["token"], data["profit"]))
    conn.commit()
    conn.close()

def fetch_arbitrage_opportunities():
    result = []
    for chain in TOP_CHAINS:
        for token in TOP_TOKENS:
            try:
                mock = requests.get("https://www.randomnumberapi.com/api/v1.0/random?min=1&max=10&count=1").json()[0]
                profit = round(0.005 * mock, 4)
                if profit > 0.03:
                    data = {
                        "timestamp": datetime.utcnow().isoformat(),
                        "chain": chain,
                        "token": token,
                        "profit": profit
                    }
                    save_to_db(data)
                    send_telegram_alert(f"🤑 {token} on {chain} → {round(profit*100, 2)}% profit")
                    result.append(data)
            except:
                continue
    return result

# ---------------------- UI ----------------------

st.set_page_config(page_title="Arbitrage Scanner", layout="wide")
st.title("🧠 Multi-Chain Arbitrage Opportunity Dashboard")

if st.button("🔍 Scan Now"):
    with st.spinner("Scanning for profitable trades..."):
        results = fetch_arbitrage_opportunities()
    if results:
        st.success(f"{len(results)} profitable trades found!")
        for r in results:
            st.write(f"[{r['timestamp']}] {r['token']} on {r['chain']} — 💸 {round(r['profit']*100, 2)}%")
    else:
        st.warning("No arbitrage found. Try again soon!")

st.markdown("---")
st.subheader("📊 Recent Logs")

conn = sqlite3.connect("arbitrage_logs.db")
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS logs (timestamp TEXT, chain TEXT, token TEXT, profit REAL)")
logs = c.execute("SELECT * FROM logs ORDER BY timestamp DESC LIMIT 50").fetchall()
conn.close()

if logs:
    for row in logs:
        st.code(f"[{row[0]}] {row[2]} on {row[1]} → {round(row[3]*100, 2)}%")
else:
    st.info("No scan logs yet.")
