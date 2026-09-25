from flask import Flask, request, jsonify
from flask_cors import CORS
from huggingface_hub import InferenceClient
import base64
import io
import os

app = Flask(__name__)

# Configuración de CORS: Permite que tu página en GitHub Pages haga peticiones a este servidor
CORS(app, resources={r"/*": {"origins": "https://nicochandia.github.io"}})

# Configuración de Hugging Face
# Antes se llamaba directo a "hf-inference" con stable-diffusion-xl-base-1.0, pero Hugging Face
# dejó de servir ese modelo ahí ("The requested model is deprecated and no longer supported by
# provider hf-inference"). Ahora usamos el cliente oficial con provider="auto": Hugging Face elige
# un proveedor que tenga el modelo activo (fal-ai, nscale, wavespeed...), así un cambio de
# proveedor no vuelve a romper la app.
# El modelo se puede cambiar desde Render con la variable de entorno HF_MODEL, sin tocar código.
API_TOKEN = os.environ.get("HF_TOKEN")  # Se obtiene la clave desde las variables de entorno de Render
MODEL = os.environ.get("HF_MODEL", "black-forest-labs/FLUX.1-schnell")

client = InferenceClient(provider="auto", api_key=API_TOKEN, timeout=90)


@app.route("/generar", methods=["POST"])
def generar():
    # 1. Obtener el prompt enviado desde el frontend
    datos = request.get_json(silent=True) or {}
    prompt = (datos.get("prompt") or "").strip()

    if not prompt:
        return jsonify({"error": "Prompt vacío"}), 400

    if not API_TOKEN:
        return jsonify({"error": "Falta configurar HF_TOKEN en el servidor"}), 500

    try:
        # 2. Pedir la imagen. El cliente devuelve directamente una imagen (PIL.Image)
        imagen = client.text_to_image(prompt, model=MODEL)

        # 3. Convertir la imagen a Base64 para usarla en el atributo 'src' del <img>
        buffer = io.BytesIO()
        imagen.save(buffer, format="PNG")
        image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return jsonify({"imagen": f"data:image/png;base64,{image_base64}"})

    except Exception as e:
        # Errores del proveedor (cuota agotada, modelo no disponible, timeout, token inválido...)
        mensaje = str(e)
        print("Error generando la imagen:", mensaje)

        if "402" in mensaje or "credits" in mensaje.lower():
            return jsonify({"error": "Se agotaron los créditos gratuitos de IA de este mes."}), 503
        if "timed out" in mensaje.lower() or "timeout" in mensaje.lower():
            return jsonify({"error": "El servidor de IA tardó demasiado en responder."}), 504
        return jsonify({"error": "No se pudo generar la imagen. Probá de nuevo en un rato."}), 503


@app.route("/", methods=["GET"])
def home():
    # Ruta de prueba para verificar si el backend está "despierto"
    return "Backend funcionando correctamente 🚀"


if __name__ == "__main__":
    # Render asigna un puerto dinámicamente; lo leemos de la variable de entorno 'PORT'
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
