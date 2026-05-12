import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

# --- CREDENCIALES ---
token = os.getenv('TOKEN', '').strip()
chat_id = os.getenv('CHAT_ID', '').strip()
if token.lower().startswith('bot'): token = token[3:]

# --- CONFIGURACIÓN DE NAVEGACIÓN ---
# Esto evita que los sitios internacionales nos bloqueen
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def enviar_telegram(mensaje):
    if not token or not chat_id: return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": mensaje, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"💥 Error Telegram: {e}")

def cargar_historial(archivo):
    """Lectura robusta del historial."""
    try:
        # Probamos con utf-16 que es como parece estar tu archivo
        df = pd.read_csv(archivo, sep='\t', encoding='utf-16')
        # Limpiamos nombres de columnas por si hay espacios invisibles
        df.columns = df.columns.str.strip()
        return df['Nombre Actividad'].unique().tolist()
    except Exception as e:
        print(f"⚠️ Error utf-16, probando utf-8: {e}")
        try:
            # Reintento con utf-8 por las dudas
            df = pd.read_csv(archivo, sep='\t', encoding='utf-8')
            df.columns = df.columns.str.strip()
            return df['Nombre Actividad'].unique().tolist()
        except:
            print("❌ No se pudo leer el historial de ninguna forma.")
            return []

# --- BÚSQUEDA ---
KEYWORDS = ["Python", "Datos", "Presupuesto", "Patrimonio", "Contabilidad", "BI", "Data Science", "Public Finance"]
SITIOS = {
    "MECON": "https://capacitacion.mecon.gob.ar/",
    "Capacitar": "https://www.argentina.gob.ar/capacitar",
    "INAP": "https://capacitacion.inap.gob.ar/",
    "Coursera_Data": "https://www.coursera.org/search?query=data%20analysis%20free",
    "edX_Public": "https://www.edx.org/search?q=public+administration",
}

def ejecutar_agente():
    # Aviso de inicio para que sepas que el bot está vivo
    enviar_telegram("🔄 *Agente iniciado:* Buscando capacitaciones...")
    
    historial = cargar_historial('Cursosa2025.txt')
    print(f"Cursos en historial: {len(historial)}")
    
    nuevas_ofertas = []
    for nombre, url in SITIOS.items():
        print(f"🔍 Revisando {nombre}...")
        try:
            # Agregamos los HEADERS para no ser bloqueados
            r = requests.get(url, headers=HEADERS, timeout=15)
            soup = BeautifulSoup(r.text, 'html.parser')
            for tag in soup.find_all(['h3', 'h4', 'a']):
                txt = tag.get_text().strip()
                if len(txt) > 10 and any(k.lower() in txt.lower() for k in KEYWORDS):
                    # Solo agregamos si no está en tu historial (e-SIDIF, Oracle, etc)
                    if not any(h.lower() in txt.lower() for h in historial):
                        item = f"🔹 *{nombre}*: {txt}\n🔗 [Link]({url})"
                        if item not in nuevas_ofertas: nuevas_ofertas.append(item)
        except Exception as e:
            print(f"❌ Error en {nombre}: {e}")

    if nuevas_ofertas:
        # Mandamos de a 5 para no saturar Telegram
        for i in range(0, len(nuevas_ofertas), 5):
            enviar_telegram("\n\n".join(nuevas_ofertas[i:i+5]))
    else:
        enviar_telegram("📭 Por ahora no hay cursos nuevos que coincidan con tu perfil.")

if __name__ == "__main__":
    ejecutar_agente()
