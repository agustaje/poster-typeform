# (te lo dejo resumido para que funcione ya)
import os, uuid
from flask import Flask, request, send_from_directory, jsonify
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

app = Flask(__name__)
BASE_URL = os.getenv("BASE_URL", "")
os.makedirs("generated", exist_ok=True)
os.makedirs("images", exist_ok=True)

@app.route("/")
def home():
    return "OK"

@app.route("/typeform-webhook", methods=["POST"])
def webhook():
    filename = f"{uuid.uuid4().hex}.pdf"
    path = f"generated/{filename}"

    c = canvas.Canvas(path, pagesize=letter)
    c.drawString(100, 700, "POSTER GENERADO")
    c.save()

    return jsonify({
        "pdf": f"{BASE_URL}/generated/{filename}"
    })

@app.route("/generated/<f>")
def gen(f):
    return send_from_directory("generated", f)

if __name__ == "__main__":
    app.run()