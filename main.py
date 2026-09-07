import os
import json
import google.generativeai as genai
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

TOKEN = os.getenv("TOKEN")
GEMINI_KEY = os.getenv("GOOGLE_API_KEY") # INI UDAH DIGANTI BIAR GA ERROR LAGI

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-2.5-flash') # SAMA KAYA HERMES

MEMORY_FILE = "memory.json"

# STATE BUAT FORM
NAMA, NICHE, PRODUK, TARGET, TONE = range(5)

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
GAYA: Profesional, santai, to the point, pake emoji dan poin. Jangan kepanjangan. Bahasa Indonesia.
DATA CLIENT: {brand_info}
ATURAN: Ingat semua data brand client. Jawab sesuai konteks chat sebelumnya. Kalau disuruh bikinin konten, langsung kasih 5-10 opsi.
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    memory = load_memory()
    
    if user_id not in memory or memory[user_id].get("brand") == "Belum diset":
        text = (
            "👋 Hai! Selamat datang di SMM Agency 🚀\n\n"
            "Seneng banget bisa kenal sama kamu. \n"
            "Aku SMM AI yang bakal bantu ngurusin konten, caption, sampe strategi brand kamu.\n\n"
            "Biar aku bisa bantu maksimal, kita setup brand kamu dulu ya 😊\n"
            "Ketik: /setbrand"
        )
    else:
        brand = memory[user_id]["brand"]
        text = f"👋 Hai {brand}! Balik lagi yaa 🚀\nKetik /setbrand kalau mau update data brand"
    await update.message.reply_text(text)

async def setbrand_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "**Set Brand:**\n\n"
        "1. **Nama Brand**: \n"
        "Contoh: Kopi Senja"
    )
    return NAMA

async def set_nama(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['nama'] = update.message.text
    await update.message.reply_text("2. **Niche**: \nContoh: F&B, Fashion, Skincare, Edukasi")
    return NICHE

async def set_niche(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['niche'] = update.message.text
    await update.message.reply_text("3. **Produk Unggulan**: \nContoh: Kopi Susu Gula Aren 18rb")
    return PRODUK

async def set_produk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['produk'] = update.message.text
    await update.message.reply_text("4. **Target Audience**: \nContoh: Mahasiswa 18-24th, suka nongkrong, budget minim")
    return TARGET

async def set_target(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['target'] = update.message.text
    await update.message.reply_text("5. **Tone Brand**: \nContoh: Santai, Ngak, Edukatif, Profesional")
    return TONE

async def set_tone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    context.user_data['tone'] = update.message.text
    
    # SIMPAN KE MEMORY
    brand_data = {
        "brand": context.user_data['nama'],
        "niche": context.user_data['niche'],
        "produk": context.user_data['produk'],
        "target": context.user_data['target'],
        "tone": context.user_data['tone'],
        "history": []
    }
    
    memory = load_memory()
    memory[user_id] = brand_data
    save_memory(memory)
    
    # BALASAN SETELAH SELESAI SET
    text = (
        f"✅ **Brand Berhasil Diset!**\n\n"
        f"**Nama**: {brand_data['brand']}\n"
        f"**Niche**: {brand_data['niche']}\n"
        f"**Produk**: {brand_data['produk']}\n"
        f"**Target**: {brand_data['target']}\n"
        f"**Tone**: {brand_data['tone']}\n\n"
        f"Siap! Sekarang aku udah kenal banget sama brand kamu 🚀\n\n"
        f"**Ini yang bisa aku lakuin buat kamu:**\n"
        f"1. **Content Plan 30 Hari** - Ketik: `Bikinin plan 30 hari`\n"
        f"2. **Hook & Caption Viral** - Ketik: `Bikinin 10 hook viral`\n"
        f"3. **Script Reel/Tiktok 15s** - Ketik: `Bikin script 15 detik`\n"
        f"4. **Ide Giveaway & Campaign** - Ketik: `Bikinin ide campaign`\n"
        f"5. **Analisa Kompetitor** - Ketik: `Analisa @akun_kompetitor`\n"
        f"6. **Export Text Rapi** - Ketik: `Kirim ke text rapi ya`\n\n"
        f"Langsung spill aja mau dibikinin apa 😁"
    )
    await update.message.reply_text(text)
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Oke dibatalin. Ketik /setbrand lagi kalau mau mulai")
    return ConversationHandler.END

async def hermes_brain(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_msg = update.message.text
    memory = load_memory()
    
    if user_id not in memory:
        await update.message.reply_text("Kita setup brand dulu ya. Ketik /setbrand")
        return
    
    brand_data = memory[user_id]
    brand_info = f"Brand: {brand_data['brand']}, Niche: {brand_data['niche']}, Produk: {brand_data['produk']}, Target: {brand_data['target']}, Tone: {brand_data['tone']}"
    history = brand_data["history"]
    
    history.append({"role": "user", "text": user_msg})
    memory[user_id]["history"] = history[-10:]
    save_memory(memory)
    
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')
    
    try:
        full_prompt = HERMES_PROMPT.format(brand_info=brand_info) + f"\n\nRIWAYAT CHAT: {history}\n\nPERTANYAAN: {user_msg}"
        response = model.generate_content(full_prompt)
        bot_reply = response.text
        
        await update.message.reply_text(bot_reply)
            
        memory[user_id]["history"].append({"role": "bot", "text": bot_reply})
        save_memory(memory)
        
    except Exception as e:
        await update.message.reply_text(f"Maaf kak ada error: {e}")

app = ApplicationBuilder().token(TOKEN).build()

conv_handler = ConversationHandler(
    entry_points=[CommandHandler('setbrand', setbrand_start)],
    states={
        NAMA: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_nama)],
        NICHE: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_niche)],
        PRODUK: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_produk)],
        TARGET: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_target)],
        TONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_tone)],
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)

app.add_handler(CommandHandler("start", start))
app.add_handler(conv_handler)
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, hermes_brain))

print("Bot SMM Agency is running...")
app.run_polling()
