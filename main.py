import flet as ft
import sys
import traceback
import time

# Global var for the engine
conversion_engine = None

def main(page):
    page.title = "CBZ Converter"
    page.scroll = "auto"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 30
    
    # 1. Immediate Boot Message
    boot_text = ft.Text("System Boot: Initializing...", color="blue", size=20, weight="bold")
    log_column = ft.Column(scroll="auto")
    page.add(boot_text, log_column)
    page.update()
    
    # 2. Safe Picker Setup
    status_txt_ref = ft.Ref[ft.Text]()
    selected_file_path = ft.Ref[str]()
    
    def on_pick(e):
        if e.files:
            path = e.files[0].path
            selected_file_path.current = path
            if status_txt_ref.current:
                status_txt_ref.current.value = f"Selected: {path}"
                status_txt_ref.current.color = "blue"
                status_txt_ref.current.update()

    # FIX: Instantiate first, assign property second
    picker = ft.FilePicker()
    picker.on_result = on_pick
    page.overlay.append(picker)
    page.update()
    
    def log(msg, color="black"):
        print(msg)
        log_column.controls.append(ft.Text(msg, color=color, size=14))
        page.update()

    log(f"Python: {sys.version}")
    log("FilePicker: Registered successfully.")
    
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
                launch_app_ui()
            else:
                log("Error: convert function missing", "red")
                btn_load.disabled = False
                
        except Exception as e:
            log(f"IMPORT ERROR: {e}", "red")
            btn_load.disabled = False

    def launch_app_ui():
        page.clean() # We can try cleaning now that we are stable
        page.add(ft.Text("CBZ to PDF Converter", size=24, weight="bold"))
        
        # UI Components
        progress_bar = ft.ProgressBar(width=300, visible=False)
        status_txt = ft.Text("Ready. Select a file.", color="green", ref=status_txt_ref)
        
        def on_progress(p, msg):
            progress_bar.value = p/100
            if status_txt_ref.current:
                status_txt_ref.current.value = msg
                status_txt_ref.current.update()
            page.update()
            
        def run_convert(e):
            if not selected_file_path.current:
                status_txt.value = "Please select a file first."
                status_txt.color = "red"
                page.update()
                return
            
            src = selected_file_path.current
            dst = src.replace(".cbz", ".pdf")
            
            status_txt.value = "Starting conversion..."
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
        
        def safe_pick(e):
            try:
                picker.pick_files(allow_multiple=False, allowed_extensions=["cbz"])
            except Exception as ex:
                status_txt.value = f"Picker Error: {ex}"
        
        page.add(
            ft.Column([
                ft.Container(height=20),
                ft.ElevatedButton("Select CBZ File", on_click=safe_pick),
                ft.Container(height=10),
                ft.ElevatedButton("Convert to PDF", on_click=run_convert),
                ft.Container(height=20),
                progress_bar,
                status_txt
            ])
        )
        page.update()

    btn_load = ft.ElevatedButton("LOAD ENGINE", on_click=load_engine_click, bgcolor="blue", color="white")
    page.add(ft.Divider(), btn_load)
    page.update()

if __name__ == "__main__":
    ft.app(target=main)
