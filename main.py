import os
import json
import google.generativeai as genai
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("TOKEN")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-3.6-flash')

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

# 1. UBAH SYSTEM PROMPT BIAR LOCKED 5 MENU SAJA
HERMES_PROMPT = """
Kamu adalah SMM Agency AI bernama SMM. Spesialismu hanya 5 hal untuk brand client.

5 TUGAS UTAMA KAMU:
1. Bikinin Content Plan 30 Hari
2. Bikinin 10 Hook dan Caption Viral
3. Bikin Script Reel Tiktok 15 detik
4. Bikinin Ide Giveaway dan Campaign
5. Analisa Kompetitor

ATURAN KERAS YANG WAJIB DIINGAT:
- Data Brand Client: {brand_info}
- Gaya: Santai, profesional, to the point, pakai emoji dan poin. Bahasa Indonesia.
- JANGAN PERNAH GUNAKAN TANDA BINTANG ** DI JAWABAN.
- JIKA USER BERTANYA DI LUAR 5 HAL DI ATAS, KAMU WAJIB MENOLAK.
- Jawaban penolakan: "Maaf kak, aku spesialis SMM untuk {brand_name} aja ya 🙏 Mau aku bikinin konten tentang itu?"
- Dilarang jawab: resep, harga bahan, cara buka usaha, teknis, atau hal diluar marketing.
- Ingat data brand dan riwayat chat. Jawab sesuai konteks Kopi Senja.

RIWAYAT CHAT: {history}
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    memory = load_memory()

    if user_id not in memory:
        text = (
            "Hai Selamat datang di SMM Agency \n\n"
            "Seneng banget bisa kenal sama kamu.\n"
            "Aku SMM AI yang bakal bantu ngurusin konten, caption, sampai strategi brand kamu.\n\n"
            "Biar aku bisa bantu maksimal, kita setup brand kamu dulu ya \n"
            "Ketik: /setbrand"
        )
    else:
        brand = memory[user_id]["brand"]
        text = f"Hai {brand} Balik lagi ya \nKetik /setbrand kalau mau update data brand\nMenu aku:\n1. Content Plan\n2. Hook + Caption\n3. Script Reels\n4. Giveaway\n5. Analisa Kompetitor"
    await update.message.reply_text(text)

async def setbrand(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    context.user_data[user_id] = "nunggu_form"

    text = (
        "Set Brand :\n"
        "Nama Brand :\n"
        "Niche :\n"
        "Produk :\n"
        "Target :\n"
        "Tone :\n\n"
        "Silakan isi semua di atas dan kirim sekaligus ya"
    )
    await update.message.reply_text(text)

async def terima_pesan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_msg = update.message.text
    memory = load_memory()

    # CEK APA LAGI NUNGGU ISI FORM
    if context.user_data.get(user_id) == "nunggu_form":
        teks = user_msg.split("\n")
        data = {}
        for baris in teks:
            if "Nama Brand" in baris:
                data["brand"] = baris.split(":")[1].strip()
            if "Niche" in baris:
                data["niche"] = baris.split(":")[1].strip()
            if "Produk" in baris:
                data["produk"] = baris.split(":")[1].strip()
            if "Target" in baris:
                data["target"] = baris.split(":")[1].strip()
            if "Tone" in baris:
                data["tone"] = baris.split(":")[1].strip()

        if "brand" in data:
            data["history"] = []
            memory[user_id] = data
            save_memory(memory)
            context.user_data[user_id] = "selesai"

            text = (
                f"Siap Aku udah inget brand kamu: {data['brand']} \n\n"
                f"Detail Brand:\n"
                f"Nama: {data['brand']}\n"
                f"Niche: {data['niche']}\n"
                f"Produk: {data['produk']}\n"
                f"Target: {data['target']}\n"
                f"Tone: {data['tone']}\n\n"
                f"Sekarang kita bisa mulai ya \n\n"
                f"Ini yang bisa aku lakuin buat kamu:\n"
                f"1. Bikinin Content Plan 30 Hari\n"
                f"2. Bikinin 10 Hook dan Caption Viral\n"
                f"3. Bikin Script Reel Tiktok 15 detik\n"
                f"4. Bikinin Ide Giveaway dan Campaign\n"
                f"5. Analisa Kompetitor\n"
                f"Langsung spill aja mau dibikinin apa"
            )
            await update.message.reply_text(text)
            return
        else:
            await update.message.reply_text("Formatnya belum bener kak. Copy form dari atas lalu isi ya")
            return

    # KALAU BUKAN LAGI ISI FORM, BERARTI CHAT BIASA KE GEMINI
    if user_id not in memory:
        await update.message.reply_text("Kita setup brand dulu ya. Ketik /setbrand")
        return

    brand_data = memory[user_id]
    brand_info = f"Brand: {brand_data['brand']}, Niche: {brand_data['niche']}, Produk: {brand_data['produk']}, Target: {brand_data['target']}, Tone: {brand_data['tone']}"
    brand_name = brand_data['brand']
    history = brand_data.get("history", [])

    history.append({"role": "user", "text": user_msg})
    memory[user_id]["history"] = history[-10:]
    save_memory(memory)

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')

    try:
        # 2. MASUKIN HISTORY DAN BRAND_NAME KE PROMPT
        history_str = json.dumps(history, ensure_ascii=False)
        full_prompt = HERMES_PROMPT.format(brand_info=brand_info, brand_name=brand_name, history=history_str) + f"\n\nPERTANYAAN TERBARU: {user_msg}"

        response = model.generate_content(full_prompt)
        bot_reply = response.text

        await update.message.reply_text(bot_reply)

        memory[user_id]["history"].append({"role": "bot", "text": bot_reply})
        memory[user_id]["history"] = memory[user_id]["history"][-10:]
        save_memory(memory)

    except Exception as e:
        if "429" in str(e):
            await update.message.reply_text("Lagi kena limit dari Google AI kak. Tunggu 1 menit ya 🙏")
        else:
            await update.message.reply_text(f"Maaf ada error: {e}")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("setbrand", setbrand))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, terima_pesan))

print("Bot SMM Agency is running...")
app.run_polling()
