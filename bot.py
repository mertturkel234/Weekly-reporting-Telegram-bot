from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes
from dotenv import load_dotenv
import os
from gemini import generate_summary
from docx_creator import create_docx

# .env dosyasını yükle
load_dotenv(dotenv_path=".env")

# State tanımlamaları
DATE, DONE, COMPLETED, NEXT, PROBLEM = range(5)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bot başlatma komutu"""
    await update.message.reply_text("📅 Tarih Aralığını Giriniz (örn: 1-7 Ocak):")
    return DATE

async def get_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Tarih aralığını al"""
    context.user_data['date_range'] = update.message.text
    await update.message.reply_text("✅ Bu hafta neler yaptın?")
    return DONE

async def get_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Yapılan işleri al"""
    context.user_data['done'] = update.message.text
    await update.message.reply_text("🏁 Hangi işler tamamlandı?")
    return COMPLETED

async def get_completed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Tamamlanan işleri al"""
    context.user_data['completed'] = update.message.text
    await update.message.reply_text("➡️ Haftaya ne yapacaksın?")
    return NEXT

async def get_next(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gelecek hafta planlarını al"""
    context.user_data['next_week'] = update.message.text
    await update.message.reply_text("⚠️ Karşılaşılan problemler?")
    return PROBLEM

async def get_problem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Problemleri al ve rapor oluştur"""
    context.user_data['problems'] = update.message.text
    await update.message.reply_text("⏳ Rapor hazırlanıyor...")

    try:
        # Rapor özeti oluştur
        summary = generate_summary(context.user_data)

        # Word dosyası oluştur
        filename = create_docx(summary, context.user_data['date_range'])

        # Başarı mesajı
        await update.message.reply_text("✅ Rapor Hazır!")
        await update.message.reply_text(summary)

        # Word dosyasını Telegram'a gönder
        with open(filename, 'rb') as doc_file:
            await update.message.reply_document(
                document=doc_file,
                filename=f"Haftalik_Rapor_{context.user_data['date_range'].replace(' ', '_').replace('-', '_')}.docx",
                caption="📄 Haftalık Rapor Dosyanız"
            )

        await update.message.reply_text("💡 Yeni bir rapor için /start yazabilirsiniz.")

        # Dosyayı sil (temizlik)
        if os.path.exists(filename):
            os.remove(filename)

    except Exception as e:
        await update.message.reply_text(f"❌ Hata oluştu: {str(e)}")

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """İşlemi iptal et"""
    await update.message.reply_text("❌ İşlem iptal edildi.")
    return ConversationHandler.END

def main():
    """Ana fonksiyon"""
    token = os.getenv("TELEGRAM_BOT_TOKEN")

    if not token:
        print("❌ ERROR: TELEGRAM_BOT_TOKEN bulunamadı. .env dosyanı kontrol et.")
        return

    print(f"🔑 Token yüklendi: {token[:15]}...")

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