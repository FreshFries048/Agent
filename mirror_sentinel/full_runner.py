"""
MirrorSentinel full runner script.

This script harvests email leads from publicly accessible breach mirror targets defined in mirror_targets.json,
saves them to the MirrorSentinel JSONL vault, inserts them into the GhostReach SQLite vault via VaultManager,
and triggers GhostReach to send outreach emails.

NOTE: This script uses simple HTTP GET to fetch pages and regular expressions to parse email addresses.
"""

import os
import re
import json
import datetime
import requests

# Import save_entries from vault_index
from mirror_sentinel.vault_index import save_entries
# Import VaultManager and GhostOutreach from GhostReach
from ghostreach.vault_manager import VaultManager
from ghostreach.ghost_outreach import GhostOutreach

MIRROR_TARGETS_PATH = os.path.join(os.path.dirname(__file__), 'mirror_targets.json')
# Path to MirrorSentinel vault file
MIRROR_VAULT_PATH = os.path.join(os.path.dirname(__file__), 'vault', 'mirrorsentinel_vault.jsonl')
# Path to GhostReach leads database
GHOSTREACH_DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'ghostreach', 'leads.db')
# GhostReach market configuration path
GHOSTREACH_CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'ghostreach', 'market_targets.json')

def load_targets():
    with open(MIRROR_TARGETS_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def extract_emails(html):
    pattern = r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}'
    return re.findall(pattern, html)

def harvest_entries():
    targets = load_targets()
    entries = []
    for target in targets:
        url = target.get('url')
        label = target.get('label', '')
        try:
            resp = requests.get(url, timeout=15)
            resp.raise_for_status()
            emails = extract_emails(resp.text)
            for email in set(emails):
                domain = email.split('@')[-1] if '@' in email else ''
                entry = {
                    "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
                    "source": label,
                    "email": email,
                    "domain": domain,
                    "company": None,
                    "role": None,
                    "leak_type": None,
                    "price": None
                }
                entries.append(entry)
        except Exception:
            # Skip unreachable targets
            continue
    return entries

def insert_into_ghostreach(entries):
    vm = VaultManager(GHOSTREACH_DB_PATH)
    for entry in entries:
        email = entry.get('email')
        company = entry.get('company') or ''
        role = entry.get('role') or ''
        name = email.split('@')[0] if email else ''
        vm.insert_lead(email, name, role, company)

def send_outreach():
    ghost = GhostOutreach(config_path=GHOSTREACH_CONFIG_PATH)
    ghost.run()

def main():
    entries = harvest_entries()
    if entries:
        save_entries(entries, vault_path=MIRROR_VAULT_PATH)
        insert_into_ghostreach(entries)
        send_outreach()

if __name__ == '__main__':
    main()
