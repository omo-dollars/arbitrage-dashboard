import streamlit as st
import requests
import sqlite3
import time
from datetime import datetime

#---------------------- SETTINGS ----------------------

TOP_CHAINS = ["BSC", "Polygon", "Solana", "Arbitrum", "Optimism", "Base", "Sonic", "Sui", "Sei", "Mantle"]

Pre-selected top 20 tokens (volume, volatility, profitability based)

TOP_TOKENS = [
"USDT", "USDC", "WBTC", "WETH", "AVAX", "MATIC", "SHIB", "PEPE",
"DOGE", "LINK", "UNI", "DAI", "CAKE", "ARBI", "SUI", "SEI",
"OP", "FTM", "SOL", "BNB"
]

# Telegram Bot Settings (replace with your own)

TELEGRAM_BOT_TOKEN = "your_bot_token_here"
TELEGRAM_CHAT_ID = "your_chat_id_here"

#---------------------- FUNCTIONS ----------------------

def send_telegram_alert(message):
url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
try:
requests.post(url, data=payload)
except:
pass

def save_to_db(data):
conn = sqlite3.connect("arbitrage_logs.db")
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS logs (timestamp TEXT, chain TEXT, token TEXT, profit REAL)")
c.execute("INSERT INTO logs VALUES (?, ?, ?, ?)", (data["timestamp"], data["chain"], data["token"], data["profit"]))
conn.commit()
conn.close()

# Dummy function to simulate fetching arbitrage opportunities

def fetch_arbitrage_opportunities():
result = []
for chain in TOP_CHAINS:
for token in TOP_TOKENS:
profit = round((0.5 - 0.1) * requests.get("https://www.randomnumberapi.com/api/v1.0/random?min=1&max=10&count=1").json()[0] / 100, 4)
if profit > 0.03:
data = {
"timestamp": datetime.utcnow().isoformat(),
"chain": chain,
"token": token,
"profit": profit
}
save_to_db(data)
send_telegram_alert(f"Profitable arbitrage on {chain}: {token} ➜ {profit*100}%")
result.append(data)
return result

#---------------------- STREAMLIT APP ----------------------

st.set_page_config(page_title="Multi-Chain Arbitrage Dashboard", layout="wide")
st.title("🚀 Real-Time Multi-Chain Arbitrage Dashboard")

if st.button("🔍 Scan for Arbitrage Opportunities"):
st.info("Scanning networks... Please wait.")
with st.spinner("Looking for profitable trades..."):
results = fetch_arbitrage_opportunities()
if results:
st.success(f"Found {len(results)} profitable opportunities!")
for res in results:
st.write(f"[{res['timestamp']}] 💰 {res['token']} on {res['chain']} — Profit: {res['profit']*100}%")
else:
st.warning("No arbitrage opportunities found right now. Try again later.")

st.markdown("---")
st.subheader("📊 Arbitrage Opportunity Log")

conn = sqlite3.connect("arbitrage_logs.db")
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS logs (timestamp TEXT, chain TEXT, token TEXT, profit REAL)")
logs = c.execute("SELECT * FROM logs ORDER BY timestamp DESC LIMIT 50").fetchall()
conn.close()

if logs:
for row in logs:
st.code(f"[{row[0]}] {row[2]} on {row[1]} → {round(row[3]*100, 2)}%")
else:
st.info("No logs yet. Run a scan to populate data.")

st.markdown("---")
st.caption("Built with ❤️ using Streamlit — 100% free-tier friendly.")

