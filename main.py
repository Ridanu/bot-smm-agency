import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.getenv("TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Halo! Selamat datang di SMM Agency Bot 🚀\n\n"
        "Ketik /order buat pesen followers/likes\n"
        "Ketik /cek buat cek saldo"
    )

async def order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Mau order apa kak? Followers IG, TikTok, YT?")

async def cek(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Saldo kamu: Rp 0")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("order", order))
app.add_handler(CommandHandler("cek", cek))
print("Bot SMM is running...")
app.run_polling()