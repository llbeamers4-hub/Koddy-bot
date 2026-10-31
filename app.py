import os
import yfinance as yf
import ta
from flask import Flask
import threading
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# === SETTINGS ===
BOT_TOKEN = os.getenv("BOT_TOKEN", "PUT_YOUR_BOT_TOKEN_HERE")
ACCESS_KEY = os.getenv("ACCESS_KEY", "82925") # Change this to your secret key

AUTHORIZED_USERS = set()

app = Flask(__name__)

def get_gold_signal():
    data = yf.download("GC=F", period="5d", interval="15m")
    close = data['Close']
    rsi = ta.momentum.RSIIndicator(close).rsi().iloc[-1]
    ema20 = ta.trend.EMAIndicator(close, window=20).ema_indicator().iloc[-1]
    ema50 = ta.trend.EMAIndicator(close, window=50).ema_indicator().iloc[-1]
    price = float(close.iloc[-1])

    if rsi < 35 and price > ema20:
        signal = "BUY 🟢"
    elif rsi > 65 and price < ema20:
        signal = "SELL 🔴"
    else:
        signal = "HOLD ⚪"

    trend = "BULLISH" if ema20 > ema50 else "BEARISH"
    return price, rsi, trend, signal

# === TELEGRAM LOGIC ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in AUTHORIZED_USERS:
        await update.message.reply_text("Welcome back Boss! Send /signal for GOLD signal.")
    else:
        await update.message.reply_text(
            "🔒 Koddy-bot is Private.\n\nPlease enter Access Key to unlock:\n\nExample: /key KODDY2025"
        )

async def check_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not context.args:
        await update.message.reply_text("Usage: /key YOUR_ACCESS_KEY")
        return
    key = context.args[0]
    if key == ACCESS_KEY:
        AUTHORIZED_USERS.add(user_id)
        await update.message.reply_text("✅ Access Granted! Welcome.\n\nSend /signal to get GOLD analysis.")
    else:
        await update.message.reply_text("❌ Wrong key! Contact owner to buy access.")

async def signal_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in AUTHORIZED_USERS:
        await update.message.reply_text("🔒 You need Access Key first. Send /key YOUR_KEY")
        return
    
    await update.message.reply_text("⏳ Analyzing GOLD...")
    try:
        price, rsi, trend, signal = get_gold_signal()
        msg = f"""💰 Koddy-bot GOLD ANALYSIS

Price: ${price:.2f}
Signal: {signal}
RSI: {rsi:.2f}
Trend: {trend}

Timeframe: 15m"""
        await update.message.reply_text(msg)
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

def run_telegram():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("key", check_key))
    application.add_handler(CommandHandler("signal", signal_cmd))
    application.run_polling()

@app.route('/')
def home():
    return "Koddy-bot is Running! Telegram bot is active."

# Start Telegram in background
threading.Thread(target=run_telegram, daemon=True).start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
