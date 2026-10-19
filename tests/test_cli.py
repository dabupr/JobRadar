from jobradar.cli import slug_variants


def test_slug_variants():
    assert slug_variants("Clarity AI")[:2] == ["clarityai", "clarity-ai"]
    assert slug_variants("Glovo")[0] == "glovo"
