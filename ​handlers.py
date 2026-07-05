import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, ConversationHandler
import database
import signature_manager
import pdf_signer
import image_signer
import utils
from config import ADMIN_ID, TEMP_DIR

SIG_UPLOAD, DOC_UPLOAD = range(2)

def get_main_menu():
    keyboard = [
        [InlineKeyboardButton("✍️ Create Signature", callback_data="nav_create")],
        [InlineKeyboardButton("📄 Sign Document (PDF)", callback_data="nav_sign_pdf")],
        [InlineKeyboardButton("📂 My Signatures", callback_data="nav_view_sig")],
        [InlineKeyboardButton("❓ Help", callback_data="nav_help")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    utils.ensure_temp_directory()
    uid = update.effective_user.id
    await database.register_user(uid)
    
    welcome = (
        "👋 Welcome to *SignFlow Bot*!\n"
        "Sign documents and images securely in just a few taps.\n\n"
        "✍️ *Create and save multiple signatures*\n"
        "📄 *Sign PDF documents professionally*\n"
        "🖼 *Sign images with transparent signatures*\n"
        "🚀 *Fast, secure, and easy to use*\n\n"
        "Tap a button below or upload a document to begin."
    )
    if update.message:
        await update.message.reply_text(welcome, reply_markup=get_main_menu(), parse_mode="Markdown")
    return ConversationHandler.END

async def start_sig_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("🖋 Please upload an image of your handwritten signature on a plain background:")
    return SIG_UPLOAD

async def handle_sig_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    photo = update.message.photo[-1]
    
    tg_file = await context.bot.get_file(photo.file_id)
    raw_path = os.path.join(TEMP_DIR, f"sig_{uid}_raw.png")
    proc_path = os.path.join(TEMP_DIR, f"sig_{uid}_{photo.file_unique_id}.png")
    
    await tg_file.download_to_drive(raw_path)
    
    if signature_manager.process_transparent_signature(raw_path, proc_path):
        await database.save_sig_meta(uid, f"Signature_{photo.file_unique_id[:5]}", proc_path)
        await update.message.reply_text("✅ Signature saved with a processed transparent background!", reply_markup=get_main_menu())
    else:
        await update.message.reply_text("❌ Error processing the alpha channels transparency on your image asset.")
        
    if os.path.exists(raw_path): os.remove(raw_path)
    return ConversationHandler.END

async def start_doc_signing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid = query.from_user.id
    
    sigs = await database.get_user_sigs(uid)
    if not sigs:
        await query.message.reply_text("❌ You must create and save a signature before you can sign documents.")
        return ConversationHandler.END
        
    await query.message.reply_text("📄 Please upload the PDF document or base image asset you need signed:")
    return DOC_UPLOAD

async def handle_document_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    doc = update.message.document
    
    if not doc or not doc.file_name.lower().endswith(('.pdf', '.png', '.jpg', '.jpeg')):
        await update.message.reply_text("❌ Unsupported file format type profile mapping constraints.")
        return ConversationHandler.END
        
    tg_file = await context.bot.get_file(doc.file_id)
    doc_path = os.path.join(TEMP_DIR, f"doc_{uid}_{doc.file_name}")
    await tg_file.download_to_drive(doc_path)
    
    sigs = await database.get_user_sigs(uid)
    active_sig = sigs[0]["path"] # Pull default saved index layer signature path configuration
    out_path = os.path.join(TEMP_DIR, f"signed_{uid}_{doc.file_name}")
    
    success = False
    if doc.file_name.lower().endswith('.pdf'):
        success = pdf_signer.apply_signature_to_pdf(doc_path, active_sig, out_path, (100, 100), page_num=0)
    else:
        success = image_signer.apply_signature_to_image(doc_path, active_sig, out_path, (50, 50))
        
    if success and os.path.exists(out_path):
        with open(out_path, 'rb') as f:
            await update.message.reply_document(document=f, caption="✨ Document signed successfully via SignFlow engine layers!")
        try:
            os.remove(out_path)
        except Exception: pass
    else:
        await update.message.reply_text("❌ Verification signing layout processing bounds error.")
        
    if os.path.exists(doc_path): os.remove(doc_path)
    return ConversationHandler.END

async def menu_routing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid = query.from_user.id
    
    if query.data == "nav_view_sig":
        sigs = await database.get_user_sigs(uid)
        if not sigs:
            await query.message.reply_text("📂 You don't have any signatures saved yet.")
        else:
            msg = "📂 *Your Saved Signatures:*\n\n" + "\n".join([f"- `{s['title']}`" for s in sigs])
            await query.message.reply_text(msg, parse_mode="Markdown")
    elif query.data == "nav_help":
        await query.message.reply_text("❓ *Quick Guide:*\n1. Upload your signature image profile to extract an ink stamp mask vector.\n2. Upload a file, and SignFlow will place your transparent signature into the document layout seamlessly.")

async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    u, s = await database.get_stats_meta()
    await update.message.reply_text(f"📊 *SignFlow Ecosystem Metrics:*\n\nRegistered Accounts: `{u}`\nSaved Signature Vectors: `{s}`", parse_mode="Markdown")

