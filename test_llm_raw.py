import asyncio
import os
import json
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv(".env")

client = AsyncOpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

from app.services.llm import extract_structured_jd
from app.services.document_parser import parse_document

async def run():
    jd_text = parse_document("data/uploads/5699770390/JD2_Core_Engineering.pdf")
    jd_struct = await extract_structured_jd(jd_text)
    
    resume_text = parse_document("data/uploads/5699770390/JD2_Resume2_M_DivyaPillai.docx")
    
    prompt = """
    You are a resume-to-job-description analysis engine.
    Compare the candidate resume against the job description strictly objectively.

    Rules:
    1. PRIORITY ASSIGNMENT: Assign every JD requirement a priority (CRITICAL, HIGH, MEDIUM, LOW).
    2. CONTEXT-AWARE MATCHING: Inspect context. "No experience with AWS" is NEGATIVE_EVIDENCE, not a match.
    3. STATUS OVERRIDE: If evidence is NEGATIVE_EVIDENCE or NEUTRAL_MENTION, the status MUST be MISSING. Do NOT give match credit.
    4. EXPERIENCE: Explicitly extract the JD requirement vs resume evidence. If missing, it's NONE. Do not assume experience.
    5. CORRECTIONS: MUST derive ONLY from gaps. If a CRITICAL or HIGH priority gap exists (MISSING or PARTIAL), you MUST generate a correction for it. Max 3 corrections.
    6. SUGGESTIONS: Max 3. One short sentence each. No explanations. E.g. "Practice PostgreSQL queries."
    7. FALSE CLAIMS: Never encourage lying or exaggerating in suggestions or corrections.
    8. RETURN VALID JSON matching the required schema perfectly.

    JSON SCHEMA:
    {
      "candidate": "Name or Unknown",
      "skills_evaluation": [
        {
          "skill": "P&ID",
          "priority": "CRITICAL",
          "status": "MISSING",
          "evidence_type": "NEGATIVE_EVIDENCE"
        }
      ],
      "experience": {
        "jd_requirement": "5-15 years...",
        "resume_evidence": "2 years...",
        "match_level": "NONE",
        "priority": "CRITICAL"
      },
      "education": {
        "jd_requirement": "...",
        "resume_evidence": "...",
        "match_level": "FULL"
      },
      "projects": {
        "evidence": "...",
        "relevance_level": "LOW"
      },
      "suggestions": ["Learn Docker basics.", "Build a React project."],
      "core_corrections": [
        {
          "issue": "P&ID validation experience is not demonstrated.",
          "why": "The JD explicitly requires hands-on P&ID validation.",
          "action": "If you have this experience, add the relevant project/work and describe the validation performed.",
          "related_requirement": "Hands-on P&ID validation",
          "priority": "CRITICAL"
        }
      ]
    }
    """
    
    user_content = f"JOB DESCRIPTION:\n{json.dumps(jd_struct.model_dump(), indent=2)}\n\nRESUME:\n{resume_text}"
    
    response = await client.chat.completions.create(
        model="qwen/qwen3.8-27b",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_content}
        ],
        response_format={ "type": "json_object" },
        max_tokens=900
    )
    
    res = response.choices[0].message.content
    print("LENGTH:", len(res))
    print(res[-200:])

asyncio.run(run())
