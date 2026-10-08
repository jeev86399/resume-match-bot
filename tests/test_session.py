from app.services.session import get_session, update_session, clear_session

def test_session_lifecycle():
    user_id = 999999
    
    # 1. New session
    session = get_session(user_id)
    assert session["user_id"] == user_id
    assert session["status"] == "waiting_for_jd"
    
    # 2. Update session
    update_session(user_id, status="ready", jd_filename="test.pdf")
    session = get_session(user_id)
    assert session["status"] == "ready"
    assert session["jd_filename"] == "test.pdf"
    
    # 3. Clear session
    clear_session(user_id)
    session = get_session(user_id)
    assert session["status"] == "waiting_for_jd"
    assert session["jd_filename"] is None
