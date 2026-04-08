#!/usr/bin/env python3
"""Extract Markdown source from built MkDocs Material HTML pages.

Strategy:
1. Parse each HTML page with BeautifulSoup
2. Pre-process: convert admonitions to placeholder markers
3. Convert to markdown with markdownify
4. Post-process: restore admonition syntax, fix home page custom divs
5. Write clean .md files
"""

import os
import re
import textwrap
from bs4 import BeautifulSoup, NavigableString, Tag, Comment
import markdownify

BUILT_DIR = "/Users/dana/.openclaw/master-rulebook"
DOCS_DIR = "/Users/dana/.openclaw/master-rulebook-src/docs"

# Map of HTML path (relative dir) -> output markdown file path
PAGES = {
    ".": "index.md",
    "plans/overview": "plans/overview.md",
    "plans/plan-h": "plans/plan-h.md",
    "plans/plan-h-backtest": "plans/plan-h-backtest.md",
    "plans/plan-m": "plans/plan-m.md",
    "plans/plan-m-forward-test": "plans/plan-m-forward-test.md",
    "plans/plan-c": "plans/plan-c.md",
    "plans/plan-alpha": "plans/plan-alpha.md",
    "plans/plan-etf": "plans/plan-etf.md",
    "plans/sicadfu": "plans/sicadfu.md",
    "regime/detection": "regime/detection.md",
    "regime/transitions": "regime/transitions.md",
    "execution/options": "execution/options.md",
    "execution/sizing": "execution/sizing.md",
    "execution/exits": "execution/exits.md",
    "backtests/results": "backtests/results.md",
    "backtests/rejected": "backtests/rejected.md",
    "backtests/discoveries": "backtests/discoveries.md",
    "infrastructure/pipeline": "infrastructure/pipeline.md",
    "infrastructure/screeners": "infrastructure/screeners.md",
    "infrastructure/monitoring": "infrastructure/monitoring.md",
    "harness/index": "harness/index.md",
    "harness/architecture": "harness/architecture.md",
    "harness/dev-pipeline": "harness/dev-pipeline.md",
    "harness/how-we-got-here": "harness/how-we-got-here.md",
    "harness/lessons-and-failure-modes": "harness/lessons-and-failure-modes.md",
    "harness/memory-and-continuity": "harness/memory-and-continuity.md",
    "harness/model-coordination": "harness/model-coordination.md",
    "harness/scheduling-and-operations": "harness/scheduling-and-operations.md",
    "harness/security-and-guardrails": "harness/security-and-guardrails.md",
    "harness/tool-integrations": "harness/tool-integrations.md",
    "journal/lessons": "journal/lessons.md",
    "journal/journey": "journal/journey.md",
    "glossary": "glossary/index.md",
}

# Counter for unique admonition placeholders
_adm_counter = 0
_adm_store = {}


def get_html_path(rel_dir):
    if rel_dir == ".":
        return os.path.join(BUILT_DIR, "index.html")
    elif rel_dir == "harness/index":
        return os.path.join(BUILT_DIR, "harness", "index.html")
    else:
        return os.path.join(BUILT_DIR, rel_dir, "index.html")


def _extract_admonition_md(adm_el):
    """Convert an admonition element to MkDocs admonition markdown syntax."""
    classes = adm_el.get("class", [])
    is_details = adm_el.name == "details"

    # Determine type
    adm_type = "note"
    for cls in classes:
        if cls != "admonition":
            adm_type = cls
            break

    # Get title
    title_el = adm_el.find(["p", "summary"], class_="admonition-title")
    title_text = title_el.get_text(strip=True) if title_el else ""
    if title_el:
        title_el.decompose()

    # Remove headerlinks from remaining content
    for a in adm_el.find_all("a", class_="headerlink"):
        a.decompose()

    # Convert inner content to markdown
    # Remove the outer admonition div wrapper
    inner_html = "".join(str(c) for c in adm_el.children)
    inner_md = markdownify.markdownify(inner_html, heading_style="ATX", bullets="-")
    inner_md = inner_md.strip()

    # Indent all lines by 4 spaces
    indented = "\n".join(
        "    " + line if line.strip() else ""
        for line in inner_md.split("\n")
    )

    # Build the admonition block
    prefix = "???" if is_details else "!!!"
    if title_text and title_text.lower() != adm_type.lower():
        header = f'{prefix} {adm_type} "{title_text}"'
    else:
        header = f"{prefix} {adm_type}"

    return f"\n{header}\n{indented}\n"


def preprocess_admonitions(article):
    """Replace admonition HTML elements with placeholder text markers."""
    global _adm_counter, _adm_store

    for adm in article.find_all(["div", "details"], class_="admonition"):
        _adm_counter += 1
        key = f"ADMBLOCK{_adm_counter}ADMBLOCK"

        # Convert to mkdocs admonition syntax
        adm_md = _extract_admonition_md(adm)
        _adm_store[key] = adm_md

        # Replace the element with a text placeholder
        adm.replace_with(NavigableString(f"\n{key}\n"))


