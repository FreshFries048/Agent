"""
vault_index.py
================
This module provides helper functions for storing and retrieving breach information entries
in a JSONL vault file. It is designed to be used by the MirrorSentinel daemon to persist
crawled data across runs.

Functions:
- save_entries(entries: List[dict], vault_path: str) -> None
  Appends a list of entries to a newline-delimited JSON file.

- load_entries(vault_path: str) -> List[dict]
  Loads and returns all entries from a newline-delimited JSON file.

Usage:
from vault_index import save_entries, load_entries

# save new entries
save_entries([{"company": "Acme Inc", "email": "admin@acme.com"}])

# load existing entries
existing = load_entries()
"""
import json
import os
from typing import List, Dict

DEFAULT_VAULT_PATH = "vault/mirrorsentinel_vault.jsonl"

def save_entries(entries: List[Dict], vault_path: str = DEFAULT_VAULT_PATH) -> None:
    """
    Append a list of entries to the vault file.

    Each entry should be a dictionary. The vault file will be created if it doesn't exist.
    """
    # Ensure directory exists
    os.makedirs(os.path.dirname(vault_path), exist_ok=True)
    with open(vault_path, "a", encoding="utf-8") as f:
        for entry in entries:
            try:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            except TypeError:
                # Skip entries that are not serializable
                continue

def load_entries(vault_path: str = DEFAULT_VAULT_PATH) -> List[Dict]:
    """
    Load all entries from the vault file.

    Returns an empty list if the file does not exist. Invalid lines are skipped.
    """
    entries: List[Dict] = []
    if not os.path.exists(vault_path):
        return entries

    with open(vault_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                if isinstance(data, dict):
                    entries.append(data)
            except json.JSONDecodeError:
                # Skip invalid JSON lines
                continue
    return entries
