from app.services.scoring import calculate_detailed_score

def get_base_llm_data():
    return {
        "skills_evaluation": [],
        "experience": {
            "match_level": "NONE",
            "jd_requirement": "2 years",
            "resume_evidence": "none",
            "priority": "CRITICAL"
        },
        "education": {
            "match_level": "NONE",
            "jd_requirement": "BSc",
            "resume_evidence": "none"
        },
        "projects": {
            "relevance_level": "NONE",
            "evidence": "none"
        }
    }

def test_calculate_score_perfect():
    data = get_base_llm_data()
    data["skills_evaluation"] = [
        {"skill": "Python", "priority": "CRITICAL", "status": "MATCHED", "evidence_type": "POSITIVE_EVIDENCE"},
        {"skill": "React", "priority": "CRITICAL", "status": "MATCHED", "evidence_type": "POSITIVE_EVIDENCE"}
    ]
    data["experience"]["match_level"] = "FULL"
    data["education"]["match_level"] = "FULL"
    data["projects"]["relevance_level"] = "HIGH"
    
    scores = calculate_detailed_score(data)
    assert scores["skills"] == 45
    assert scores["experience"] == 20
    assert scores["keywords"] == 15
    assert scores["education"] == 10
    assert scores["projects"] == 10
    assert scores["total"] == 100

def test_calculate_score_zero():
    data = get_base_llm_data()
    scores = calculate_detailed_score(data)
    assert scores["skills"] == 0
    assert scores["experience"] == 0
    assert scores["education"] == 0
    assert scores["projects"] == 0
    assert scores["total"] == 15 # Because keyword defaults to 15 if no skills exist

    data["skills_evaluation"] = [
        {"skill": "Python", "priority": "CRITICAL", "status": "MISSING", "evidence_type": "NONE"}
    ]
    scores = calculate_detailed_score(data)
    assert scores["skills"] == 0
    assert scores["keywords"] == 0
    assert scores["total"] == 0

def test_calculate_score_partial():
    data = get_base_llm_data()
    # 2 matched (Critical=4, High=3), 2 partial (Medium=2, Low=1), 1 missing (Critical=4)
    # Total weight = 4 + 3 + 2 + 1 + 4 = 14
    # Earned weight = 4 + 3 + (2*0.5) + (1*0.5) = 7 + 1 + 0.5 = 8.5
    # Skills = 8.5 / 14 * 45 = 27
    # Keywords = 8.5 / 14 * 15 = 9
    
    data["skills_evaluation"] = [
        {"skill": "A", "priority": "CRITICAL", "status": "MATCHED", "evidence_type": "POSITIVE_EVIDENCE"},
        {"skill": "B", "priority": "HIGH", "status": "MATCHED", "evidence_type": "POSITIVE_EVIDENCE"},
        {"skill": "C", "priority": "MEDIUM", "status": "PARTIAL", "evidence_type": "POSITIVE_EVIDENCE"},
        {"skill": "D", "priority": "LOW", "status": "PARTIAL", "evidence_type": "POSITIVE_EVIDENCE"},
        {"skill": "E", "priority": "CRITICAL", "status": "MISSING", "evidence_type": "NONE"}
    ]
    
    data["experience"]["match_level"] = "PARTIAL" # 10
    data["education"]["match_level"] = "FULL" # 10
    data["projects"]["relevance_level"] = "LOW" # 4
    
    scores = calculate_detailed_score(data)
    assert scores["skills"] == 27
    assert scores["experience"] == 10
    assert scores["keywords"] == 9
    assert scores["education"] == 10
    assert scores["projects"] == 4
    assert scores["total"] == 27 + 10 + 9 + 10 + 4
