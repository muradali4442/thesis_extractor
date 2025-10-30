# Contributing

Thanks for considering a contribution!

## Dev setup
```bash
pip install -e .
pip install -r dev-requirements.txt
pre-commit install
```

## Commit style
Use clear, present-tense messages:
- feat(pdf): add page-range support
- fix(ocr): handle missing poppler gracefully
- docs(readme): add CI badge

## Testing
Run `pytest -q` before opening a PR.

## Linting & typing
- `ruff check . --fix`
- `mypy src`

## Opening a PR
- Describe the motivation and the approach.
- Include before/after behavior if UX changes.
- Update docs and tests as needed.
