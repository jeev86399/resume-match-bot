import json
from openai import AsyncOpenAI
from app.config import settings
from app.models.schemas import JobDescriptionData, LLMAnalysisResponse

client = AsyncOpenAI(
    api_key=settings.GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

async def extract_structured_jd(text: str) -> JobDescriptionData:
    prompt = """
    Analyze the following Job Description and extract structured information.
    Return ONLY valid JSON matching this structure exactly:
    {
      "job_title": "",
      "required_skills": [],
      "preferred_skills": [],
      "programming_languages": [],
      "frameworks": [],
      "databases": [],
      "cloud_tools": [],
      "soft_skills": [],
      "experience_requirements": [],
      "education_requirements": [],
      "keywords": []
    }
    """
    
    try:
        response = await client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": text}
            ],
            response_format={ "type": "json_object" },
            max_tokens=900
        )
        result = response.choices[0].message.content
        data = json.loads(result)
        return JobDescriptionData(**data)
    except Exception:
        try:
            retry_prompt = prompt + "\n\nCRITICAL: YOU MUST RETURN STRICTLY VALID JSON."
            response = await client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[
                    {"role": "system", "content": retry_prompt},
                    {"role": "user", "content": text}
                ],
                response_format={ "type": "json_object" },
                max_tokens=900
            )
            result = response.choices[0].message.content
            data = json.loads(result)
            return JobDescriptionData(**data)
        except Exception as e:
            raise ValueError(f"Failed to decode LLM response into JSON after retry: {e}")

async def analyze_resume(resume_text: str, jd_structured: dict) -> LLMAnalysisResponse:
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
    8. EXTREME BREVITY: Keep all text strings in the JSON as short as possible to save tokens!
    9. RETURN VALID JSON matching the required schema perfectly.

    JSON SCHEMA:
    {
      "candidate": "Name or Unknown",
      "skills_evaluation": [
        {
          "skill": "P&ID",
          "priority": "CRITICAL",
          "status": "MISSING", // or "MATCHED", "PARTIAL"
          "evidence_type": "NEGATIVE_EVIDENCE" // or "POSITIVE_EVIDENCE", "NEUTRAL_MENTION", "NONE"
        }
      ],
      "experience": {
        "jd_requirement": "5-15 years...",
        "resume_evidence": "2 years...",
        "match_level": "NONE", // or "FULL", "PARTIAL"
        "priority": "CRITICAL"
      },
      "education": {
        "jd_requirement": "...",
        "resume_evidence": "...",
        "match_level": "FULL"
      },
      "projects": {
        "evidence": "...",
        "relevance_level": "LOW" // or "HIGH", "MEDIUM", "NONE"
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
    
    user_content = f"JOB DESCRIPTION:\n{json.dumps(jd_structured, indent=2)}\n\nRESUME:\n{resume_text}"
    
    try:
        response = await client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_content}
            ],
            response_format={ "type": "json_object" },
            max_tokens=900
        )
        
        result = response.choices[0].message.content
        data = json.loads(result)
        return LLMAnalysisResponse(**data)
    except Exception:
        try:
            retry_prompt = prompt + "\n\nCRITICAL: YOU MUST RETURN STRICTLY VALID JSON."
            response = await client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[
                    {"role": "system", "content": retry_prompt},
                    {"role": "user", "content": user_content}
                ],
                response_format={ "type": "json_object" },
                max_tokens=900
            )
            result = response.choices[0].message.content
            data = json.loads(result)
            return LLMAnalysisResponse(**data)
        except Exception as e:
            raise ValueError(f"Failed to decode LLM response into JSON after retry: {e}")
