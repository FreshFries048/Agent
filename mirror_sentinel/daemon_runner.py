#!/usr/bin/env python3
"""
Daemon runner for MirrorSentinel.

This script imports and runs the MirrorSentinel agent driver. It should be used
as the entry point for scheduled daemon execution (e.g., via GitHub Actions).

The daemon runner does not perform any unauthorized access; it simply
orchestrates the run of the agent driver, which is responsible for browsing
public breach indexes and saving data to the breach vault.
"""

from datetime import datetime

# Import the agent driver from the same package
from agent_driver import run_agent_on_targets


def main():
    """Execute the MirrorSentinel Agent Driver."""
    start_time = datetime.utcnow().isoformat()
    print(f"[{start_time}] MirrorSentinel daemon runner started.")
    # Run the agent driver to crawl mirrors and update the vault
    run_agent_on_targets()
    end_time = datetime.utcnow().isoformat()
    print(f"[{end_time}] MirrorSentinel daemon runner completed.")


if __name__ == "__main__":
    main()
