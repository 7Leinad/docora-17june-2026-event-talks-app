"""BigQuery Release Notes Viewer — Flask Backend."""

from flask import Flask, render_template, jsonify
import requests
import xml.etree.ElementTree as ET

app = Flask(__name__)

FEED_URL = "https://docs.cloud.google.com/feeds/bigquery-release-notes.xml"
ATOM_NS = {"atom": "http://www.w3.org/2005/Atom"}


@app.route("/")
def index():
    """Serve the main page."""
    return render_template("index.html")


@app.route("/api/releases")
def get_releases():
    """Fetch the Atom feed, parse it, and return JSON."""
    try:
        resp = requests.get(FEED_URL, timeout=20)
        resp.raise_for_status()

        root = ET.fromstring(resp.content)
        entries = []

        for entry in root.findall("atom:entry", ATOM_NS):
            title_el = entry.find("atom:title", ATOM_NS)
            link_el = entry.find("atom:link", ATOM_NS)
            updated_el = entry.find("atom:updated", ATOM_NS)
            content_el = entry.find("atom:content", ATOM_NS)

            entries.append(
                {
                    "title": title_el.text if title_el is not None else "",
                    "link": link_el.get("href", "") if link_el is not None else "",
                    "updated": updated_el.text if updated_el is not None else "",
                    "content": content_el.text if content_el is not None else "",
                }
            )

        return jsonify({"status": "success", "entries": entries})

    except requests.RequestException as exc:
        return jsonify({"status": "error", "message": str(exc)}), 502
    except ET.ParseError as exc:
        return jsonify({"status": "error", "message": f"XML parse error: {exc}"}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
