import urllib.request
import urllib.parse
import re
import webbrowser
import traceback

def web_navigation(parameters: dict, player=None) -> str:
    """
    Maneja la navegación web unificada para búsquedas y reproducción multimedia.
    """
    action = parameters.get("action", "").lower().strip()
    query = parameters.get("query", "").strip()

    if not action or not query:
        return "Error: Faltan parámetros ('action' o 'query')."

    try:
        # Agrupación de todas las posibles llamadas relacionadas con YouTube
        if action in ["play_youtube", "youtube", "youtube_video"]:
            search_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
            try:
                # Petición con User-Agent para evitar bloqueos básicos y timeout de seguridad
                req = urllib.request.Request(search_url, headers={'User-Agent': 'Mozilla/5.0'})
                html = urllib.request.urlopen(req, timeout=5).read().decode('utf-8')
                
                video_ids = re.findall(r"watch\?v=(\S{11})", html)
                if video_ids:
                    first_video_id = video_ids[0]
                    video_url = f"https://www.youtube.com/watch?v={first_video_id}"
                    
                    webbrowser.open(video_url)
                    
                    msg = f"Reproduciendo '{query}' en YouTube automáticamente."
                    if player:
                        if hasattr(player, "set_state"):
                            player.set_state("SUCCESS")
                        player.write_log(f"▶️ {msg} (URL: {video_url})")
                        
                    return msg
                else:
                    webbrowser.open(search_url)
                    return f"Abrí los resultados de búsqueda en YouTube para '{query}'. No se encontró un ID de video válido para reproducción automática."
            except Exception as e_req:
                webbrowser.open(search_url)
                return f"Abrí YouTube con tu búsqueda '{query}'. Interrupción en la extracción de enlace directo: {e_req}"

        elif action == "search":
            search_url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
            webbrowser.open(search_url)
            msg = f"Búsqueda en Google abierta para '{query}'."
            if player:
                player.write_log(f"🔍 {msg}")
            return msg

        else:
            return f"Error: Acción web '{action}' desconocida o no enrutada."

    except Exception as e:
        return f"Error estructural al navegar: {str(e)}\n{traceback.format_exc()}"