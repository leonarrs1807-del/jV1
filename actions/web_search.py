# -*- coding: utf-8 -*-
"""
web_search.py — Búsqueda web silenciosa en segundo plano para JARVIS.
"""
import traceback

def web_search(parameters: dict, player=None) -> str:
    query = parameters.get("query", "").strip()
    if not query:
        return "Error: Se requiere el parámetro 'query' para buscar."

    try:
        from duckduckgo_search import DDGS
        
        if player:
            player.write_log(f"🔍 Investigando en la web: '{query}'...")

        with DDGS() as ddgs:
            # Extrae los 5 resultados más relevantes de forma silenciosa
            results = list(ddgs.text(query, max_results=5))
        
        if not results:
            return f"No se encontró información en internet para: '{query}'."

        # Estructura los datos para que la IA los procese internamente
        formatted_results = f"Resultados de la base de datos web para '{query}':\n\n"
        for i, res in enumerate(results, 1):
            formatted_results += f"[{i}] Título: {res.get('title')}\n"
            formatted_results += f"    Fragmento: {res.get('body')}\n"
            formatted_results += f"    Fuente: {res.get('href')}\n\n"

        formatted_results += "Instrucción estricta para la IA: Lee estos fragmentos, sintetiza la información factual solicitada por el usuario y responde de forma directa basándote exclusivamente en estos datos."
        
        return formatted_results

    except ImportError:
        return "Error: La biblioteca 'duckduckgo-search' no está instalada. Ejecute 'pip install duckduckgo-search' en la terminal."
    except Exception as e:
        return f"Error durante la búsqueda web silenciosa: {str(e)}\n{traceback.format_exc()}"