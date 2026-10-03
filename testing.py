import psutil
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ========== اپنی معلومات یہاں درج کریں ==========
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
CHAT_ID = 123456789  # اپنا عددی چیٹ آئی ڈی

# جس پروگرام/سروس کو مانیٹر کرنا ہے، اس کا نام یہاں لکھیں
# مثال: "nginx", "python", "node", "sshd"
PROCESS_NAME = "python"
# ==================================================

def is_process_running(process_name):
    """چیک کرتا ہے کہ دیا گیا پروسیس چل رہا ہے یا نہیں"""
    for proc in psutil.process_iter(['name']):
        try:
            if process_name.lower() in proc.info['name'].lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """جب آپ /status بھیجیں تو جواب دے"""
    if update.effective_chat.id != CHAT_ID:
        await update.message.reply_text("آپ مجاز صارف نہیں ہیں۔")
        return

    running = is_process_running(PROCESS_NAME)
    if running:
        await update.message.reply_text(f"✅ پروسیس '{PROCESS_NAME}' ابھی بھی چل رہا ہے (آن لائن ہے)۔")
    else:
        await update.message.reply_text(f"❌ پروسیس '{PROCESS_NAME}' بند ہو چکا ہے (آف لائن ہے)۔")

async def auto_monitor(app):
    """ہر 30 سیکنڈ بعد خودکار چیک کر کے اطلاع بھیجتا ہے"""
    last_status = None
    while True:
        running = is_process_running(PROCESS_NAME)
        if last_status is not None and last_status != running:
            if running:
                await app.bot.send_message(chat_id=CHAT_ID, text=f"🔔 پروسیس '{PROCESS_NAME}' دوبارہ شروع ہو گیا ہے!")
            else:
                await app.bot.send_message(chat_id=CHAT_ID, text=f"⚠️ پروسیس '{PROCESS_NAME}' بند ہو گیا ہے!")
        last_status = running
        await asyncio.sleep(30)  # 30 سیکنڈ کا وقفہ

async def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("status", status_command))

    # پس منظر میں خودکار مانیٹرنگ شروع کریں
    asyncio.create_task(auto_monitor(application))

    print(f"بوٹ چل رہا ہے... پروسیس '{PROCESS_NAME}' کی نگرانی ہو رہی ہے۔")
    await application.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
