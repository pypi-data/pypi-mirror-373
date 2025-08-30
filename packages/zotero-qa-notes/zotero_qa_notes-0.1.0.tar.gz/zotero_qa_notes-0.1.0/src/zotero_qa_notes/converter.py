from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, List, Any, Iterable
from slugify import slugify

def load_zotero_json(path: Path | str) -> List[Dict[str, Any]]:
    p = Path(path)
    data = json.loads(p.read_text(encoding="utf-8"))
    if isinstance(data, dict) and "items" in data:
        return data.get("items", [])
    if isinstance(data, list):
        return data
    raise ValueError("Unsupported Zotero export format")

def _authors(item: Dict[str, Any]) -> str:
    creators = item.get("creators", [])
    names = []
    for c in creators:
        first = c.get("firstName") or ""
        last = c.get("lastName") or ""
        full = (first + " " + last).strip()
        if full:
            names.append(full)
    return ", ".join(names) if names else "Unknown"

def _tags(item: Dict[str, Any]) -> str:
    tags = item.get("tags", [])
    vals = []
    for t in tags:
        if isinstance(t, dict):
            tag = t.get("tag")
            if tag: vals.append(tag)
        elif isinstance(t, str):
            vals.append(t)
    return ", ".join(vals)

def _kv_lines(extra: str | None) -> Iterable[str]:
    if not extra:
        return []
    lines = []
    for piece in extra.split(";"):
        if ":" in piece:
            k, v = piece.split(":", 1)
            lines.append(f"- {k.strip()}: {v.strip()}")
    return lines

def item_to_markdown(item: Dict[str, Any], qa_hints: List[str] | None = None) -> str:
    title = item.get("title") or "Untitled"
    year = (item.get("date") or "").split("-")[0]
    authors = _authors(item)
    tags = _tags(item)
    url = item.get("url") or item.get("DOI") or ""
    abstract = (item.get("abstractNote") or "").strip()

    md = [f"# {title} ({year})\n"]
    md.append(f"**Authors:** {authors}  \n")
    if tags:
        md.append(f"**Tags:** {tags}  \n")
    if url:
        md.append(f"**Link:** {url}\n")
    md.append("\n## Abstract\n")
    md.append(abstract + "\n" if abstract else "(No abstract provided)\n")

    extra = item.get("extra")
    kv = list(_kv_lines(extra))
    if kv:
        md.append("\n## Key Facts\n")
        md.extend(line + "\n" for line in kv)

    if qa_hints:
        md.append("\n## Q&A Prompts\n")
        for hint in qa_hints:
            md.append(f"- What about **{hint.strip()}**?\n")
    return "".join(md)

def convert_items_to_markdown(items: List[Dict[str, Any]], *, qa_hints: List[str] | None = None,
                              merge: bool = False, out_dir: Path | None = None,
                              output_file: Path | None = None, slug: bool = False) -> None:
    if merge:
        docs = [item_to_markdown(it, qa_hints) for it in items]
        text = "\n\n---\n\n".join(docs)
        if not output_file:
            output_file = Path("notes.md")
        Path(output_file).write_text(text, encoding="utf-8")
        return

    out = Path(out_dir or "out")
    out.mkdir(parents=True, exist_ok=True)
    for it in items:
        title = it.get("title") or "untitled"
        fname = slugify(title) if slug else title.replace("/", "-")
        path = out / f"{fname}.md"
        path.write_text(item_to_markdown(it, qa_hints), encoding="utf-8")
