from app.services.resource_finder import find_resources

def test_find_resources():
    missing = ["Python", "UnknownSkill", "AWS", "react.js"]
    partial = ["Docker"]
    
    resources = find_resources(missing, partial)
    
    assert "Python" in resources
    assert "Aws" in resources or "AWS" in resources or "aws" in [k.lower() for k in resources.keys()]
    assert "React" in resources or "react" in [k.lower() for k in resources.keys()]
    assert "Docker" in resources or "docker" in [k.lower() for k in resources.keys()]
    assert "UnknownSkill" not in resources

def test_find_resources_max_5():
    missing = ["Python", "AWS", "React", "Docker", "Git", "SQL", "MongoDB"]
    partial = []
    
    resources = find_resources(missing, partial)
    assert len(resources) <= 5
