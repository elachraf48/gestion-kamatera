# Smart Kamatera Server Manager

A desktop GUI tool (built with PyQt5) for managing Kamatera cloud servers with:
- **Automated power management** (Power On, Power Off, Reboot)
- **Smart network switching workflows** (automatic + guided manual fallback)
- **Step-by-step instructions** for manual changes
- **Real-time workflow logging and verification**
- **Server info inspection with color-coded status**

This tool combines automation where possible with guided manual steps where needed — giving you reliability and control when switching between public and private networks.

---

## Features

- **Login with API credentials** (stored locally in `config.json`)
- **Load and display servers** in an interactive table
- **Select and control multiple servers** at once
- **Smart Network Switch**
  - Powers servers off automatically
  - Opens Kamatera console for manual steps (if required)
  - Powers servers on automatically
  - Verifies network changes
- **Color-coded statuses**
  - Running / Stopped / Pending
  - Public vs. Private network detection
- **Detailed server information viewer**

---

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/smart-kamatera-manager.git
   cd smart-kamatera-manager
2. **Install dependencies

pip install -r requirements.txt


Typical dependencies:

PyQt5
requests


3. **Run the application
