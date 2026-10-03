import win32ts
import win32api
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# ========== اپنی ٹیلی گرام بوٹ کی معلومات یہاں درج کریں ==========
BOT_TOKEN = "8963965367:AAF-pJFc6W3Nx1z9_rr2YIdWSX7AtutwuCU"
CHAT_ID = 5415781142  # اپنا عددی چیٹ آئی ڈی یہاں لکھیں
# ==============================================================

def check_rdp_session():
    """
    RDP سیشن کی موجودہ حالت چیک کرتا ہے۔
    اگر کوئی ایکٹو RDP سیشن ملے تو True، ورنہ False واپس کرتا ہے۔
    """
    try:
        # مقامی مشین کے تمام سیشنز حاصل کریں
        sessions = win32ts.WTSEnumerateSessions(win32ts.WTS_CURRENT_SERVER_HANDLE, 0, 1)
        for session in sessions:
            # صرف وہ سیشنز دیکھیں جن کا نام RDP سے شروع ہو اور حالت Active ہو
            if session.get('WinStationName', '').startswith('RDP-Tcp'):
                if session.get('State') == win32ts.WTSActive:
                    return True
    except Exception as e:
        print(f"RDP سیشن چیک کرنے میں خرابی: {e}")
    return False

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    جب صارف /status کمانڈ بھیجے تو RDP سیشن کی حالت کا جواب دے۔
    """
    # صرف مجاز چیٹ آئی ڈی سے آنے والے میسجز پر عمل کریں
    if update.effective_chat.id != CHAT_ID:
        await update.message.reply_text("آپ اس بوٹ کے مجاز صارف نہیں ہیں۔")
        return

    is_online = check_rdp_session()
    if is_online:
        await update.message.reply_text("✅ RDP سیشن آن لائن ہے (ایکٹو)۔")
    else:
        await update.message.reply_text("❌ RDP سیشن آف لائن ہے (کوئی ایکٹو سیشن نہیں)۔")

def main():
    """
    بوٹ کو شروع کرنے اور /status کمانڈ کو ہینڈل کرنے کا مین فنکشن۔
    """
    # بوٹ ایپلیکیشن بنائیں
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # /status کمانڈ کے لیے ہینڈلر شامل کریں
    status_handler = CommandHandler('status', status_command)
    application.add_handler(status_handler)

    print("بوٹ چل رہا ہے... /status کمانڈ کے ذریعے RDP سیشن چیک کریں۔")
    # بوٹ کو مسلسل چلائیں (polling کے ذریعے)
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
