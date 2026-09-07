import os
import google.generativeai as genai
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

# SETUP GEMINI FLASH
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

HERMES_PROMPT = """
KAMU ADALAH: AI SOCIAL MEDIA MANAGER + SCRIPTWRITER + ART DIRECTOR + DATA ANALYST + COPYWRITER
NAMA PANGGILAN: "SMM"
TUGAS: Jawab singkat, to the point, gaya santai tapi profesional. Bisa bikin content plan, caption, analisa, script, ide viral.
FORMAT JAWAB: Pakai emoji, poin-poin, dan CTA. Kalau diminta spreadsheet bilang "siap aku buatin file nya"
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "👋 Halo! Aku SMM AI kamu 🚀\nLangsung chat aja: 'Bikinin content plan 3 hari niche F&B'"
    await update.message.reply_text(text)

async def order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Siap! Mau order platform apa? IG/TikTok/YT\nContoh: IG Followers 1000")

async def hermes_brain(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = update.message.text
    await update.message.reply_text("Sedang mikir... 🤔")
    
    try:
        full_prompt = f"{HERMES_PROMPT}\n\nPERTANYAAN USER: {user_msg}"
        response = model.generate_content(full_prompt)
        await update.message.reply_text(response.text)
    except Exception as e:
        await update.message.reply_text(f"Ada error kak: {e}")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("order", order))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, hermes_brain))

print("Bot SMM Hermes Gemini is running...")
app.run_polling()
