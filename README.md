# 📋 BigQuery Release Notes Viewer

A sleek, dark-themed web application that fetches and displays Google BigQuery release notes from the official Atom feed — with one-click sharing to X (Twitter).

Built with **Python Flask** on the backend and **vanilla HTML, CSS & JavaScript** on the frontend.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔄 **Live Feed** | Fetches the latest release notes from Google's official [BigQuery Atom feed](https://docs.cloud.google.com/feeds/bigquery-release-notes.xml) |
| ⚡ **Refresh with Spinner** | One-click refresh button with an animated spinner for visual feedback |
| 🃏 **Card-based UI** | Each release note is displayed as an expandable glassmorphism card |
| 📖 **Expand / Collapse** | Cards start truncated — click "Show more" to reveal the full content |
| 🐦 **Post on X** | Each card includes a "Post" button that opens Twitter/X's compose window pre-filled with the title, link, and hashtags |
| 🔔 **Toast Notifications** | A brief slide-up toast confirms each successful refresh |
| 🛡️ **Error Handling** | Graceful error states for network failures or XML parse issues |
| 🌙 **Dark Theme** | Premium dark design with glassmorphism, gradients, and micro-animations |
| 📱 **Responsive** | Fully responsive layout that works on desktop, tablet, and mobile |

---

## 🏗️ Architecture

```
Browser (JS)  ──fetch──▶  Flask API  ──requests──▶  Google Atom Feed
                                                         │
              ◀──JSON───  Flask API  ◀──XML──────────────┘
                  │
          Renders cards in the DOM
```

The Flask server acts as a **proxy** because browsers can't directly fetch the Google XML feed due to CORS restrictions. Flask fetches it server-side, parses the XML, and returns clean JSON to the frontend.

---

## 📁 Project Structure

```
bq-release-notes/
├── app.py                  # Flask backend — 2 routes (UI + API)
├── requirements.txt        # Python dependencies (flask, requests)
├── .gitignore              # Git ignore rules
├── templates/
│   └── index.html          # Main HTML page (Jinja2 template)
└── static/
    ├── css/
    │   └── style.css       # Dark-themed design system
    └── js/
        └── app.js          # Frontend logic — fetch, render, tweet
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.9+** installed
- **pip** (comes with Python)

### Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/7Leinad/docora-17june-2026-event-talks-app.git
   cd docora-17june-2026-event-talks-app
   ```

2. **Create a virtual environment:**

   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment:**

   - **Windows (PowerShell):**
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
   - **macOS / Linux:**
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

5. **Run the app:**

   ```bash
   python app.py
   ```

6. **Open your browser** and go to **http://localhost:5000**

---

## 🔌 API Reference

### `GET /`

Serves the main HTML page.

### `GET /api/releases`

Fetches and parses the BigQuery release notes feed.

**Success Response** (`200`):

```json
{
  "status": "success",
  "entries": [
    {
      "title": "BigQuery release notes",
      "link": "https://cloud.google.com/bigquery/docs/release-notes#June_16_2026",
      "updated": "2026-06-16T18:00:00Z",
      "content": "<h2>June 16, 2026</h2><p>BigQuery now supports...</p>"
    }
  ]
}
```

**Error Response** (`502` or `500`):

```json
{
  "status": "error",
  "message": "Connection timed out"
}
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3, Flask |
| **Frontend** | Vanilla HTML5, CSS3, JavaScript (ES6+) |
| **XML Parsing** | Python `xml.etree.ElementTree` (built-in) |
| **HTTP Client** | `requests` library |
| **Fonts** | [Inter](https://fonts.google.com/specimen/Inter) via Google Fonts |
| **Social Sharing** | Twitter/X Web Intent URL (no API keys required) |

---

## 📜 License

This project is open source and available under the [MIT License](LICENSE).

---

## 🙏 Acknowledgements

- [Google Cloud BigQuery](https://cloud.google.com/bigquery) for the release notes feed
- [Flask](https://flask.palletsprojects.com/) for the lightweight web framework
- [Inter Typeface](https://rsms.me/inter/) for the beautiful typography
