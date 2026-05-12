import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

# --- CREDENCIALES ---
token = os.getenv('TOKEN', '').strip()
chat_id = os.getenv('CHAT_ID', '').strip()
if token.lower().startswith('bot'): token = token[3:]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# --- FILTROS DE ESTADO ---
# Si el texto del curso contiene alguna de estas, el bot lo ignora
TERMINOS_NEGATIVOS = ["finalizado", "suspendido", "sin vacantes", "inscripción cerrada", "cupo lleno"]

def enviar_telegram(mensaje):
    if not token or not chat_id: return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": mensaje, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"💥 Error Telegram: {e}")

def cargar_historial(archivo):
    try:
        df = pd.read_csv(archivo, sep='\t', encoding='utf-16')
        df.columns = df.columns.str.strip()
        return df['Nombre Actividad'].unique().tolist()
    except:
        try:
            df = pd.read_csv(archivo, sep='\t', encoding='utf-8')
            df.columns = df.columns.str.strip()
            return df['Nombre Actividad'].unique().tolist()
        except:
            return []

KEYWORDS = ["Python", "Datos", "Presupuesto", "Patrimonio", "Contabilidad", "BI", "Data Science", "Public Finance", "Inglés"]
SITIOS = {
    "MECON": "https://capacitacion.mecon.gob.ar/",
    "Capacitar": "https://www.argentina.gob.ar/capacitar",
    "INAP": "https://capacitacion.inap.gob.ar/",
    "Coursera": "https://www.coursera.org/search?query=data%20analysis%20free",
    "edX": "https://www.edx.org/search?q=public+administration",
    "UBA_Econ": "https://economicas.uba.ar/graduados/ciclos-talleres-y-conferencias-semanales/"
}

def ejecutar_agente():
    enviar_telegram("🔄 *Agente actualizado:* Buscando solo cursos con vacantes...")
    historial = cargar_historial('Cursosa2025.txt')
    nuevas_ofertas = []

    for nombre, url in SITIOS.items():
        print(f"🔍 Revisando {nombre}...")
        try:
            r = requests.get(url, headers=HEADERS, timeout=15)
            soup = BeautifulSoup(r.text, 'html.parser')
            for tag in soup.find_all(['h3', 'h4', 'a', 'p']):
                txt = tag.get_text().strip()
                
                # 1. Verificamos longitud y palabras clave
                if len(txt) > 10 and any(k.lower() in txt.lower() for k in KEYWORDS):
                    
                    # 2. NUEVO FILTRO: Verificamos que NO tenga términos negativos
                    if any(neg.lower() in txt.lower() for neg in TERMINOS_NEGATIVOS):
                        print(f"🚫 Saltando curso sin cupo/finalizado: {txt[:30]}...")
                        continue
                    
                    # 3. Verificamos que NO esté en el historial
                    if not any(h.lower() in txt.lower() for h in historial):
                        item = f"🔹 *{nombre}*: {txt}\n🔗 [Link]({url})"
                        if item not in nuevas_ofertas: nuevas_ofertas.append(item)
        except Exception as e:
            print(f"❌ Error en {nombre}: {e}")

    if nuevas_ofertas:
        for i in range(0, len(nuevas_ofertas), 5):
            enviar_telegram("\n\n".join(nuevas_ofertas[i:i+5]))
    else:
        enviar_telegram("📭 No hay novedades con vacantes disponibles por el momento.")

if __name__ == "__main__":
    ejecutar_agente()
