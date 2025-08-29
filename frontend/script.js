async function generar() {
  const prompt = document.getElementById("prompt").value;
  const img = document.getElementById("resultado");

  img.src = "";
  img.alt = "Generando...";

  // ⚠️ Poné aquí la URL de tu backend en Render
  const backendUrl = "https://tu-backend.onrender.com/generar";

  const response = await fetch(backendUrl, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt }),
  });

  if (!response.ok) {
    img.alt = "Error al generar la imagen";
    return;
  }

  const data = await response.json();
  img.src = data.imagen;
  img.alt = "Imagen generada";
}
