import os
import json
import google.generativeai as genai
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

# FILE BUAT NYIMPEN MEMORY TIAP CLIENT
MEMORY_FILE = "memory.json"

def load_memory():
    try:
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_memory(data):
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f)

HERMES_PROMPT = """
KAMU ADALAH SMM AGENCY AI. Nama kamu "SMM".
TUGAS: Jadi SMM, Scriptwriter, Copywriter, Data Analyst untuk client.
GAYA: Profesional, santai, to the point, pake emoji dan poin. Jangan kepanjangan.
DATA CLIENT: {brand_info}
ATURAN: Ingat nama brand client. Jawab sesuai konteks chat sebelumnya. Kalau diminta bikin plan/table, format pake poin biar rapi.
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    memory = load_memory()
    
    # KALAU CLIENT BARU
    if user_id not in memory:
        memory[user_id] = {"brand": "Belum diset", "history": []}
        save_memory(memory)
        text = (
            "👋 Hai! Selamat datang di SMM Agency 🚀\n\n"
            "Seneng banget bisa kenal sama kamu. \n"
            "Aku SMM AI yang bakal bantu ngurusin konten, caption, sampe strategi brand kamu.\n\n"
            "Biar aku bisa bantu maksimal, boleh tau dulu nama brand kamu apa? 😊\n"
            "Caranya ketik: /setbrand NamaBrandKamu"
        )
    # KALAU CLIENT LAMA
    else:
        brand = memory[user_id]["brand"]
        text = (
            f"👋 Hai {brand}! Balik lagi yaa 🚀\n\n"
            f"Siap bantu kamu hari ini. Ini yang bisa aku lakuin:\n"
            f"1. **Content Plan** - 'Bikinin plan 30 hari niche F&B'\n"
            f"2. **Caption & Hook** - 'Bikinin 10 hook viral kopi 18rb'\n"
            f"3. **Script Video** - 'Bikin script reel 15 detik'\n"
            f"4. **Analisa** - Kirim aja link postingan kamu\n"
            f"5. **Export** - 'Kirim ke text rapi ya'\n\n"
            f"Langsung spill aja mau dibikinin apa 😁"
        )
    await update.message.reply_text(text)

async def setbrand(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if not context.args:
        await update.message.reply_text("Contoh: /setbrand Kopi Senja")
        return
    
    brand_name = ' '.join(context.args)
    memory = load_memory()
    if user_id not in memory:
        memory[user_id] = {"brand": brand_name, "history": []}
    else:
        memory[user_id]["brand"] = brand_name
    save_memory(memory)
    await update.message.reply_text(f"Siap! Aku udah inget brand kamu: **{brand_name}** ✅\nSekarang kita bisa mulai ya")

async def hermes_brain(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_msg = update.message.text
    memory = load_memory()
    
    if user_id not in memory:
        memory[user_id] = {"brand": "Belum diset", "history": []}
    
    brand_info = memory[user_id]["brand"]
    history = memory[user_id]["history"]
    
    # SIMPAN CHAT KE MEMORY
    history.append({"role": "user", "text": user_msg})
    memory[user_id]["history"] = history[-10:] # simpan 10 chat terakhir aja
    save_memory(memory)
    
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')
    
    try:
        full_prompt = HERMES_PROMPT.format(brand_info=brand_info) + f"\n\nRIWAYAT CHAT: {history}\n\nPERTANYAAN: {user_msg}"
        response = model.generate_content(full_prompt)
        bot_reply = response.text
        
        # KALAU MINTA EXPORT
        if "excel" in user_msg.lower() or "export" in user_msg.lower() or "text rapi" in user_msg.lower():
            await update.message.reply_text(f"**Content Plan untuk {brand_info}:**\n\n{bot_reply}\n\n_Tinggal copy paste ke Google Sheet ya ✨_")
        else:
            await update.message.reply_text(bot_reply)
            
        # SIMPAN BALASAN BOT
        memory[user_id]["history"].append({"role": "bot", "text": bot_reply})
        save_memory(memory)
        
    except Exception as e:
        await update.message.reply_text(f"Maaf kak ada error: {e}\nCek API Key Gemini di Railway udah bener belum")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("setbrand", setbrand))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, hermes_brain))

print("Bot SMM Agency is running...")
app.run_polling()
