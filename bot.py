from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes
from dotenv import load_dotenv
import os

from gemini import generate_summary
from docx_creator import create_docx
from drive_upload import upload_to_drive

load_dotenv(dotenv_path=".env")

DATE, DONE, COMPLETED, NEXT, PROBLEM = range(5)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📅 Tarih Aralığını Giriniz (örn: 1-7 Ocak):")
    return DATE

async def get_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['date_range'] = update.message.text
    await update.message.reply_text("✅ Bu hafta neler yaptın?")
    return DONE

async def get_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['done'] = update.message.text
    await update.message.reply_text("🏁 Hangi işler tamamlandı?")
    return COMPLETED

async def get_completed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['completed'] = update.message.text
    await update.message.reply_text("➡️ Haftaya ne yapacaksın?")
    return NEXT

async def get_next(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['next_week'] = update.message.text
    await update.message.reply_text("⚠️ Karşılaşılan problemler?")
    return PROBLEM

async def get_problem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['problems'] = update.message.text
    await update.message.reply_text("⏳ Rapor hazırlanıyor...")

    try:
        summary = generate_summary(context.user_data)
        filename = create_docx(summary, context.user_data['date_range'])
        link = upload_to_drive(filename)

        await update.message.reply_text("✅ Rapor Hazır!")
        await update.message.reply_text(summary)
        await update.message.reply_text(f"📄 Drive Link: {link}")
    except Exception as e:
        await update.message.reply_text(f"❌ Hata oluştu: {str(e)}")

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ İşlem iptal edildi.")
    return ConversationHandler.END

def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("ERROR: TELEGRAM_BOT_TOKEN bulunamadı. .env dosyanı kontrol et.")
        return

    app = ApplicationBuilder().token(token).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_date)],
            DONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_done)],
            COMPLETED: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_completed)],
            NEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_next)],
            PROBLEM: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_problem)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    app.add_handler(conv_handler)
    print("✅ Bot başlatıldı... /start ile Telegram'dan test et")
    app.run_polling()

if __name__ == "__main__":
    main()