from telegram import Update
from telegram.ext import ContextTypes
from app.services.session import get_session, update_session

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Initialize or reset session
    update_session(user_id, status="waiting_for_jd", jd_text=None, jd_filename=None, jd_structured=None, resumes=[], reports=[])
    
    welcome_message = """🤖 *ResumeMatch AI*

I compare your resume against a Job Description.

Workflow:
1️⃣ Upload Job Description
2️⃣ Upload one or more resumes
3️⃣ Send /analyze
4️⃣ Get score + skill matching + suggestions + corrections + resources

Supported:
📄 PDF
📝 DOCX
📃 TXT

Send your Job Description to begin."""

    await update.message.reply_text(welcome_message, parse_mode='Markdown')

async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    update_session(user_id, status="waiting_for_jd", jd_text=None, jd_filename=None, jd_structured=None, resumes=[], reports=[])
    
    await update.message.reply_text("✅ Session cleared.\n\nSend a new Job Description to begin.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """*ResumeMatch AI Commands:*

/start - Start a new session
/analyze - Analyze uploaded resumes against JD
/status - Check current session status
/report 1 - Get detailed report for a specific resume
/report all - Get reports for all resumes
/reset - Clear session and start over
"""
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    session = get_session(user_id)
    
    jd_status = "✅ Uploaded" if session.get("jd_text") else "❌ Not uploaded"
    resumes_count = len(session.get("resumes", []))
    
    status_map = {
        "waiting_for_jd": "Waiting for JD",
        "waiting_for_resumes": "Waiting for resumes",
        "ready": "Ready",
        "analyzing": "Analyzing"
    }
    current_status = status_map.get(session.get("status"), "Unknown")
    
    status_text = f"""📊 *CURRENT SESSION*

JD:
{jd_status} {f'({session.get("jd_filename")})' if session.get("jd_filename") else ''}

Resumes:
{resumes_count} uploaded

Status:
{current_status}

Commands:
/analyze
/report 1
/reset
"""
    await update.message.reply_text(status_text, parse_mode='Markdown')
