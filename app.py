from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import pytesseract
from PIL import Image
import requests
from datetime import datetime
import os

app = Flask(__name__, static_folder="frontend", static_url_path="")
CORS(app)

# --------------------------------
# Configure Tesseract path (SAFE)
# --------------------------------
# Local Windows example:
# C:\\Program Files\\Tesseract-OCR\\tesseract.exe
# On Render/Linux, this is usually auto-detected

TESSERACT_PATH = os.environ.get(
    "TESSERACT_CMD",
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

if os.path.exists(TESSERACT_PATH):
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

# --------------------------------
# In-memory scan history
# --------------------------------
scan_history = []

# --------------------------------
# Risk analysis logic
# --------------------------------

def analyze_text_risk(text):
    text_lower = text.lower()
    if any(word in text_lower for word in ["free", "paid", "job"]):
        return {
            "riskLevel": "Medium",
            "reason": "Possible scam or unsolicited offer"
        }
    return {
        "riskLevel": "Low",
        "reason": "No major suspicious patterns found"
    }

def analyze_website_risk(url):
    try:
        response = requests.get(url, timeout=5)
        content = response.text.lower()
        if any(word in content for word in ["login", "password", "bank", "account"]):
            return {
                "riskLevel": "High",
                "reason": "Suspicious keywords found on page"
            }
        return {
            "riskLevel": "Low",
            "reason": "No major suspicious patterns found"
        }
    except Exception as e:
        return {
            "riskLevel": "Medium",
            "reason": f"Unable to reach site: {str(e)}"
        }

# --------------------------------
# API endpoints
# --------------------------------

@app.route("/api/analyze-text", methods=["POST"])
def analyze_text():
    data = request.get_json(force=True)
    text = data.get("text", "")
    result = analyze_text_risk(text)

    scan_history.append({
        "timestamp": datetime.now().isoformat(),
        "type": "Text",
        "content": text[:50] + ("..." if len(text) > 50 else ""),
        "riskLevel": result["riskLevel"]
    })

    return jsonify(result)

@app.route("/api/analyze-screenshot", methods=["POST"])
def analyze_screenshot():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    try:
        image_file = request.files["image"]
        img = Image.open(image_file.stream)
        extracted_text = pytesseract.image_to_string(img)
    except Exception as e:
        return jsonify({
            "riskLevel": "Medium",
            "reason": "OCR failed",
            "error": str(e)
        }), 500

    result = analyze_text_risk(extracted_text)

    scan_history.append({
        "timestamp": datetime.now().isoformat(),
        "type": "Screenshot",
        "content": image_file.filename,
        "riskLevel": result["riskLevel"]
    })

    return jsonify({
        "extractedText": extracted_text,
        **result
    })

@app.route("/api/analyze-website", methods=["POST"])
def analyze_website():
    data = request.get_json(force=True)
    url = data.get("url", "")
    result = analyze_website_risk(url)

    scan_history.append({
        "timestamp": datetime.now().isoformat(),
        "type": "Website",
        "content": url,
        "riskLevel": result["riskLevel"]
    })

    return jsonify(result)

@app.route("/api/history", methods=["GET"])
def get_history():
    return jsonify(scan_history)

@app.route("/api/stats", methods=["GET"])
def get_stats():
    stats = {"Low": 0, "Medium": 0, "High": 0}
    for entry in scan_history:
        if entry["riskLevel"] in stats:
            stats[entry["riskLevel"]] += 1
    return jsonify(stats)

# --------------------------------
# Serve frontend (SAFE)
# --------------------------------

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_frontend(path):
    static_folder = app.static_folder
    file_path = os.path.join(static_folder, path)

    if path and os.path.exists(file_path):
        return send_from_directory(static_folder, path)

    return send_from_directory(static_folder, "index.html")

# --------------------------------
# Production entry point
# --------------------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)