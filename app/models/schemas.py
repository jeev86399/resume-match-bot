from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class JobDescriptionData(BaseModel):
    job_title: str
    required_skills: List[str]
    preferred_skills: List[str]
    programming_languages: List[str]
    frameworks: List[str]
    databases: List[str]
    cloud_tools: List[str]
    soft_skills: List[str]
    experience_requirements: List[str]
    education_requirements: List[str]
    keywords: List[str]

class ResumeData(BaseModel):
    candidate_name: str
    skills: List[str]
    experience: List[str]
    education: List[str]
    projects: List[str]
    certifications: List[str]
    keywords: List[str]

class SkillEvidence(BaseModel):
    skill: str
    priority: str # "CRITICAL", "HIGH", "MEDIUM", "LOW"
    status: str # "MATCHED", "PARTIAL", "MISSING"
    evidence_type: str # "POSITIVE_EVIDENCE", "NEGATIVE_EVIDENCE", "NEUTRAL_MENTION", "NONE"

class ExperienceMatch(BaseModel):
    jd_requirement: str
    resume_evidence: str
    match_level: str  # "FULL", "PARTIAL", "NONE"
    priority: str = "CRITICAL"

class EducationMatch(BaseModel):
    jd_requirement: str
    resume_evidence: str
    match_level: str  # "FULL", "NONE"

class ProjectsMatch(BaseModel):
    evidence: str
    relevance_level: str  # "HIGH", "MEDIUM", "LOW", "NONE"

class Correction(BaseModel):
    issue: str
    why: str
    action: str
    related_requirement: str
    priority: str

class LLMAnalysisResponse(BaseModel):
    candidate: str
    skills_evaluation: List[SkillEvidence] = Field(default_factory=list)
    experience: ExperienceMatch
    education: EducationMatch
    projects: ProjectsMatch
    suggestions: List[str] = Field(default_factory=list)
    core_corrections: List[Correction] = Field(default_factory=list)
