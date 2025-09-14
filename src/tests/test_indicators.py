
from extraction.indicators import extract_indicators


def test_extract_simple():
    text = "Visit https://example.com and contact admin@example.com. UA-123456-1 t.me/somechannel"
    out = extract_indicators(text)
    assert any('https://example.com' in v for v, _ in out['url'])
    assert any('admin@example.com' in v for v, _ in out['email'])
    assert any(v.startswith('ga:') for v, _ in out['tracker'])
    assert len(out['social']) >= 1
