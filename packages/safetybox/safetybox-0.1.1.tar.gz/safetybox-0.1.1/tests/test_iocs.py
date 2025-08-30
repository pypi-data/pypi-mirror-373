from safetybox.iocs import extract_iocs

def test_extract_ips_and_emails():
    text = 'Contact admin@example.com from 192.0.2.1 or visit https://example.com/test'
    iocs = extract_iocs(text)
    assert '192.0.2.1' in iocs['ips']
    assert 'admin@example.com' in iocs['emails']
