import os
import asyncio
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ConversationHandler
import database
import handlers
from config import BOT_TOKEN

def main():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(database.init_db())

    if not BOT_TOKEN:
        print("Fatal error: Missing BOT_TOKEN")
        return

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    sig_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(handlers.start_sig_upload, pattern="^nav_create$")],
        states={handlers.SIG_UPLOAD: [MessageHandler(filters.PHOTO, handlers.handle_sig_image)]},
        fallbacks=[CommandHandler("start", handlers.start)]
    )

    doc_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(handlers.start_doc_signing, pattern="^nav_sign_pdf$")],
        states={handlers.DOC_UPLOAD: [MessageHandler(filters.Document.ALL | filters.PHOTO, handlers.handle_document_file)]},
        fallbacks=[CommandHandler("start", handlers.start)]
    )

    app.add_handler(CommandHandler("start", handlers.start))
    app.add_handler(CommandHandler("stats", handlers.admin_stats))
    app.add_handler(CallbackQueryHandler(handlers.menu_routing, pattern="^nav_"))
    app.add_handler(sig_conv)
    app.add_handler(doc_conv)

    print("SignFlow Engine Workers Active & Polling...")
    app.run_polling()

if __name__ == '__main__':
    main()

