#!/usr/bin/env python3

"""
MirrorSentinel Enhanced Runner

This script harvests breach data from mirror targets, applies email extraction
with regex and BeautifulSoup fallback, scores each lead, rotates personas for
outreach, saves entries to the JSONL vault, inserts leads into the GhostReach
SQLite database, updates the market_targets.json configuration, and runs the
GhostReach outreach engine.

It is designed to be run autonomously (e.g., via GitHub Actions).
"""

import os
import re
import json
import random
import requests
from datetime import datetime
from typing import List, Dict
from bs4 import BeautifulSoup

from mirror_sentinel.vault_index import save_entries
from ghostreach.vault_manager import VaultManager
from ghostreach.ghost_outreach import GhostOutreach

TARGETS_FILE = os.path.join(os.path.dirname(__file__), "mirror_targets.json")
MIRROR_VAULT_PATH = os.path.join(os.path.dirname(__file__), "vault", "mirrorsentinel_vault.jsonl")

def load_targets() -> List[Dict]:
    with open(TARGETS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def extract_emails(html: str) -> List[str]:
    # Basic regex extraction
    emails = set(re.findall(r"[\w\.\-]+@[\w\.\-]+", html))
    # Fallback using BeautifulSoup for mailto links and text
    if not emails:
        soup = BeautifulSoup(html, "html.parser")
        for link in soup.find_all("a", href=True):
            href = link["href"]
            if href.startswith("mailto:"):
                emails.add(href.split("mailto:")[1])
        # Additional fallback: scan text with '@'
        for word in soup.get_text(" ").split():
            if "@" in word and "." in word:
                cleaned = word.strip(" ,;()[]{}<>\"'")
                if "@" in cleaned:
                    emails.add(cleaned)
    return list(emails)

def harvest_entries(targets: List[Dict]) -> List[Dict]:
    harvested: List[Dict] = []
    for target in targets:
        url = target.get("url")
        label = target.get("label", url)
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            html = response.text
            emails = extract_emails(html)
            for email in emails:
                domain = email.split("@")[ - 1]
                company = domain.split(".")[0] if domain else ""
                generic_domains = {"gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "icloud.com", "protonmail.com"}
                score = 1.0 if domain not in generic_domains else 0.5
                entry = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "source": label,
                    "company": company,
                    "email": email,
                    "leak_type": target.get("extract", {}).get("category", "unknown"),
                    "price": target.get("price"),
                    "score": score
                }
                harvested.append(entry)
        except Exception as e:
            print(f"Error fetching {url}: {e}")
    return harvested

def insert_into_ghostreach(entries: List[Dict], db_path: str = "ghostreach/leads.db") -> None:
    vm = VaultManager(db_path)
    for entry in entries:
        email = entry.get("email")
        name = email.split("@")[0] if email else ""
        role = "Founder"
        company = entry.get("company", "")
        vm.insert_lead(email, name, role, company)
    vm.close()

def rotate_persona(config_path: str = "ghostreach/market_targets.json") -> None:
    personas = [
        {
            "industry": "Cybersecurity",
            "buyer_personas": [
                {"role": "Founder", "pain_points": ["data breaches", "compliance", "customer trust"]},
                {"role": "CTO", "pain_points": ["vulnerability management", "incident response", "security budgets"]}
            ],
            "template": "Hello {name},\n\nOur automated scans detected potential exposure of {company}'s data. As a {role}, addressing breaches and {pain_points} is critical. We offer a free audit and recommendations.\n\nBest regards,\nGhostReach Security Team"
        },
        {
            "industry": "SaaS",
            "buyer_personas": [
                {"role": "CEO", "pain_points": ["user data leaks", "platform security", "brand reputation"]},
                {"role": "Head of Engineering", "pain_points": ["security monitoring", "incident response", "compliance"]}
            ],
            "template": "Hi {name},\n\nWe see that {company} may be affected by a recent exposure. As {role}, ensuring platform integrity and solving {pain_points} is important. Here's how we can help.\n\nCheers,\nGhostReach Team"
        },
        {
            "industry": "E-commerce",
            "buyer_personas": [
                {"role": "Owner", "pain_points": ["customer data protection", "payment security", "trust signals"]},
                {"role": "Security Lead", "pain_points": ["PCI compliance", "fraud detection", "breach prevention"]}
            ],
            "template": "Dear {name},\n\nWe identified that {company}'s online store might have compromised data. As {role}, tackling {pain_points} is top priority. We can provide an immediate security assessment.\n\nRegards,\nGhostReach"
        }
    ]
    persona = random.choice(personas)
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(persona, f, ensure_ascii=False, indent=2)

def main() -> None:
    # Load targets
    targets = load_targets()
    # Harvest entries
    entries = harvest_entries(targets)
    if entries:
        # Save to JSONL vault
        save_entries(entries, MIRROR_VAULT_PATH)
        # Insert into GhostReach database
        insert_into_ghostreach(entries, db_path="ghostreach/leads.db")
        # Rotate persona and update market targets
        rotate_persona()
        # Run GhostReach outreach
        outreach = GhostOutreach("ghostreach/market_targets.json", "ghostreach/leads.db")
        outreach.run()
    else:
        print("No emails harvested from targets.")

if __name__ == "__main__":
    main()
