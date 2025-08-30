from pathlib import Path
from zotero_qa_notes.converter import item_to_markdown, load_zotero_json

def test_item_to_markdown_basic(tmp_path: Path):
    item = {
        "title": "Test Paper",
        "creators": [{"firstName": "A.", "lastName": "Author"}],
        "date": "2024",
        "abstractNote": "A short abstract.",
        "tags": [{"tag": "Raman"}],
        "url": "https://example.com"
    }
    md = item_to_markdown(item, qa_hints=["methods", "results"]) 
    assert "Test Paper (2024)" in md
    assert "Authors:" in md
    assert "Raman" in md
    assert "Q&A Prompts" in md

def test_load_zotero_json_examples(tmp_path: Path):
    import json
    data = {
        "items": [{
            "title": "Sample",
            "creators": [{"firstName": "Z", "lastName": "Tester"}]
        }]
    }
    p = tmp_path / "sample.json"
    p.write_text(json.dumps(data))
    items = load_zotero_json(p)
    assert isinstance(items, list)
    assert items
