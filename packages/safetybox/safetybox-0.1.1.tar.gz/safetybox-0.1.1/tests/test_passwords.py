from safetybox.passwords import generate_password, analyze_password

def test_generate_length():
    p = generate_password(20)
    assert len(p) == 20

def test_analyze_common():
    a = analyze_password('password')
    assert a.found_common is True
