from thesis_extractor.pdf import extract_text_from_pdf

def test_import():
    assert callable(extract_text_from_pdf)
