from __future__ import annotations
import argparse
from pathlib import Path
from .converter import load_zotero_json, convert_items_to_markdown
from . import __version__

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="zotero-qa-notes",
        description="Convert Zotero JSON export to Markdown with optional Q&A prompts",
    )
    p.add_argument("input", type=Path, help="Path to Zotero JSON export")
    p.add_argument("--out", type=Path, default=Path("out"), help="Output directory")
    p.add_argument("-o", "--output", type=Path, help="Single merged Markdown file path")
    p.add_argument("--merge", action="store_true", help="Merge all items")
    p.add_argument("--qa-hints", type=str, help="Comma-separated list of Q&A topics")
    p.add_argument("--slug", action="store_true", help="Slugify filenames from titles")
    p.add_argument("-q", "--quiet", action="store_true", help="Reduce console output")
    p.add_argument("-V", "--version", action="version", version=f"%(prog)s {__version__}")
    return p

def main() -> None:
    p = build_parser()
    args = p.parse_args()

    items = load_zotero_json(args.input)
    qa = [s.strip() for s in args.qa_hints.split(",")] if args.qa_hints else None

    convert_items_to_markdown(
        items,
        qa_hints=qa,
        merge=bool(args.merge or args.output),
        out_dir=args.out,
        output_file=args.output,
        slug=args.slug,
    )

    if not args.quiet:
        if args.merge or args.output:
            print(f"Wrote merged Markdown to {args.output or 'notes.md'}")
        else:
            print(f"Wrote {len(items)} files to {args.out}")
if __name__ == "__main__":
    main()
