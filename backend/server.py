from flask import Flask, request, jsonify
import requests, base64
from flask_cors import CORS
import os

app = Flask(__name__)

# Configuración de CORS: Permite que tu página en GitHub Pages haga peticiones a este servidor
CORS(app, resources={r"/*": {"origins": "https://nicochandia.github.io"}})

# Configuración de la API de Hugging Face
API_URL = "https://router.huggingface.co/hf-inference/models/stabilityai/stable-diffusion-xl-base-1.0"
API_TOKEN = os.environ.get("HF_TOKEN") # Se obtiene la clave desde las variables de entorno de Render
headers = {"Authorization": f"Bearer {API_TOKEN}"}

@app.route("/generar", methods=["POST"])
def generar():
    # 1. Obtener el prompt enviado desde el frontend
    datos = request.get_json()
    prompt = datos.get("prompt")
    
    if not prompt:
        return jsonify({"error": "Prompt vacío"}), 400

    try:
        # 2. Configurar la carga útil (payload)
        # El parámetro 'wait_for_model' es VITAL: obliga a la API a no responder 
        # hasta que el modelo esté cargado y listo para generar la imagen.
        payload = {
            "inputs": prompt,
            "options": {"wait_for_model": True} 
        }

        # 3. Realizar la petición a Hugging Face
        # timeout=60 da un margen de un minuto para que la IA procese la imagen
        response = requests.post(API_URL, headers=headers, json=payload, timeout=60)

        # 4. Verificar el tipo de contenido de la respuesta
        # Si la respuesta es JSON, significa que ocurrió un error (ej: cuota excedida)
        if "application/json" in response.headers.get("content-type", ""):
            error_info = response.json()
            print("Error detectado de Hugging Face:", error_info)
            # Devolvemos el error específico para que el frontend sepa qué pasó
            return jsonify({"error": error_info.get("error", "Error en la IA")}), 503

        # 5. Si la respuesta es exitosa (Código 200) y es una imagen
        if response.status_code == 200:
            # Convertimos los datos binarios de la imagen a una cadena Base64
            image_bytes = response.content
            image_base64 = base64.b64encode(image_bytes).decode("utf-8")
            
            # Devolvemos un JSON con la imagen formateada para el atributo 'src' de HTML
            return jsonify({"imagen": f"data:image/png;base64,{image_base64}"})
        
        else:
            # Manejo de otros códigos de estado (404, 500, etc.)
            return jsonify({"error": f"La IA respondió con error {response.status_code}"}), response.status_code

    except requests.exceptions.Timeout:
        # Error si la petición tarda más de los 60 segundos definidos
        return jsonify({"error": "El servidor de IA tardó demasiado en responder."}), 504
    except requests.exceptions.RequestException as e:
        # Error general de red o conexión
        print("Excepción de red:", e)
        return jsonify({"error": "Error de conexión con el proveedor de IA"}), 500

@app.route("/", methods=["GET"])
def home():
    # Ruta de prueba para verificar si el backend está "despierto"
    return "Backend funcionando correctamente 🚀"

if __name__ == "__main__":
    # Render asigna un puerto dinámicamente; lo leemos de la variable de entorno 'PORT'
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)