# GitShield for VS Code

GitShield is an AI-powered Git Guardian that prevents secret leaks, enforces best practices, and coaches developers — right inside your IDE.

## Features

- **Real-time Security Scanning**: Scans for leaked API keys, passwords, and tokens before they hit your repo.
- **Pre-commit Health Checks**: Warns you if you are missing tests, have vague commit messages, or are working directly on `main`.
- **Developer Coaching**: Analyzes your git habits and provides personalized feedback over time.
- **Recovery Wizard**: Provides a safe GUI interface to undo commits, remove files from history, or unstage files cleanly.

## Setup

The extension will automatically activate in any workspace that contains a `.git` folder.

To manually install GitShield hooks into your repository to enforce checks via the CLI, run the `GitShield: Install Hooks` command from the Command Palette.
