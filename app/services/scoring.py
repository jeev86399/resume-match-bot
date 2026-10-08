def calculate_detailed_score(llm_data: dict) -> dict:
    """
    Calculates deterministic score based on facts extracted by LLM.
    Skills = 45% (derived from priorities and status)
    Experience = 20%
    Keywords = 15%
    Education = 10%
    Project Relevance = 10%
    """
    skills_eval = llm_data.get('skills_evaluation', [])
    
    matched = [s for s in skills_eval if s['status'] == 'MATCHED']
    partial = [s for s in skills_eval if s['status'] == 'PARTIAL']
    missing = [s for s in skills_eval if s['status'] == 'MISSING']
    
    # Calculate weighted skill points
    priority_weights = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}
    total_skill_weight = 0
    earned_skill_weight = 0
    
    for s in skills_eval:
        w = priority_weights.get(s['priority'].upper(), 1)
        total_skill_weight += w
        if s['status'] == 'MATCHED':
            earned_skill_weight += w
        elif s['status'] == 'PARTIAL':
            earned_skill_weight += (w * 0.5)

    if total_skill_weight == 0:
        skills_score = 0
        kw_score = 15 # default
    else:
        skills_score = int(round((earned_skill_weight / total_skill_weight) * 45))
        kw_score = int(round((earned_skill_weight / total_skill_weight) * 15)) # keywords now tied to skill matches
        
    # Experience (20)
    exp_level = str(llm_data['experience']['match_level']).upper()
    if exp_level == "FULL":
        exp_score = 20
    elif exp_level == "PARTIAL":
        exp_score = 10
    else:
        exp_score = 0
        
    # Education (10)
    edu_level = str(llm_data['education']['match_level']).upper()
    edu_score = 10 if edu_level == "FULL" else 0
    
    # Projects (10)
    proj_level = str(llm_data['projects']['relevance_level']).upper()
    if proj_level == "HIGH":
        proj_score = 10
    elif proj_level == "MEDIUM":
        proj_score = 7
    elif proj_level == "LOW":
        proj_score = 4
    else:
        proj_score = 0
        
    total = skills_score + exp_score + kw_score + edu_score + proj_score
    
    # Expose lists for formatting
    return {
        "skills": skills_score,
        "experience": exp_score,
        "keywords": kw_score, # tied directly to skills now
        "education": edu_score,
        "projects": proj_score,
        "total": total,
        "matched_skills": [s['skill'] for s in matched],
        "partial_skills": [s['skill'] for s in partial],
        "missing_skills": [s['skill'] for s in missing]
    }

def generate_score_bar(score: int) -> str:
    filled_blocks = int(round(score / 5))
    empty_blocks = 20 - filled_blocks
    bar = "█" * filled_blocks + "░" * empty_blocks
    return bar