def preprocess_home_page(article):
    """Preserve custom HTML divs on the home page (hero, stat-grid, live-results)."""
    global _adm_counter, _adm_store

    # Hero section - keep as raw HTML
    hero = article.find("div", class_="hero")
    if hero:
        # Remove headerlinks
        for a in hero.find_all("a", class_="headerlink"):
            a.decompose()
        hero_html = str(hero)
        _adm_counter += 1
        key = f"ADMBLOCK{_adm_counter}ADMBLOCK"
        _adm_store[key] = f"\n{hero_html}\n"
        hero.replace_with(NavigableString(f"\n{key}\n"))

    # Stat grid - keep as raw HTML
    stat_grid = article.find("div", class_="stat-grid")
    if stat_grid:
        sg_html = str(stat_grid)
        _adm_counter += 1
        key = f"ADMBLOCK{_adm_counter}ADMBLOCK"
        _adm_store[key] = f"\n{sg_html}\n"
        stat_grid.replace_with(NavigableString(f"\n{key}\n"))

    # Live results - keep as raw HTML
    live = article.find("div", class_="live-results")
    if live:
        for a in live.find_all("a", class_="headerlink"):
            a.decompose()
        live_html = str(live)
        _adm_counter += 1
        key = f"ADMBLOCK{_adm_counter}ADMBLOCK"
        _adm_store[key] = f"\n{live_html}\n"
        live.replace_with(NavigableString(f"\n{key}\n"))


def extract_and_convert(html_path, is_home=False):
    """Extract article content and convert to Markdown."""
    with open(html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    # Find the main content area
    content_div = soup.find("div", class_="md-content")
    if not content_div:
        return ""
    article = content_div.find("article")
    if not article:
        article = content_div

    # Remove headerlink anchors
    for a in article.find_all("a", class_="headerlink"):
        a.decompose()

    # Remove edit/source links
    for a in article.find_all("a", title="Edit this page"):
        p = a.parent
        if p:
            p.decompose()

    # Remove source-date
    for div in article.find_all("div", class_="md-source-date"):
        div.decompose()

    # Remove form elements
    for tag_name in ["button", "input", "label", "form"]:
        for el in article.find_all(tag_name):
            el.decompose()

    # Pre-process home page custom divs
    if is_home:
        preprocess_home_page(article)

    # Pre-process admonitions (replace with placeholders)
    preprocess_admonitions(article)

    # Convert to markdown
    html_str = str(article)
    md = markdownify.markdownify(html_str, heading_style="ATX", bullets="-")

    # Restore admonition placeholders
    for key, value in _adm_store.items():
        md = md.replace(key, value)

    # Clean up
    md = _cleanup_markdown(md)

    return md


def _cleanup_markdown(md):
    """Final cleanup of the converted markdown."""
    # Remove HTML wrapper tags left by markdownify
    md = re.sub(r"</?article[^>]*>", "", md)
    md = re.sub(r"</?section[^>]*>", "", md)

    # Remove stray empty divs (but preserve our custom ones)
    md = re.sub(r'<div>\s*</div>', '', md)

    # Fix double-encoded entities
    md = md.replace("&amp;", "&")
    md = md.replace("&lt;", "<")
    md = md.replace("&gt;", ">")
    md = md.replace("&quot;", '"')

    # Collapse excessive blank lines (3+ -> 2)
    md = re.sub(r"\n{3,}", "\n\n", md)

    # Remove trailing whitespace on each line
    md = "\n".join(line.rstrip() for line in md.split("\n"))

    # Trim and ensure single trailing newline
    md = md.strip() + "\n"

    return md


def process_page(rel_dir, output_path):
    """Process a single HTML page."""
    global _adm_counter, _adm_store
    _adm_counter = 0
    _adm_store = {}

    html_path = get_html_path(rel_dir)
    if not os.path.exists(html_path):
        print(f"  SKIP: {html_path} not found")
        return False

    print(f"  Processing: {rel_dir} -> {output_path}")

    is_home = (rel_dir == ".")
    md = extract_and_convert(html_path, is_home=is_home)
    if not md.strip():
        print(f"  WARNING: Empty content for {rel_dir}")
        return False

    # Write output
    out_full = os.path.join(DOCS_DIR, output_path)
    os.makedirs(os.path.dirname(out_full), exist_ok=True)
    with open(out_full, "w", encoding="utf-8") as f:
        f.write(md)

    return True


def main():
    print("Extracting Markdown from built HTML pages...")
    print(f"Source: {BUILT_DIR}")
    print(f"Output: {DOCS_DIR}")
    print()

    success = 0
    failed = 0
    for rel_dir, output_path in PAGES.items():
        if process_page(rel_dir, output_path):
            success += 1
        else:
            failed += 1

    print(f"\nDone: {success} pages extracted, {failed} failed")


if __name__ == "__main__":
    main()
