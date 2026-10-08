from typing import List

RESOURCES = {
    "python": "https://docs.python.org/3/tutorial/",
    "javascript": "https://developer.mozilla.org/en-US/docs/Web/JavaScript",
    "react": "https://react.dev/learn",
    "node.js": "https://nodejs.org/en/learn",
    "docker": "https://docs.docker.com/get-started/",
    "aws": "https://aws.amazon.com/training/",
    "sql": "https://www.w3schools.com/sql/",
    "git": "https://git-scm.com/doc",
    "mongodb": "https://www.mongodb.com/docs/",
    "postgresql": "https://www.postgresql.org/docs/",
    "java": "https://dev.java/learn/",
    "spring boot": "https://spring.io/guides",
    "typescript": "https://www.typescriptlang.org/docs/",
    "kubernetes": "https://kubernetes.io/docs/tutorials/",
    "redis": "https://redis.io/docs/latest/"
}

import re

def find_resources(missing_skills: List[str], partial_skills: List[str]) -> dict:
    results = {}
    skills_to_check = [s.lower() for s in (missing_skills + partial_skills)]
    
    for skill in skills_to_check:
        if skill in RESOURCES and skill not in [k.lower() for k in results.keys()]:
            results[skill.title()] = RESOURCES[skill]
            
        else:
            for res_key, res_url in RESOURCES.items():
                if res_key not in [k.lower() for k in results.keys()]:
                    # Use word boundary regex to prevent "git" matching "digital"
                    pattern = r'\b' + re.escape(res_key) + r'\b'
                    if re.search(pattern, skill):
                        results[res_key.title()] = res_url
                        break
                
        if len(results) >= 5:
            break
            
    return results
