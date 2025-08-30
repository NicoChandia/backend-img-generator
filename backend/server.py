from flask import Flask, request, jsonify
import requests, base64
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "https://nicochandia.github.io"}})

API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
API_TOKEN = os.environ.get("HF_TOKEN")
headers = {"Authorization": f"Bearer {API_TOKEN}"}

@app.route("/generar", methods=["POST"])
def generar():
    datos = request.get_json()
    prompt = datos.get("prompt")
    if not prompt:
        return jsonify({"error": "Prompt vacío"}), 400

    try:
        response = requests.post(API_URL, headers=headers, json={"inputs": prompt})

        # Si la API devuelve JSON (error), lo mostramos
        if response.headers.get("content-type") == "application/json":
            print("Error Hugging Face:", response.json())
            return jsonify({"error": response.json()}), 500

        # Caso exitoso: recibimos imagen en binario
        image_bytes = response.content
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")
        return jsonify({"imagen": f"data:image/png;base64,{image_base64}"})

    except requests.exceptions.RequestException as e:
        print("Error de conexión con Hugging Face:", e)
        return jsonify({"error": "No se pudo generar la imagen"}), 500


@app.route("/", methods=["GET"])
def home():
    return "Backend funcionando correctamente 🚀"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
