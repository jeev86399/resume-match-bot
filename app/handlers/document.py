import os
import asyncio
from telegram import Update
from telegram.ext import ContextTypes
from app.services.session import get_session, update_session
from app.services.document_parser import parse_document
from app.services.llm import extract_structured_jd

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    session = get_session(user_id)
    
    document = update.message.document
    filename = document.file_name
    ext = os.path.splitext(filename)[1].lower()
    
    if ext not in ['.pdf', '.docx', '.txt']:
        await update.message.reply_text("❌ I couldn't process that file.\n\nPlease upload:\n• PDF\n• DOCX\n• TXT")
        return
        
    # Download file
    file = await context.bot.get_file(document.file_id)
    user_dir = os.path.join(UPLOAD_DIR, str(user_id))
    os.makedirs(user_dir, exist_ok=True)
    
    filepath = os.path.join(user_dir, filename)
    await file.download_to_drive(filepath)
    
    # Extract text
    text = parse_document(filepath)
    
    if not text or len(text.strip()) < 10:
        await update.message.reply_text("❌ I couldn't extract readable text from this file.\n\nPlease upload a text-based PDF, DOCX, or TXT file.")
        return
        
    status = session.get("status")
    
    if status == "waiting_for_jd":
        await process_jd(update, user_id, filename, text)
    else:
        await process_resume(update, user_id, session, filename, text)

async def process_jd(update: Update, user_id: int, filename: str, text: str):
    await update.message.reply_text(f"✅ Job Description received.\n📄 JD: {filename}\n\nAnalyzing JD structure...")
    
    try:
        jd_structured = await extract_structured_jd(text)
        update_session(
            user_id, 
            status="waiting_for_resumes", 
            jd_text=text, 
            jd_filename=filename, 
            jd_structured=jd_structured.model_dump()
        )
        
        await update.message.reply_text("Now upload one or more resumes.\n\nYou can send multiple files.\n\nWhen finished, send:\n/analyze")
    except Exception as e:
        print(f"JD Extraction Error: {e}")
        error_msg = str(e).lower()
        if "insufficient_quota" in error_msg or "429" in error_msg or "credit_balance_exhausted" in error_msg:
            await update.message.reply_text("⚠️ OpenAI API Error: Quota/Billing exhausted. Please add credits to your OpenAI account.")
        else:
            await update.message.reply_text("⚠️ Failed to analyze Job Description. Please try uploading again.")
        update_session(user_id, status="waiting_for_jd")

async def process_resume(update: Update, user_id: int, session: dict, filename: str, text: str):
    resumes = session.get("resumes", [])
    
    # Truncate if too long (simple strategy)
    if len(text) > 15000:
        text = text[:15000]
        
    resumes.append({
        "filename": filename,
        "text": text
    })
    
    update_session(user_id, resumes=resumes, status="ready")
    
    count = len(resumes)
    await update.message.reply_text(f"✅ Resume #{count} added\n📄 {filename}\n\nUpload another resume or send:\n/analyze")
