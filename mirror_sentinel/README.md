# MirrorSentinel

MirrorSentinel is an autonomous breach-visibility daemon that monitors publicly leaked credentials and data exposures, enriches them with GhostReach, and performs legally compliant outreach to affected organizations.

## Purpose

This module scans public mirrors of infostealer and breach marketplaces to identify companies or domains whose credentials have been exposed. It does **not** replay stolen logins or perform unauthorized access. Instead, it uses the leak signal to:

- Generate targeted outreach offering security services or breach alerts.
- Trigger follow-on actions in GhostReach (lead harvesting & messaging).
- Feed signal data into the vault for future actions.

## Components

- **crawler.py**: Uses Agent Mode to browse public breach listings, extracting company names, domains, and leaked email addresses without logging in or attempting unauthorized access.
- **log_parser.py**: Parses and classifies scraped data, filtering relevant entries and computing a signal score.
- **vault_index.py**: Stores breach entries for later analysis and outreach.
- **sentinel_runner.py**: Orchestrates crawling, parsing, and data storage; can be run on a schedule via GitHub Actions.

## Usage

After placing this folder in your repository, run `python3 mirror_sentinel/sentinel_runner.py` to collect signals. Then connect the output to GhostReach's email engine for breach-related outreach.

## Note

MirrorSentinel is designed to operate within legal boundaries. It does not break into systems or use stolen credentials; it merely uses publicly available breach data to provide value-added security services.
