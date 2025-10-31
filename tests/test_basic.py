import pytest

# Skip this test if PyPDF2 isn't installed locally
pytest.importorskip("PyPDF2")

from thesis_extractor.pdf import extract_text_from_pdf


def test_import():
    assert callable(extract_text_from_pdf)
