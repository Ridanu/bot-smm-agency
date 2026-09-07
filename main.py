import os
import google.generativeai as genai
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

HERMES_PROMPT = """
KAMU ADALAH SMM AGENCY AI. Nama kamu "SMM".
Gaya: Santai, to the point, pake emoji, pake poin. Ahli di content plan, caption, script, hook, analisa.
Aturan: Jawab langsung solusi. Kalau diminta bikin tabel/plan bilang "mau aku kirim ke excel?"
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "👋 Halo! Aku SMM AI kamu 🚀\n\n"
        "Bisa bantu:\n"
        "1. `/order` - Pesen followers/likes\n"
        "2. `/cek` - Cek saldo\n"
        "3. Chat bebas - 'Bikinin caption kopi 18rb' / 'Bikin 10 hook viral'\n"
    )
    await update.message.reply_text(text)

async def order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Siap! Mau order apa kak?\nContoh: IG Followers 1000, TikTok Likes 5000")

async def cek(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Saldo kamu: Rp 0\nHubungi admin buat topup ya")

async def hermes_brain(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = update.message.text
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')
    
    try:
        full_prompt = f"{HERMES_PROMPT}\n\nPERTANYAAN USER: {user_msg}"
        response = model.generate_content(full_prompt)
        await update.message.reply_text(response.text)
    except Exception as e:
        await update.message.reply_text(f"Maaf kak error: {e}\nCek API Key Gemini di Railway udah bener belum")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("order", order))
app.add_handler(CommandHandler("cek", cek))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, hermes_brain))

print("Bot SMM Hermes Gemini is running...")
app.run_polling()
