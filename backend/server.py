from flask import Flask, request, jsonify, make_response
import requests, base64
from flask_cors import CORS
import os

app = Flask(__name__)
# Permitir tu frontend y fallback a cualquier origen (útil para pruebas)
CORS(app, resources={r"/*": {"origins": ["https://nicochandia.github.io", "*"]}})

API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
API_TOKEN = os.environ.get("HF_TOKEN")

if not API_TOKEN:
    raise RuntimeError("⚠️ Falta definir la variable de entorno HF_TOKEN en Render")

headers = {"Authorization": f"Bearer {API_TOKEN}"}

@app.after_request
def aplicar_cors(response):
    """Forzar headers CORS para todos los responses"""
    response.headers["Access-Control-Allow-Origin"] = "https://nicochandia.github.io"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response

@app.route("/generar", methods=["POST", "OPTIONS"])
def generar():
    if request.method == "OPTIONS":  # preflight CORS
        return make_response("", 200)

    datos = request.get_json()
    prompt = datos.get("prompt") if datos else None
    if not prompt:
        return jsonify({"error": "Prompt vacío"}), 400

    try:
        response = requests.post(API_URL, headers=headers, json={"inputs": prompt})
        # Revisar si Hugging Face devolvió error
        if response.status_code != 200 or response.headers.get("content-type") != "image/png":
            print("Respuesta Hugging Face:", response.text)
            return jsonify({"error": "Error al generar la imagen en Hugging Face"}), 500

        image_bytes = response.content
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")
        return jsonify({"imagen": f"data:image/png;base64,{image_base64}"})
    except requests.exceptions.RequestException as e:
        print("Error Hugging Face:", str(e))
        return jsonify({"error": "No se pudo generar la imagen"}), 500


@app.route("/", methods=["GET"])
def home():
    return "✅ Backend funcionando correctamente 🚀"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
