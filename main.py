import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("TOKEN")

# INI OTAK HERMES KITA
HERMES_PROMPT = """
KAMU ADALAH: AI SOCIAL MEDIA MANAGER + SCRIPTWRITER + ART DIRECTOR + DATA ANALYST + COPYWRITER
NAMA PANGGILAN: "SMM"
ATURAN: Jawab singkat, to the point, gaya santai tapi profesional. Bisa bikin content plan, caption, analisa, script.
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "👋 Halo! Selamat datang di SMM Agency Bot 🚀\n\n"
        "Aku SMM AI kamu. Bisa bantu:\n"
        "1. Ketik /order buat pesen followers/likes\n"
        "2. Ketik /cek buat cek saldo\n"
        "3. Atau langsung chat aja: 'Bikinin content plan 3 hari niche F&B'\n"
    )
    await update.message.reply_text(text)

async def order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Siap! Mau order platform apa? IG/TikTok/YT\nContoh: IG Followers 1000")

async def cek(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Saldo kamu: Rp 0\nTopup via admin ya kak")

# INI FUNGSI OTAK HERMES
async def hermes_brain(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = update.message.text
    
    # Jawaban simpel dulu, nanti bisa upgrade pake AI beneran
    if "content plan" in user_msg.lower():
        reply = (
            "Siap kak! Ini Content Plan 3 Hari 🔥\n\n"
            "Hari 1: Hook 'Kopi 18rb bikin begadang ilang'\nFormat: Reel | CTA: Komen kopi favorit\n\n"
            "Hari 2: Edukasi '3 Alasan Kopi Mahal'\nFormat: Carousel | CTA: Save\n"
            "Hari 3: Testimoni Mahasiswa\nFormat: Foto + Caption | CTA: Tag temen\n"
            "Mau saya bikinin ke Excel juga?"
        )
    elif "caption" in user_msg.lower():
        reply = "Contoh Caption Santai:\n'Nggak ngopi = nggak waras 😭\nKopi 18rb doang udah bisa begadang produktif.\nLokasi: [Nama Kedai]\n#kopimahasiswa #ngopi18rb'"
    elif "analisa" in user_msg.lower():
        reply = "Kirim link postingan nya kak, nanti aku analisa hook, retention, sama CTA nya"
    else:
        reply = f"Oke kak, aku catat: '{user_msg}'\nMau aku bikinin jadi content plan / caption / script?"
    
    await update.message.reply_text(reply)

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("order", order))
app.add_handler(CommandHandler("cek", cek))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, hermes_brain)) # ini buat chat bebas

print("Bot SMM Hermes is running...")
app.run_polling()
