import yfinance as yf
import pandas as pd
import ta
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Tomar Token ar Admin ID set kora ache
TOKEN = "8849404077:AAGnOH8qhgLlpDA6iY07WA2-TYoXlhHqTN0"
ADMIN_ID = 7602187216  

# Authorization check korar function
def is_boss(user_id):
    return user_id == ADMIN_ID

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_boss(update.message.from_user.id):
        await update.message.reply_text("⛔ Sorry, you are not authorized to use this bot!")
        return

    welcome_msg = (
        "Hello Boss! Ami tomar Market Analysis Bot. 📊\n\n"
        "Live EUR/USD market analysis korte type koro: /signal"
    )
    await update.message.reply_text(welcome_msg)

async def get_signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_boss(update.message.from_user.id):
        await update.message.reply_text("⛔ Access Denied! Ei bot shudhu amar Boss er jonno.")
        return

    await update.message.reply_text("Market data analysis kora hocche. Ektu wait koro Boss... ⏳")
    
    try:
        data = yf.download("EURUSD=X", period="1d", interval="1m", progress=False)
        
        if data.empty:
            await update.message.reply_text("❌ Data fetch korte problem hocche.")
            return

        data['rsi'] = ta.momentum.RSIIndicator(data['Close'], window=14).rsi()
        data['ema_5'] = ta.trend.EMAIndicator(data['Close'], window=5).ema_indicator()
        data['ema_20'] = ta.trend.EMAIndicator(data['Close'], window=20).ema_indicator()
        
        last_close = float(data['Close'].iloc[-1])
        last_rsi = float(data['rsi'].iloc[-1])
        ema_5 = float(data['ema_5'].iloc[-1])
        ema_20 = float(data['ema_20'].iloc[-1])
        
        if last_rsi < 30 and ema_5 > ema_20:
            signal = "🟢 **UP (CALL) Signal!**\n_Reason: Market Oversold & Bullish Crossover._"
        elif last_rsi > 70 and ema_5 < ema_20:
            signal = "🔴 **DOWN (PUT) Signal!**\n_Reason: Market Overbought & Bearish Crossover._"
        else:
            signal = "⚪ **NEUTRAL / NO TRADE!**\n_Reason: Wait for good movement._"
            
        msg = (
            "📊 **Live Market Analysis (EUR/USD - 1M)** 📊\n\n"
            f"**Current Price:** {last_close:.5f}\n"
            f"**RSI (14):** {last_rsi:.2f}\n"
            f"**EMA (5):** {ema_5:.5f} | **EMA (20):** {ema_20:.5f}\n\n"
            f"**Prediction:** {signal}"
        )
        
        await update.message.reply_text(msg, parse_mode='Markdown')
        
    except Exception as e:
        await update.message.reply_text(f"⚠️ Shomossha hoyeche: {e}")

def main():
    print("Trading Bot is starting with Security System...")
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("signal", get_signal))

    app.run_polling()

if __name__ == "__main__":
    main()
