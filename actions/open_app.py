# -*- coding: utf-8 -*-
"""
open_app.py — Intelligent heuristic application finder and launcher for JARVIS.
"""
import os
import subprocess
import webbrowser
import traceback

def find_executable(app_name: str) -> str:
    """Scan standard system folders recursively to find executable, desktop link, or document matching name."""
    app_lower = app_name.lower().strip()
    
    # 1. Prioritize scanning shortcut files (.lnk) in Start Menu and Desktop first
    try:
        from actions.path_helper import get_desktop_path
        desktop_dir = str(get_desktop_path())
    except Exception:
        desktop_dir = os.path.join(os.path.expanduser("~"), "Desktop")

    start_menu_dirs = [
        os.path.join(os.environ.get("ProgramData", "C:\\ProgramData"), "Microsoft\\Windows\\Start Menu\\Programs"),
        os.path.join(os.environ.get("APPDATA", ""), "Microsoft\\Windows\\Start Menu\\Programs"),
        desktop_dir
    ]
    
    # First pass: Exact match in shortcuts (.lnk)
    for base_dir in start_menu_dirs:
        if not base_dir or not os.path.exists(base_dir):
            continue
        for root, dirs, files in os.walk(base_dir):
            for file in files:
                if file.lower().endswith(".lnk"):
                    file_name_no_ext = os.path.splitext(file)[0].lower().strip()
                    if app_lower == file_name_no_ext:
                        return os.path.join(root, file)
                        
    # Second pass: Partial match in shortcuts (.lnk)
    for base_dir in start_menu_dirs:
        if not base_dir or not os.path.exists(base_dir):
            continue
        for root, dirs, files in os.walk(base_dir):
            for file in files:
                if file.lower().endswith(".lnk"):
                    file_name_no_ext = os.path.splitext(file)[0].lower().strip()
                    if app_lower in file_name_no_ext:
                        return os.path.join(root, file)
                        
    # 2. If no shortcut found, scan Program Files and standard search dirs
    exe_search_dirs = [
        os.path.join(os.environ.get("ProgramFiles", "C:\\Program Files")),
        os.path.join(os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")),
        os.path.join(os.environ.get("LocalAppData", ""), "Programs"),
        os.environ.get("LocalAppData", ""),
        os.environ.get("APPDATA", ""),
        "C:\\Windows\\System32"
    ]
    
    excluded_dirs = ["windowsapps", "redist", "uninst", "drivers", "systemvolumeinformation", "temp", "cache"]
    
    # First pass: Exact match of executable name (.exe)
    for base_dir in exe_search_dirs:
        if not base_dir or not os.path.exists(base_dir):
            continue
        for root, dirs, files in os.walk(base_dir):
            depth = root.count(os.sep) - base_dir.count(os.sep)
            if depth > 4:
                dirs.clear()
                continue
            dirs[:] = [d for d in dirs if d.lower() not in excluded_dirs]
            
            for file in files:
                if file.lower().endswith(".exe"):
                    file_name_no_ext = os.path.splitext(file)[0].lower().strip()
                    if app_lower == file_name_no_ext:
                        return os.path.join(root, file)

    # Second pass: Partial match of executable name (.exe)
    for base_dir in exe_search_dirs:
        if not base_dir or not os.path.exists(base_dir):
            continue
        for root, dirs, files in os.walk(base_dir):
            depth = root.count(os.sep) - base_dir.count(os.sep)
            if depth > 4:
                dirs.clear()
                continue
            dirs[:] = [d for d in dirs if d.lower() not in excluded_dirs]
            
            for file in files:
                if file.lower().endswith(".exe"):
                    file_name_no_ext = os.path.splitext(file)[0].lower().strip()
                    if app_lower in file_name_no_ext:
                        return os.path.join(root, file)

    # 3. Last resort: scan User Documents/Downloads for matching files
    try:
        from actions.path_helper import get_desktop_path, get_documents_path, get_downloads_path
        desktop_dir = str(get_desktop_path())
        documents_dir = str(get_documents_path())
        downloads_dir = str(get_downloads_path())
    except Exception:
        desktop_dir = os.path.join(os.path.expanduser("~"), "Desktop")
        documents_dir = os.path.join(os.path.expanduser("~"), "Documents")
        downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")

    doc_search_dirs = [desktop_dir, documents_dir, downloads_dir]
    doc_extensions = [".docx", ".xlsx", ".pptx", ".pdf", ".txt", ".csv", ".zip", ".png", ".jpg", ".mp3", ".mp4", ".py", ".bat", ".vbs"]
    
    for base_dir in doc_search_dirs:
        if not base_dir or not os.path.exists(base_dir):
            continue
        for root, dirs, files in os.walk(base_dir):
            depth = root.count(os.sep) - base_dir.count(os.sep)
            if depth > 4:
                dirs.clear()
                continue
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in doc_extensions:
                    file_name_no_ext = os.path.splitext(file)[0].lower().strip()
                    if app_lower == file_name_no_ext or app_lower in file_name_no_ext:
                        return os.path.join(root, file)
                        
    return None

def open_app(parameters: dict, response=None, player=None) -> str:
    """Launch local desktop applications, folders, or web URLs heuristically based on app_name."""
    app_name = parameters.get("app_name", "").strip()
    if not app_name:
        return "Error: Se requiere el parámetro 'app_name'."

    app_lower = app_name.lower().strip()

    try:
        # 1. Check if it's a URL
        if app_lower.startswith("http://") or app_lower.startswith("https://") or app_lower.endswith(".com") or app_lower.endswith(".org") or app_lower.endswith(".net") or app_lower.endswith(".es") or app_lower.endswith(".cl"):
            url = app_name if app_lower.startswith("http") else f"https://{app_name}"
            webbrowser.open(url)
            msg = f"Abriendo el sitio web: '{url}'."
            if player:
                player.write_log(f"🌐 {msg}")
            return msg

        # 2. Check if it is a directory path or drive letter
        if os.path.exists(app_name) and os.path.isdir(app_name):
            os.startfile(app_name)
            msg = f"Abriendo la carpeta local: '{app_name}'."
            if player:
                player.write_log(f"📁 {msg}")
            return msg

        # 3. Check virtual directories
        home = os.path.expanduser("~")
        virtual_folders = {
            "desktop": os.path.join(home, "Desktop"),
            "escritorio": os.path.join(home, "Desktop"),
            "downloads": os.path.join(home, "Downloads"),
            "descargas": os.path.join(home, "Downloads"),
            "documents": os.path.join(home, "Documents"),
            "documentos": os.path.join(home, "Documents"),
            "pictures": os.path.join(home, "Pictures"),
            "imagenes": os.path.join(home, "Pictures"),
            "music": os.path.join(home, "Music"),
            "musica": os.path.join(home, "Music"),
            "videos": os.path.join(home, "Videos")
        }
        if app_lower in virtual_folders:
            folder_path = virtual_folders[app_lower]
            os.startfile(folder_path)
            msg = f"Abriendo carpeta del sistema: '{app_lower}'."
            if player:
                player.write_log(f"📁 {msg}")
            return msg

        # 4. Standard Static mappings dictionary
        mappings = {
            "notepad": "notepad.exe",
            "bloc de notas": "notepad.exe",
            "calculator": "calc.exe",
            "calculadora": "calc.exe",
            "chrome": "chrome.exe",
            "google chrome": "chrome.exe",
            "explorer": "explorer.exe",
            "explorador de archivos": "explorer.exe",
            "cmd": "cmd.exe",
            "terminal": "powershell.exe",
            "powershell": "powershell.exe",
            "paint": "mspaint.exe",
            "taskmgr": "taskmgr.exe",
            "administrador de tareas": "taskmgr.exe",
            "word": "winword.exe",
            "microsoft word": "winword.exe",
            "excel": "excel.exe",
            "microsoft excel": "excel.exe",
            "powerpoint": "powerpnt.exe",
            "microsoft powerpoint": "powerpnt.exe",
            "matemática": r"D:\2. MATEMATICA",
            "matemáticas": r"D:\2. MATEMATICA",
            "mate": r"D:\2. MATEMATICA",
            "material de mate": r"D:\2. MATEMATICA",
            "material de matemática": r"D:\2. MATEMATICA",
            "carpeta material de matematica": r"D:\2. MATEMATICA",            
            "colegio coprodeli": r"D:\1. COLEGIOS\2026 Coprodeli",
            "colegio corpus": r"D:\1. COLEGIOS\2026 Coprodeli",
            "colegio corpus 2026": r"D:\1. COLEGIOS\2026 Coprodeli",
            "corpus": r"D:\1. COLEGIOS\2026 Coprodeli",
            "coprodeli": r"D:\1. COLEGIOS\2026 Coprodeli",
            "anotator": "PDFAnnotator.exe",    
            "pdf anotator": "PDFAnnotator.exe",
            "pdf anoteitor": "PDFAnnotator.exe",
            "anoteitor": "PDFAnnotator.exe",
            "dota": "steam://rungameid/570",
            "dota 2": "steam://rungameid/570",
            "juego dota": "steam://rungameid/570"
        }

        executable = None
        for clave, ruta in mappings.items():
            if clave in app_lower:
                executable = ruta
                break
        
        # 5. Custom protocols / special launchers for common apps
        custom_launchers = {
            "whatsapp": "whatsapp:",
            "spotify": "spotify:",
            "steam": "steam:",
            "discord": os.path.expandvars(r"%LocalAppData%\Discord\Update.exe") + " --processStart Discord.exe",
        }

        # 6. Ejecución Lógica Estructurada
        if not executable and app_lower in custom_launchers:
            executable = custom_launchers[app_lower]
        
        if not executable:
            executable = find_executable(app_name)

        if not executable:
            executable = app_name        

        # Launch the resolved application safely using shell execution (prevents space-in-path bugs)
        try:
            os.startfile(executable)
        except Exception:
            # Fallback for raw commands
            # If path has spaces, wrap in double quotes for safe shell launching
            cmd_exec = f'"{executable}"' if " " in executable and not executable.startswith('"') else executable
            subprocess.Popen(cmd_exec, shell=True)

        msg = f"Abriendo la aplicación: '{app_name}'."
        if player:
            player.write_log(f"🚀 {msg}")
        return f"Aplicación '{app_name}' iniciada correctamente (Ruta: {executable})."

    except Exception as e:
        traceback.print_exc()
        return f"Error intentando abrir '{app_name}': {str(e)}"
