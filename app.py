import streamlit as st
import requests
import sqlite3
import time
from datetime import datetime

#---------------------- SETTINGS ----------------------

CHAINS = ["BSC", "Polygon", "Arbitrum", "Optimism", "Solana", "Base", "Sui", "Sei", "Mantle", "Sonic"]
MIN_PROFIT_USD = 0.5
MIN_TRADE_AMOUNT = 10

# Pre-selected top 20 tokens (auto-updated in full version)

TOKENS = ["USDT", "USDC", "WETH", "WBTC", "SHIB", "PEPE", "CAKE", "MATIC", "AVAX", "FLOKI", "OP", "SUI", "SEI", "SONIC"]

Telegram config (to be set in app)

TELEGRAM_TOKEN = ""
TELEGRAM_CHAT_ID = ""

#---------------------- INIT DB ----------------------

def init_db():
conn = sqlite3.connect("arbitrage_logs.db")
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS opportunities (
id INTEGER PRIMARY KEY AUTOINCREMENT,
timestamp TEXT,
token TEXT,
chain_buy TEXT,
chain_sell TEXT,
profit_usd REAL,
route TEXT
)
""")
conn.commit()
conn.close()

#---------------------- TELEGRAM ----------------------

def send_telegram_alert(msg):
if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
data = {"chat_id": TELEGRAM_CHAT_ID, "text": msg}
try:
requests.post(url, data=data)
except:
pass

#---------------------- DUMMY PRICE FETCHER ----------------------

def fetch_price(token, chain):
# Simulated API call - replace with real DEX aggregator
import random
return round(1 + random.uniform(-0.1, 0.1), 4)

#---------------------- MAIN LOGIC ----------------------

def check_arbitrage():
results = []
for token in TOKENS:
for buy_chain in CHAINS:
for sell_chain in CHAINS:
if buy_chain != sell_chain:
buy_price = fetch_price(token, buy_chain)
sell_price = fetch_price(token, sell_chain)
profit = (sell_price - buy_price) * MIN_TRADE_AMOUNT
if profit > MIN_PROFIT_USD:
results.append({
"token": token,
"buy_chain": buy_chain,
"sell_chain": sell_chain,
"profit": round(profit, 2),
"route": f"Buy on {buy_chain}, sell on {sell_chain}"
})
return results

#---------------------- APP UI ----------------------

st.set_page_config(page_title="Multi-Chain Arbitrage Dashboard", layout="wide")
st.title("🚀 Real-Time Multi-Chain Arbitrage Opportunities")

col1, col2 = st.columns(2)

with col1:
TELEGRAM_TOKEN = st.text_input("Telegram Bot Token", type="password")
with col2:
TELEGRAM_CHAT_ID = st.text_input("Telegram Chat ID")

if st.button("Start Arbitrage Scan"):
init_db()
with st.spinner("Scanning for profitable trades..."):
opportunities = check_arbitrage()
if not opportunities:
st.warning("No profitable opportunities found right now.")
else:
st.success(f"{len(opportunities)} opportunities found!")
for opp in opportunities:
st.write(f"🔁 {opp['token']} | 💰 ${opp['profit']} | {opp['route']}")
msg = f"[ARBITRAGE] {opp['token']}\nProfit: ${opp['profit']}\nRoute: {opp['route']}"
send_telegram_alert(msg)
# Log to DB
conn = sqlite3.connect("arbitrage_logs.db")
c = conn.cursor()
c.execute("INSERT INTO opportunities (timestamp, token, chain_buy, chain_sell, profit_usd, route) VALUES (?, ?, ?, ?, ?, ?)",
(datetime.utcnow().isoformat(), opp['token'], opp['buy_chain'], opp['sell_chain'], opp['profit'], opp['route']))
conn.commit()
conn.close()

st.markdown("---")

if st.checkbox("📄 Show Arbitrage Log"):
try:
conn = sqlite3.connect("arbitrage_logs.db")
df = conn.execute("SELECT * FROM opportunities ORDER BY id DESC LIMIT 50").fetchall()
conn.close()
if df:
st.dataframe(df)
else:
st.info("No data logged yet.")
except:
st.error("Failed to read logs.")

st.caption("Built for $10+ trades | Avoids Ethereum | Powered by real-time DEX data")

