#!/usr/bin/env python3
"""Validate the static Vitalis Interactive website with the standard library."""

from __future__ import annotations

import re
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_CONTACTS = (
    "hello@vitalisinteractive.com",
    "support@vitalisinteractive.com",
)
EXPECTED_NAV = (
    ("Family Office Simulator", "family-office-simulator.html"),
    ("Games", "games.html"),
    ("Studio", "studio.html"),
    ("Updates", "latest.html"),
    ("Support", "support.html"),
    (
        "Play on Steam",
        "https://store.steampowered.com/app/4820790/Family_Office_Simulator/",
    ),
)
CURRENT_PAGE = {
    "family-office-simulator.html": "family-office-simulator.html",
    "games.html": "games.html",
    "studio.html": "studio.html",
    "latest.html": "latest.html",
    "support.html": "support.html",
}
REQUIRED_STYLES = {"styles.css", "foundation.css"}
NEWSLETTER_PAGES = {"index.html", "privacy.html"}
LEGACY_FILES = {
    "script.js",
    "site-v2.css",
    "site-v3.css",
    "site-v4.css",
    "hero-v5.css",
}
ACTIVE_DOCUMENTS = ("README.md", "DESIGN.md", "AGENTS.md")
OLD_PUBLIC_EMAIL = "vitalisinteractive@gmail.com"
TRACKER_URL = "https://tracker.metricool.com/resources/be.js"
TRACKER_HASH = "f0e9f7ba2d868aa7d04d28c28366f0ec"


def _decode(values: tuple[int, ...]) -> str:
    return "".join(chr(value) for value in values)


def _protected_public_phrases() -> tuple[str, ...]:
    """Return restricted phrases without spelling private/reveal terms in source."""
    encoded = (
        (80, 111, 114, 116, 102, 111, 108, 105, 111, 32, 80, 108, 97, 121, 116, 104, 114, 111, 117, 103, 104),
        (84, 72, 69, 80, 79, 82, 84, 70, 79, 76, 73, 79, 80, 76, 65, 89, 84, 72, 82, 79, 85, 71, 72),
        (77, 97, 105, 110, 32, 83, 116, 114, 101, 101, 116, 32, 79, 112, 101, 114, 97, 116, 111, 114),
        (68, 101, 97, 108, 101, 114, 32, 80, 114, 105, 110, 99, 105, 112, 97, 108),
        (82, 97, 110, 99, 104, 32, 66, 111, 115, 115),
        (84, 114, 97, 105, 108, 98, 108, 97, 122, 101, 114),
    )
    return tuple(_decode(value).casefold() for value in encoded)


