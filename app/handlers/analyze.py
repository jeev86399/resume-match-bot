from telegram import Update
from telegram.ext import ContextTypes
from app.services.session import get_session, update_session
from app.services.llm import analyze_resume
from app.services.scoring import calculate_detailed_score, generate_score_bar
from app.services.resource_finder import find_resources
import asyncio

async def analyze_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    session = get_session(user_id)
    
    if not session.get("jd_text") or not session.get("jd_structured"):
        await update.message.reply_text("❌ Please upload a Job Description first.")
        return
        
    resumes = session.get("resumes", [])
    if not resumes:
        await update.message.reply_text("❌ Please upload at least one resume before running /analyze.")
        return
        
    progress_msg = await update.message.reply_text(f"🔍 Analyzing {len(resumes)} resumes against the JD...\n\n(This may take a minute due to AI rate limits)")
    update_session(user_id, status="analyzing")
    
    jd_structured = session["jd_structured"]
    reports = []
    
    for i, resume_data in enumerate(resumes):
        filename = resume_data["filename"]
        text = resume_data["text"]
        
        try:
            # Retry loop for rate limits
            retries = 0
            while retries < 3:
                try:
                    await context.bot.edit_message_text(
                        chat_id=update.effective_chat.id,
                        message_id=progress_msg.message_id,
                        text=f"⏳ Analyzing resume {i+1}/{len(resumes)}:\n📄 {filename}..."
                    )
                    
                    llm_result = await analyze_resume(text, jd_structured)
                    break # Success!
                    
                except Exception as e:
                    err_str = str(e).lower()
                    if "429" in err_str or "rate limit" in err_str:
                        retries += 1
                        if retries >= 3:
                            raise e
                        await context.bot.edit_message_text(
                            chat_id=update.effective_chat.id,
                            message_id=progress_msg.message_id,
                            text=f"⚠️ API Rate limit hit. Waiting 60s before continuing resume {i+1}..."
                        )
                        await asyncio.sleep(60)
                    else:
                        raise e # Re-raise if it's not a rate limit issue
            
            # Find base resources
            missing_skills = [s.skill for s in llm_result.skills_evaluation if s.status == "MISSING"]
            partial_skills = [s.skill for s in llm_result.skills_evaluation if s.status == "PARTIAL"]
            resources = find_resources(missing_skills, partial_skills)
            
            # Apply consistency rules
            llm_dump = llm_result.model_dump()
            llm_dump, resources = enforce_consistency(llm_dump, resources)
            
            # Calculate final score in python
            scores = calculate_detailed_score(llm_dump)
            final_score = scores["total"]
            
            report = {
                "id": i + 1,
                "filename": filename,
                "score_breakdown": scores,
                "llm_result": llm_dump,
                "resources": resources
            }
            reports.append(report)
            
        except Exception as e:
            print(f"Error analyzing {filename}: {e}")
            await update.message.reply_text(f"⚠️ I couldn't analyze resume #{i+1} ({filename}).\nContinuing with the remaining resumes.")
            
    update_session(user_id, reports=reports, status="ready")
    
    if not reports:
        await update.message.reply_text("❌ Analysis failed for all resumes.")
        return
        
    # Generate summary message
    summary = f"📊 ANALYSIS COMPLETE\n\nJD:\n{jd_structured.get('job_title', 'Unknown Role')}\n\nResumes analyzed: {len(reports)}\n\n"
    
    # Sort reports by score descending for summary, but keep original IDs
    sorted_reports = sorted(reports, key=lambda x: x["score_breakdown"]["total"], reverse=True)
    
    for r in sorted_reports:
        summary += f"{r['id']}️⃣ {r['filename']} — {r['score_breakdown']['total']}/100\n"
        
    summary += "\nUse:\n"
    for r in sorted_reports:
        summary += f"/report {r['id']}\n"
    summary += "\nor:\n/report all"
    
    await update.message.reply_text(summary)

async def send_long_message(update: Update, text: str):
    max_length = 4000
    if len(text) <= max_length:
        await update.message.reply_text(text, disable_web_page_preview=True)
        return
        
    parts = []
    while len(text) > 0:
        if len(text) > max_length:
            split_at = text.rfind('\n', 0, max_length)
            if split_at == -1:
                split_at = max_length
            parts.append(text[:split_at])
            text = text[split_at:]
        else:
            parts.append(text)
            break
            
    for part in parts:
        await update.message.reply_text(part, disable_web_page_preview=True)

