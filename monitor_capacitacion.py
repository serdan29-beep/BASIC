import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

# --- CONFIGURACIÓN DE ACCESO ---
token = os.getenv('TOKEN', '').strip()
chat_id = os.getenv('CHAT_ID', '').strip()

if token.lower().startswith('bot'):
    token = token[3:]

def enviar_telegram(mensaje):
    """Envía notificaciones al bot de Telegram."""
    if not token or not chat_id:
        print("❌ Error: TOKEN o CHAT_ID no configurados.")
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": mensaje, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"💥 Error enviando a Telegram: {e}")

# --- PARÁMETROS DE BÚSQUEDA ---
# Incluimos los términos bilingües para aprovechar tu nivel C1/C2 de inglés
KEYWORDS = [
    "Python", "Datos", "Presupuesto", "Patrimonio", "Contabilidad", 
    "GDE", "Excel", "BI", "Data Science", "Public Finance", 
    "Accounting", "Automation", "Audit", "Gestión Pública"
]

SITIOS = {
    "MECON": "https://capacitacion.mecon.gob.ar/",
    "Capacitar": "https://www.argentina.gob.ar/capacitar",
    "Consejo": "https://www.consejo.org.ar/capacitacion-profesional",
    "INAP": "https://capacitacion.inap.gob.ar/",
    "UBA_Economicas": "https://economicas.uba.ar/graduados/ciclos-talleres-y-conferencias-semanales/",
    "Coursera_Data": "https://www.coursera.org/search?query=data%20analysis%20free",
    "edX_Public": "https://www.edx.org/search?q=public+administration&tab=course",
    "IMF_Academy": "https://www.edx.org/school/imfx"
}

def cargar_historial(archivo):
    """Lee tu historial Cursosa2025.txt para no repetir avisos."""
    try:
        # Mantenemos el encoding utf-16 y separador tabulado de tu archivo original
        df = pd.read_csv(archivo, sep='\t', encoding='utf-16')
        return df['Nombre Actividad'].tolist()
    except Exception as e:
        print(f"⚠️ No se pudo leer el historial: {e}")
        return []

def scrape_generic(name, url):
    """Busca palabras clave en los sitios definidos."""
    print(f"🔍 Revisando {name}...")
    try:
        response = requests.get(url, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        encontrados = []
        # Buscamos en títulos, enlaces y párrafos
        for texto in soup.find_all(['h3', 'h4', 'a', 'p']):
            contenido = texto.get_text().strip()
            if len(contenido) > 10 and any(key.lower() in contenido.lower() for key in KEYWORDS):
                if contenido not in encontrados:
                    encontrados.append(contenido)
        return encontrados
    except Exception as e:
        print(f"❌ Error en {name}: {e}")
        return []

def ejecutar_agente():
    historial = cargar_historial('Cursosa2025.txt')
    nuevas_ofertas = []

    # Recorremos todos los sitios (locales e internacionales)
    for nombre, url in SITIOS.items():
        ofertas = scrape_generic(nombre, url)
        for oferta in ofertas:
            # Filtramos contra tu historial de años anteriores (e-SIDIF, Oracle BI, etc.)
            if oferta not in historial:
                nuevas_ofertas.append(f"🔹 *{nombre}*: {oferta}\n🔗 [Link]({url})")

    if nuevas_ofertas:
        mensaje_final = "🤖 *Nuevas oportunidades de capacitación:*\n\n" + "\n\n".join(nuevas_ofertas)
        enviar_telegram(mensaje_final)
        print(f"✅ Se enviaron {len(nuevas_ofertas)} ofertas a Telegram.")
    else:
        print("📭 No se encontraron novedades esta semana.")

if __name__ == "__main__":
    print("--- Agente de Capacitación v2.0 Ampliada ---")
    ejecutar_agente()