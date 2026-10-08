import os
from app.services.document_parser import parse_txt, _normalize_text

def test_parse_txt(tmp_path):
    p = tmp_path / "test.txt"
    p.write_text("Hello\n\n\nWorld   \n!")
    
    text = parse_txt(str(p))
    normalized = _normalize_text(text)
    
    assert "Hello" in normalized
    assert "World" in normalized
    assert "!" in normalized

def test_normalize_text():
    raw = "This   is \n\n a test   \n"
    normalized = _normalize_text(raw)
    assert normalized == "This   is\na test"
