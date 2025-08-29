from flask import Flask, request, jsonify
import requests, base64
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # habilita CORS para todas las rutas

API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2"
API_TOKEN = "TU_TOKEN_DE_HUGGINGFACE"
headers = {"Authorization": f"Bearer {API_TOKEN}"}

@app.route("/generar", methods=["POST"])
def generar():
    datos = request.get_json()
    prompt = datos.get("prompt")
    response = requests.post(API_URL, headers=headers, json={"inputs": prompt})
    if response.status_code != 200:
        return jsonify({"error": "No se pudo generar la imagen"}), 500
    image_bytes = response.content
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")
    return jsonify({"imagen": f"data:image/png;base64,{image_base64}"})

@app.route("/", methods=["GET"])
def home():
    return "Backend funcionando correctamente 🚀"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