def _protected_identity_terms() -> set[str]:
    encoded = (
        (82, 121, 97, 110),
        (114, 121, 97, 110, 64),
    )
    terms = {_decode(value).casefold() for value in encoded}

    # The surname is intentionally not stored in this public repository. When
    # Git history is available, protect non-organizational author-name parts too.
    try:
        result = subprocess.run(
            ["git", "log", "--format=%aN"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return terms

    protected_first_name = _decode(encoded[0]).casefold()
    exclusions = {"vitalis", "interactive", "github", "actions", "noreply"}
    for name in result.stdout.splitlines():
        parts = re.findall(r"[A-Za-z][A-Za-z'-]{2,}", name)
        if protected_first_name not in {part.casefold() for part in parts}:
            continue
        for part in parts:
            folded = part.casefold()
            if folded not in exclusions:
                terms.add(folded)
    return terms


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.paths: list[tuple[str, str]] = []
        self.images: list[dict[str, str]] = []
        self.stylesheets: list[str] = []
        self.scripts: list[str] = []
        self.nav_links: list[dict[str, str]] = []
        self.footer_links: list[str] = []
        self._in_primary_nav = False
        self._in_footer = False
        self._current_nav_link: dict[str, str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key: value or "" for key, value in attrs}
        if tag == "nav" and values.get("aria-label") == "Primary navigation":
            self._in_primary_nav = True
        elif tag == "footer":
            self._in_footer = True

        for attr in ("href", "src"):
            if values.get(attr):
                self.paths.append((attr, values[attr]))

        if tag == "img":
            self.images.append(values)
        elif tag == "link" and "stylesheet" in values.get("rel", "").split():
            self.stylesheets.append(values.get("href", ""))
        elif tag == "script" and values.get("src"):
            self.scripts.append(values["src"])
        elif tag == "a" and self._in_primary_nav:
            self._current_nav_link = {
                "href": values.get("href", ""),
                "current": values.get("aria-current", ""),
                "text": "",
            }
        elif tag == "a" and self._in_footer:
            self.footer_links.append(values.get("href", ""))

    def handle_data(self, data: str) -> None:
        if self._current_nav_link is not None:
            self._current_nav_link["text"] += data

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self._current_nav_link is not None:
            self._current_nav_link["text"] = " ".join(
                self._current_nav_link["text"].split()
            )
            self.nav_links.append(self._current_nav_link)
            self._current_nav_link = None
        elif tag == "nav" and self._in_primary_nav:
            self._in_primary_nav = False
        elif tag == "footer" and self._in_footer:
            self._in_footer = False


def _internal_target(page: Path, raw_url: str) -> Path | None:
    if raw_url.startswith("//"):
        return None
    parsed = urlsplit(raw_url)
    if parsed.scheme or not parsed.path:
        return None
    path_text = unquote(parsed.path)
    if path_text == "/":
        return ROOT / "index.html"
    if path_text.startswith("/"):
        target = ROOT / path_text.lstrip("/")
    else:
        target = page.parent / path_text
    if path_text.endswith("/"):
        target /= "index.html"
    return target.resolve()


def _page_errors(page: Path, text: str, parser: PageParser) -> list[str]:
    errors: list[str] = []
    lowered = text.casefold()

    for attr, raw_url in parser.paths:
        target = _internal_target(page, raw_url)
        if target is not None and (ROOT not in target.parents and target != ROOT):
            errors.append(f"{page.name}: {attr} escapes the repository root")
        elif target is not None and not target.exists():
            errors.append(f"{page.name}: broken internal {attr} path: {raw_url}")

    for image in parser.images:
        if "alt" not in image or len(image["alt"].strip()) < 3:
            errors.append(f"{page.name}: image is missing useful alt text")

    for phrase in _protected_public_phrases():
        if phrase in lowered:
            errors.append(f"{page.name}: contains a paused or unrevealed project reference")
            break

    for term in _protected_identity_terms():
        found = term in lowered if term.endswith("@") else re.search(
            rf"(?<![A-Za-z]){re.escape(term)}(?![A-Za-z])", lowered
        )
        if found:
            errors.append(f"{page.name}: contains a protected personal identifier")
            break

    if OLD_PUBLIC_EMAIL in lowered:
        errors.append(f"{page.name}: contains the retired public email address")

    for contact in REQUIRED_CONTACTS:
        if contact not in lowered:
            errors.append(f"{page.name}: missing required public contact address")

    actual_nav = tuple((link["text"], link["href"]) for link in parser.nav_links)
    if actual_nav != EXPECTED_NAV:
        errors.append(f"{page.name}: primary navigation labels or order are inconsistent")

    expected_current = CURRENT_PAGE.get(page.name)
    current_links = [link for link in parser.nav_links if link["current"] == "page"]
    if expected_current:
        if len(current_links) != 1 or current_links[0]["href"] != expected_current:
            errors.append(f"{page.name}: aria-current does not identify the current page")
    elif current_links:
        errors.append(f"{page.name}: unexpected aria-current in primary navigation")

    if "contact.html" not in parser.footer_links:
        errors.append(f"{page.name}: footer is missing the Contact link")
    if "privacy.html" not in parser.footer_links:
        errors.append(f"{page.name}: footer is missing the Privacy link")

    styles = set(parser.stylesheets)
    if not REQUIRED_STYLES.issubset(styles):
        errors.append(f"{page.name}: missing required active styles")
    if page.name in NEWSLETTER_PAGES and "newsletter.css" not in styles:
        errors.append(f"{page.name}: missing newsletter.css")
    if parser.scripts.count("site.js") != 1:
        errors.append(f"{page.name}: must load site.js exactly once")

    for legacy in LEGACY_FILES:
        if legacy.casefold() in lowered:
            errors.append(f"{page.name}: references deleted legacy file {legacy}")

    return errors


def main() -> int:
    errors: list[str] = []
    public_pages = sorted(ROOT.glob("*.html"))
    if not public_pages:
        errors.append("No public HTML pages were found.")

    for page in public_pages:
        text = page.read_text(encoding="utf-8")
        parser = PageParser()
        parser.feed(text)
        errors.extend(_page_errors(page, text, parser))

    active_text = "\n".join(
        (ROOT / name).read_text(encoding="utf-8")
        for name in ACTIVE_DOCUMENTS
        if (ROOT / name).exists()
    ).casefold()
    if OLD_PUBLIC_EMAIL in active_text:
        errors.append("Active documentation contains the retired public email address.")
    for legacy in LEGACY_FILES:
        if legacy.casefold() in active_text:
            errors.append(f"Active documentation references deleted legacy file {legacy}.")

    javascript = "\n".join(
        path.read_text(encoding="utf-8") for path in sorted(ROOT.glob("*.js"))
    )
    if len(re.findall(r"\bbeTracker\s*\.\s*t\s*\(", javascript)) != 1:
        errors.append("Metricool must initialize exactly once across active JavaScript.")
    if javascript.count(TRACKER_URL) != 1 or javascript.count(TRACKER_HASH) != 1:
        errors.append("Metricool loader URL or approved hash is missing or duplicated.")

    if errors:
        print("Site validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Site validation passed for {len(public_pages)} public HTML pages.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