def enforce_consistency(llm_data: dict, resources: dict) -> dict:
    # 1. Negative evidence -> MISSING
    for s in llm_data.get('skills_evaluation', []):
        if s['evidence_type'] in ['NEGATIVE_EVIDENCE', 'NEUTRAL_MENTION', 'NONE']:
            s['status'] = 'MISSING'
            
    # 2. Extract critical gaps
    critical_gaps = [
        s for s in llm_data.get('skills_evaluation', [])
        if s['priority'] in ['CRITICAL', 'HIGH'] and s['status'] in ['MISSING', 'PARTIAL']
    ]
    if llm_data.get('experience', {}).get('match_level') in ['NONE', 'PARTIAL']:
        critical_gaps.append({"skill": "Experience Requirement", "priority": "CRITICAL", "status": "MISSING"})
        
    # 3. Corrections guarantee
    corrections = llm_data.get('core_corrections', [])
    if critical_gaps and not corrections:
        corrections.append({
            "issue": f"Missing {critical_gaps[0]['skill']}",
            "why": "This is a CRITICAL/HIGH priority requirement.",
            "action": f"If you have experience with {critical_gaps[0]['skill']}, add it.",
            "related_requirement": critical_gaps[0]['skill'],
            "priority": "CRITICAL"
        })
    llm_data['core_corrections'] = corrections
    
    # 4. Filter resources strictly
    gap_skills = [s['skill'].lower() for s in llm_data.get('skills_evaluation', []) if s['status'] in ['MISSING', 'PARTIAL']]
    filtered_resources = {}
    for r_key, r_url in resources.items():
        if any(r_key.lower() in g for g in gap_skills):
            filtered_resources[r_key] = r_url
            
    return llm_data, filtered_resources

def generate_report_text(report: dict) -> str:
    filename = report["filename"]
    scores = report["score_breakdown"]
    total = scores["total"]
    llm = report["llm_result"]
    resources = report["resources"]
    
    score_bar = generate_score_bar(total)
    
    text = f"""━━━━━━━━━━━━━━━━━━━━
📊 RESUME MATCH SCORE: {total}/100
━━━━━━━━━━━━━━━━━━━━

📄 Resume: {filename}

{score_bar}

━━━━━━━━━━━━━━━━━━━━
🤔 WHY THIS SCORE?
━━━━━━━━━━━━━━━━━━━━

💻 Skills: {scores['skills']}/45
🎯 TOP MATCHING SKILLS:
"""
    matched = scores.get('matched_skills', [])
    if matched:
        for s in matched[:10]:
            text += f"- {s}\n"
    else:
        text += "- None\n"
        
    text += "\n⚠️ PARTIAL MATCHES:\n"
    partial = scores.get('partial_skills', [])
    if partial:
        for s in partial[:10]:
            text += f"- {s}\n"
    else:
        text += "- None\n"
        
    text += "\n❌ KEY MISSING SKILLS:\n"
    missing = scores.get('missing_skills', [])
    if missing:
        for s in missing[:10]:
            text += f"- {s}\n"
    else:
        text += "- None\n"
        
    text += f"""
💼 Experience: {scores['experience']}/20
JD requires: {llm["experience"]["jd_requirement"]}
Resume evidence: {llm["experience"]["resume_evidence"]}

🔑 Keywords: {scores['keywords']}/15
(Score is now tightly coupled to validated skill evidence)

🎓 Education: {scores['education']}/10
JD requires: {llm["education"]["jd_requirement"]}
Resume evidence: {llm["education"]["resume_evidence"]}

🚀 Projects/Relevance: {scores['projects']}/10
Evidence: {llm["projects"]["evidence"]}

━━━━━━━━━━━━━━━━━━━━
🧮 SCORE BREAKDOWN
━━━━━━━━━━━━━━━━━━━━
Skills:        {str(scores['skills']).rjust(2)} / 45
Experience:    {str(scores['experience']).rjust(2)} / 20
Keywords:      {str(scores['keywords']).rjust(2)} / 15
Education:     {str(scores['education']).rjust(2)} / 10
Projects:      {str(scores['projects']).rjust(2)} / 10
-------------------
TOTAL:         {str(total).rjust(2)} / 100

━━━━━━━━━━━━━━━━━━━━
💡 SUGGESTIONS
━━━━━━━━━━━━━━━━━━━━
"""
    if llm["suggestions"]:
        for s in llm["suggestions"][:3]:
            text += f"• {s}\n"
    else:
        text += "No suggestions.\n"
        
    text += """
━━━━━━━━━━━━━━━━━━━━
🔥 TOP CORRECTIONS
━━━━━━━━━━━━━━━━━━━━
"""
    if llm["core_corrections"]:
        for i, c in enumerate(llm["core_corrections"][:3]):
            text += f"⚠️ {c['issue']}\nWhy: {c['why']}\nAction: {c['action']}\n\n"
    else:
        text += "No major corrections needed.\n\n"
        
    if resources:
        text += """━━━━━━━━━━━━━━━━━━━━
🔗 RESOURCES
━━━━━━━━━━━━━━━━━━━━
"""
        for k, v in resources.items():
            text += f"{k}:\n{v}\n\n"
            
    return text

async def report_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    session = get_session(user_id)
    reports = session.get("reports", [])
    
    if not reports:
        await update.message.reply_text("❌ No reports available. Please run /analyze first.")
        return
        
    if not context.args:
        await update.message.reply_text("Please specify a report number or 'all'. Example: /report 1")
        return
        
    arg = context.args[0].lower()
    
    if arg == "all":
        for report in reports:
            text = generate_report_text(report)
            await send_long_message(update, text)
            await asyncio.sleep(0.5)
        return
        
    try:
        report_id = int(arg)
        report = next((r for r in reports if r["id"] == report_id), None)
        
        if not report:
            await update.message.reply_text(f"❌ Report #{report_id} not found.")
            return
            
        text = generate_report_text(report)
        await send_long_message(update, text)
        
    except ValueError:
        await update.message.reply_text("❌ Invalid report number.")
