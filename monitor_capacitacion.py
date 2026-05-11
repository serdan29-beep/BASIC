import os
import requests
import pandas as pd

# 1. VERIFICACIÓN DE SECRETOS (Sin mostrar el token completo por seguridad)
token = os.getenv('TOKEN')
chat_id = os.getenv('CHAT_ID')

print(f"--- Diagnóstico de Inicio ---")
print(f"Token detectado: {'SÍ' if token else 'NO'}")
print(f"Chat ID detectado: {'SÍ' if chat_id else 'NO'}")

def enviar_telegram(mensaje):
    if not token or not chat_id:
        print("Error: Faltan credenciales de Telegram.")
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    print(f"DEBUG: Intentando conectar a {url}") # Agrega esto
    payload = {"chat_id": chat_id, "text": mensaje}
    try:
        r = requests.post(url, json=payload)
        print(f"Resultado envío Telegram: {r.status_code}")
        if r.status_code != 200:
            print(f"Detalle del error: {r.text}")
    except Exception as e:
        print(f"Falla en la conexión: {e}")

# 2. PRUEBA DE VIDA (Apenas arranca el script)
enviar_telegram("🤖 Agente iniciado. Buscando cursos nuevos...")

def ejecutar_monitoreo():
    # Aquí iría tu lógica de scraping...
    # ASEGÚRATE de poner un print cada vez que encuentres algo
    encontrados = ["Prueba de curso 1", "Prueba de curso 2"] # Simulación
    
    print(f"Cursos encontrados en la web: {len(encontrados)}")
    
    # Supongamos que comparas con el historial
    nuevos = []
    for c in encontrados:
        # Aquí imprimiría por qué descarta o acepta
        print(f"Analizando: {c}...")
        nuevos.append(c)
    
    if nuevos:
        print(f"Enviando {len(nuevos)} notificaciones...")
        for n in nuevos:
            enviar_telegram(f"📌 Nuevo curso: {n}")
    else:
        print("No se encontraron cursos nuevos fuera del historial.")

if __name__ == "__main__":
    ejecutar_monitoreo()
