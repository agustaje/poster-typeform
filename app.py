import os
import uuid
from flask import Flask, request, send_from_directory, jsonify
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader

app = Flask(__name__)

BASE_URL = os.getenv("BASE_URL", "https://web-production-9fe3c.up.railway.app")
GENERATED_DIR = "generated"
IMAGES_DIR = "images"
BACKGROUND_PATH = "poster_background.png"

os.makedirs(GENERATED_DIR, exist_ok=True)


@app.route("/")
def home():
    return "OK"


@app.route("/typeform-webhook", methods=["POST"])
def webhook():
    data = request.json or {}
    answers = data.get("form_response", {}).get("answers", [])

    nombre = "Sin nombre"
    imagenes = []
    incluir_nombre = True
    email = ""

    REF_IMAGENES = "64307fcd-9c8a-4d21-bf65-98bd2c375d9a"
    REF_NOMBRE = "c3bf67e80ffbb8d2"
    REF_INCLUIR_NOMBRE = "cc2e0532-21de-4f32-83c5-d42c99a9bc6d"
    REF_EMAIL = "b2e1b0d1-8bf6-4f4f-ad0b-bc8531644642"

    for a in answers:
        field_ref = a.get("field", {}).get("ref", "")

        if field_ref == REF_IMAGENES:
            labels = a.get("choices", {}).get("labels", [])
            imagenes = [f"image_{label}.png" for label in labels]

        elif field_ref == REF_NOMBRE:
            nombre = a.get("text", "Sin nombre")

        elif field_ref == REF_INCLUIR_NOMBRE:
            incluir_nombre = a.get("boolean", True)

        elif field_ref == REF_EMAIL:
            email = a.get("email", "")

    if not incluir_nombre:
        nombre = ""

    if not imagenes:
        imagenes = ["image_01.png", "image_02.png", "image_03.png", "image_04.png"]

    filename = f"poster_{uuid.uuid4().hex}.pdf"
    path = os.path.join(GENERATED_DIR, filename)

    make_poster(nombre, imagenes[:4], path)

    return jsonify({
        "status": "ok",
        "nombre": nombre,
        "email": email,
        "imagenes": imagenes[:4],
        "pdf": f"{BASE_URL}/generated/{filename}"
    })


@app.route("/generated/<filename>")
def generated(filename):
    return send_from_directory(GENERATED_DIR, filename)


@app.route("/images/<filename>")
def images(filename):
    return send_from_directory(IMAGES_DIR, filename)


@app.route("/posters")
def list_posters():
    files = [
        f for f in os.listdir(GENERATED_DIR)
        if f.lower().endswith(".pdf")
    ]
    files.sort(reverse=True)

    html = """
    <html>
    <head>
        <title>Posters generados</title>
        <style>
            body { font-family: Arial, sans-serif; padding: 30px; }
            h1 { margin-bottom: 20px; }
            li { margin: 10px 0; font-size: 18px; }
            a { color: #0057b8; text-decoration: none; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <h1>Posters generados</h1>
        <ul>
    """

    for f in files:
        html += f'<li><a href="/generated/{f}" target="_blank">{f}</a></li>'

    html += """
        </ul>
    </body>
    </html>
    """

    return html


def make_poster(nombre, imagenes, output_path):
    page_w, page_h = letter
    c = canvas.Canvas(output_path, pagesize=letter)

    if os.path.exists(BACKGROUND_PATH):
        c.drawImage(
            ImageReader(BACKGROUND_PATH),
            0,
            0,
            width=page_w,
            height=page_h
        )

    # Nombre del doctor en el pie, arriba de los logos
    if nombre:
        c.setFont("Helvetica-Bold", 13)
        c.drawCentredString(page_w / 2, 58, nombre)

    # Posiciones ajustadas al fondo
    box_w = 245
    box_h = 300

    positions = [
        (45, 430),    # arriba izquierda
        (322, 430),   # arriba derecha
        (45, 130),    # abajo izquierda
        (322, 130),   # abajo derecha
    ]

    for img_name, (x, y) in zip(imagenes, positions):
        img_path = os.path.join(IMAGES_DIR, img_name)

        if os.path.exists(img_path):
            c.drawImage(
                ImageReader(img_path),
                x,
                y,
                width=box_w,
                height=box_h,
                preserveAspectRatio=True,
                anchor="c"
            )
        else:
            c.setFont("Helvetica", 10)
            c.drawCentredString(
                x + box_w / 2,
                y + box_h / 2,
                f"No encontrada: {img_name}"
            )

    c.save()


if __name__ == "__main__":
    app.run()
