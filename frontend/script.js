// Replace with your PC IP running backend
const BACKEND_URL = "http://172.20.58.103:5000";

async function analyzeScreenshot() {
    const fileInput = document.getElementById("imageInput");
    if (!fileInput.files.length) {
        alert("Please upload an image first!");
        return;
    }
    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append("image", file);

    const res = await fetch(`${BACKEND_URL}/api/analyze-screenshot`, {
        method: "POST",
        body: formData
    });
    const data = await res.json();
    alert(`Risk: ${data.riskLevel}\nReason: ${data.reason}`);
    refreshHistory();
    refreshStats();
}

async function analyzeText() {
    const text = document.getElementById("textInput").value.trim();
    if (!text) { alert("Please enter text!"); return; }

    const res = await fetch(`${BACKEND_URL}/api/analyze-text`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text })
    });
    const data = await res.json();
    alert(`Risk: ${data.riskLevel}\nReason: ${data.reason}`);
    refreshHistory();
    refreshStats();
}

async function analyzeWebsite() {
    const url = document.getElementById("urlInput").value.trim();
    if (!url) { alert("Please enter a website URL!"); return; }

    const res = await fetch(`${BACKEND_URL}/api/analyze-website`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url })
    });
    const data = await res.json();
    alert(`Risk: ${data.riskLevel}\nReason: ${data.reason}`);
    refreshHistory();
    refreshStats();
}

async function refreshHistory() {
    const res = await fetch(`${BACKEND_URL}/api/history`);
    const data = await res.json();
    document.getElementById("history").textContent = data.length
        ? data.map(e => `[${e.timestamp}] ${e.type} - ${e.content} - Risk: ${e.riskLevel}`).join("\n")
        : "No scans yet...";
}

async function refreshStats() {
    const res = await fetch(`${BACKEND_URL}/api/stats`);
    const data = await res.json();
    document.getElementById("stats").textContent = `Low: ${data.Low} | Medium: ${data.Medium} | High: ${data.High}`;
}

// Auto-refresh history and stats every 10 seconds (optional)
setInterval(refreshHistory, 10000);
setInterval(refreshStats, 10000);