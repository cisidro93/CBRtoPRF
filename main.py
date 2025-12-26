import flet as ft
import sys
import os
import traceback
import time

# Global var for the engine
conversion_engine = None

def main(page):
    page.title = "CBZ Converter (Page Swap)"
    page.scroll = "auto"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20
    
    # Global State
    state = {
        "current_path": "/storage/emulated/0/Download",
        "selected_file": "/storage/emulated/0/Download",
    }
    
    # 1. Boot Message
    boot_text = ft.Text("System Boot: Initializing...", color="blue", size=16, weight="bold")
    log_column = ft.Column(scroll="auto")
    page.add(boot_text, log_column)

    def log(msg, color="black"):
        print(msg)
        log_column.controls.append(ft.Text(msg, color=color, size=12))
        page.update()

    log(f"Python: {sys.version}")
    log("Mode: Full Page Browser (No Dialogs)")
    
    def load_engine_click(e):
        global conversion_engine
        
        btn_load.disabled = True
        btn_load.text = "Loading Engine..."
        page.update()
        
        try:
            log("Importing CBZ Engine...")
            import cbz_to_pdf
            
            if hasattr(cbz_to_pdf, 'convert_cbz_to_pdf'):
                conversion_engine = cbz_to_pdf.convert_cbz_to_pdf
                log("Engine Loaded!", "green")
                show_main_ui()
            else:
                log("Error: convert function missing", "red")
                btn_load.disabled = False
                
        except Exception as e:
            log(f"IMPORT ERROR: {e}", "red")
            btn_load.disabled = False

    # --- MAIN CONVERTER SCREEN ---
    def show_main_ui():
        page.clean()
        
        path_input = ft.TextField(
            label="File Path", 
            value=state["selected_file"], 
            expand=True
        )
        progress_bar = ft.ProgressBar(width=300, visible=False)
        status_txt = ft.Text("Ready. Browse or type path.", color="green")
        
        def on_browse_click(e):
            show_browser_ui(state["current_path"])

        def on_progress(p, msg):
            progress_bar.value = p/100
            status_txt.value = msg
            status_txt.update()
            page.update()
            
        def run_convert(e):
            src = path_input.value
            if not src:
                status_txt.value = "Enter a path first."
                status_txt.color = "red"
                page.update()
                return
            
            state["selected_file"] = src # Save manually typed path
            dst = src.replace(".cbz", ".pdf")
            
            status_txt.value = f"Converting: {os.path.basename(src)}"
            status_txt.color = "black"
            progress_bar.visible = True
            page.update()
            
            import threading
            def worker():
                try:
                    conversion_engine(src, dst, progress_callback=on_progress)
                    status_txt.value = "Conversion Complete!"
                    status_txt.color = "green"
                    page.update()
                except Exception as e:
                    status_txt.value = f"Error: {e}"
                    status_txt.color = "red"
                    page.update()
            
            threading.Thread(target=worker).start()
            
        page.add(
            ft.Text("CBZ to PDF Converter", size=24, weight="bold"),
            ft.Container(height=10),
            ft.Row([
                path_input,
                ft.ElevatedButton("Browse", on_click=on_browse_click)
            ]),
            ft.Container(height=10),
            ft.ElevatedButton("Convert to PDF", on_click=run_convert),
            ft.Container(height=20),
            progress_bar,
            status_txt
        )
        page.update()

    # --- FULL PAGE FILE BROWSER ---
    def show_browser_ui(start_path):
        page.clean()
        
        # Ensure path exists
        if not os.path.exists(start_path):
            start_path = "/storage/emulated/0"
        
        state["current_path"] = start_path
        
        file_list = ft.Column(scroll="auto", expand=True)
        path_display = ft.Text(start_path, color="grey", size=12)
        
        def navigate(path):
            show_browser_ui(path)
            
        def select(path):
            state["selected_file"] = path
            state["current_path"] = os.path.dirname(path)
            show_main_ui()
            
        def go_back(e):
            show_main_ui()

        # Build List
        try:
            parent = os.path.dirname(start_path)
            
            # Navigation Helpers
            file_list.controls.append(
                ft.Row([
                    ft.ElevatedButton(".. (UP)", on_click=lambda _: navigate(parent), expand=True, bgcolor="grey", color="white"),
                    ft.ElevatedButton("/storage (ROOT)", on_click=lambda _: navigate("/storage"), expand=True, bgcolor="orange", color="white"),
                ])
            )
            
            items = sorted(os.listdir(start_path))
            for item in items:
                full_path = os.path.join(start_path, item)
                if os.path.isdir(full_path):
                    file_list.controls.append(
                        ft.OutlinedButton(f"[DIR]  {item}", on_click=lambda _, p=full_path: navigate(p), width=300)
                    )
                elif item.lower().endswith('.cbz'):
                    file_list.controls.append(
                        ft.ElevatedButton(f"[FILE] {item}", on_click=lambda _, p=full_path: select(p), width=300, bgcolor="blue", color="white")
                    )
        except Exception as e:
            file_list.controls.append(ft.Text(f"Error listing files: {e}", color="red"))

        page.add(
            ft.Text("Select File", size=24, weight="bold"),
            path_display,
            ft.Divider(),
            ft.Container(content=file_list, height=400, border=ft.border.all(1, "grey"), padding=5),
            ft.Divider(),
            ft.ElevatedButton("Cancel", on_click=go_back)
        )
        page.update()

    btn_load = ft.ElevatedButton("LOAD ENGINE", on_click=load_engine_click, bgcolor="blue", color="white")
    page.add(ft.Divider(), btn_load)
    page.update()

if __name__ == "__main__":
    ft.app(target=main)
