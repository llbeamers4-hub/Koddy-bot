import os
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler

BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_KEY = "KODDY2026"
AUTHORIZED_USERS = set()
app = Flask(__name__)

def get_gold_signal():
    return 2650.5, 65.5, "BULLISH", "BUY"

async def start_cmd(update, context):
    await update.message.reply_text("Koddy-bot Running! Use /key KODDY2026")

async def key_cmd(update, context):
    uid = update.effective_user.id
    if not context.args:
        await update.message.reply_text("Usage: /key KODDY2026")
        return
    if context.args[0] == ADMIN_KEY:
        AUTHORIZED_USERS.add(uid)
        await update.message.reply_text("Access Granted! Use /signal")
    else:
        await update.message.reply_text("Wrong key!")

async def signal_cmd(update, context):
    uid = update.effective_user.id
    if uid not in AUTHORIZED_USERS:
        await update.message.reply_text("Need access! Use /key KODDY2026")
        return
    await update.message.reply_text("Analyzing GOLD...")
    try:
        price, rsi, trend, signal = get_gold_signal()
        msg = f"GOLD ANALYSIS\nPrice: ${price}\nSignal: {signal}\nRSI: {rsi}\nTrend: {trend}"
        await update.message.reply_text(msg)
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

application = Application.builder().token(BOT_TOKEN).build()
application.add_handler(CommandHandler("start", start_cmd))
application.add_handler(CommandHandler("key", key_cmd))
application.add_handler(CommandHandler("signal", signal_cmd))

@app.route('/', methods=['GET'])
def home():
    return "Koddy-bot is Running!"

@app.route('/', methods=['POST'])
async def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, application.bot)
    await application.initialize()
    await application.process_update(update)
    return "ok"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
