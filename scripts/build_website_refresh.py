#!/usr/bin/env python3
"""Archived one-shot migration builder for the September 2026 website refresh.

This script intentionally does not rebuild the current Vitalis website.

Why it is retired:
- it was authored against an immutable August 2026 baseline;
- rerunning it after later website work could overwrite current pages,
  update history, validation rules, documentation, and design guidance;
- the current committed files on main are authoritative.

Git history preserves the original migration implementation if forensic review
is ever needed. Future structural rebuild tooling must be written against the
current site model rather than reviving this migration script.
"""

raise SystemExit(
    "build_website_refresh.py is retired and must not be run. "
    "Edit the current website files on an isolated branch, run "
    "python scripts/check_site.py and git diff --check, browser-test visual "
    "changes, then merge only after review."
)
