from telegram.ext import Application, CommandHandler, MessageHandler, filters
from app.config import settings
from app.handlers.start import start_command, reset_command, help_command, status_command
from app.handlers.document import handle_document
from app.handlers.analyze import analyze_command, report_command

def setup_bot() -> Application:
    application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("reset", reset_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("analyze", analyze_command))
    application.add_handler(CommandHandler("report", report_command))
    
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))

    return application
