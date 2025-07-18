#!/usr/bin/env python3
"""
MirrorSentinel log parser module.

This module parses the raw data scraped by the crawler, extracting structured
entries such as company, domain, email, and optionally leak type or severity.
It can also compute a simple signal score for each entry based on heuristics.
"""

from typing import List, Dict


def parse(raw_entries: List[Dict[str, str]]) -> List[Dict[str, object]]:
    """Parse raw entries into structured data with a score."""
    entries: List[Dict[str, object]] = []
    for entry in raw_entries:
        entries.append({
            "company": entry.get("company"),
            "domain": entry.get("domain"),
            "email": entry.get("email"),
            "score": 1.0  # Placeholder signal score
        })
    return entries


if __name__ == "__main__":
    sample_data = [
        {"company": "ExampleCorp", "domain": "example.com", "email": "contact@example.com"},
    ]
    print(parse(sample_data))
