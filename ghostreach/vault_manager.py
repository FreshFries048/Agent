"""
GhostReach Vault Manager

A lightweight interface for storing and retrieving lead data in an SQLite database.
This module ensures deduplication of leads and provides helper methods for
fetching unprocessed or processed leads.

Usage:
  python3 vault_manager.py --init

"""

import sqlite3
import argparse
import os
from typing import List, Tuple

class VaultManager:
    def __init__(self, db_path: str = 'leads.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.ensure_schema()

    def ensure_schema(self) -> None:
        with self.conn:
            self.conn.execute('''
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE,
                name TEXT,
                role TEXT,
                company TEXT,
                status TEXT DEFAULT 'new'
            )
            ''')

    def insert_lead(self, email: str, name: str, role: str, company: str) -> None:
        try:
            with self.conn:
                self.conn.execute(
                    'INSERT INTO leads (email, name, role, company) VALUES (?, ?, ?, ?)',
                    (email, name, role, company)
                )
        except sqlite3.IntegrityError:
            # duplicate email
            pass

    def fetch_leads_by_status(self, status: str = 'new') -> List[Tuple[int, str, str, str, str]]:
        cur = self.conn.cursor()
        cur.execute('SELECT id, email, name, role, company FROM leads WHERE status=?', (status,))
        return cur.fetchall()

    def update_status(self, lead_ids: List[int], status: str) -> None:
        with self.conn:
            self.conn.executemany(
                'UPDATE leads SET status=? WHERE id=?',
                [(status, lead_id) for lead_id in lead_ids]
            )

    def close(self) -> None:
        self.conn.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='GhostReach vault manager')
    parser.add_argument('--init', action='store_true', help='Initialize the database schema')
    args = parser.parse_args()

    vm = VaultManager()
    if args.init:
        print('Database initialized.')
    vm.close()
