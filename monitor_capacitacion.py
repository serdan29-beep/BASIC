import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

# Configuración de búsqueda
KEYWORDS = ["Python", "Datos", "Presupuesto", "Patrimonio", "Contabilidad", "GDE", "Excel", "BI"]
SITIOS = {
    "MECON": "https://capacitacion.mecon.gob.ar/",
    "Capacitar": "https://www.argentina.gob.ar/capacitar",
    "Consejo": "https://www.consejo.org.ar/capacitacion-profesional",
    "INAP": "https://capacitacion.inap.gob.ar/",
    "AGENCIA_CABA": "https://www.google.com/search?q=https://buenosaires.gob.ar/educacion/agencia-de-aprendizaje-a-lo-largo-de-la-vida",
    "UBA_Economicas": "https://economicas.uba.ar/graduados/ciclos-talleres-y-conferencias-semanales/"
}

def cargar_historial(archivo):
    """Carga el historial de cursos para evitar duplicados."""
    try:
        # Usamos pandas para leer el txt que ya tenés
        df = pd.read_csv(archivo, sep='\t', encoding='utf-16')
        return df['Nombre Actividad'].tolist()
    except:
        return []

def scrape_generic(name, url):
    """Lógica básica de scraping para sitios con listas de texto."""
    print(f"--- Revisando {name} ---")
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Buscamos textos que contengan nuestras palabras clave
        encontrados = []
        for texto in soup.find_all(['h3', 'h4', 'a', 'p']):
            contenido = texto.get_text().strip()
            if any(key.lower() in contenido.lower() for key in KEYWORDS):
                if contenido not in encontrados:
                    encontrados.append(contenido)
        return encontrados
    except Exception as e:
        return [f"Error al acceder: {e}"]

def ejecutar_agente():
    historial = cargar_historial('Cursosa2025.txt')
    resumen = []

    for nombre, url in SITIOS.items():
        ofertas = scrape_generic(nombre, url)
        for oferta in ofertas:
            # Filtro: si no está en el historial y es relevante, lo guardamos
            if oferta not in historial:
                resumen.append(f"[{nombre}] {oferta} - Link: {url}")

    if resumen:
        print("\nNuevas oportunidades encontradas:")
        for r in resumen:
            print(r)
    else:
        print("\nNo se encontraron cursos nuevos esta semana.")

if __name__ == "__main__":
    ejecutar_agente()