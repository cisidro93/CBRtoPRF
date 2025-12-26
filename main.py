import flet as ft
import sys
import traceback
import time

# Global var for the engine
conversion_engine = None

def main(page):
    page.title = "Manual Boot"
    page.scroll = "auto"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 30
    
    # --- REFS & PICKER SETUP (Pre-init) ---
    # We define these early to avoid "Unknown Control" errors with dynamic adding
    status_txt_ref = ft.Ref[ft.Text]()
    selected_file_path = ft.Ref[str]()
    
    def on_pick(e):
        if e.files:
            path = e.files[0].path
            selected_file_path.current = path
            
            # Update UI if available
            if status_txt_ref.current:
                status_txt_ref.current.value = f"Selected: {path}"
                status_txt_ref.current.color = "blue"
                page.update()

    # CRITICAL: Add picker to overlay IMMEDIATELY
    picker = ft.FilePicker()
    picker.on_result = on_pick
    page.overlay.append(picker)
    
    # --- BOOTLOADER UI ---
    log_column = ft.Column(scroll="auto")
    
    def log(msg, color="black"):
        print(msg)
        log_column.controls.append(ft.Text(msg, color=color, size=14, selectable=True))
        page.update()

    page.add(
        ft.Text("System Boot (Picker Ready)", size=24, weight="bold", color="blue"),
        ft.Text(f"Python: {sys.version}", size=12),
        ft.Divider(),
        log_column
    )
    
    def load_engine_click(e):
        global conversion_engine
        
        btn_load.disabled = True
        btn_load.text = "Loading..."
        page.update()
        
        log("Attempting Manual Import...")
        
        try:
            import cbz_to_pdf
            
            if hasattr(cbz_to_pdf, 'convert_cbz_to_pdf'):
                conversion_engine = cbz_to_pdf.convert_cbz_to_pdf
                log("Import Successful!", "green")
                launch_app_ui()
            else:
                log("Error: convert_cbz_to_pdf function missing", "red")
                btn_load.disabled = False
                btn_load.text = "Retry Load"
                page.update()
                
        except Exception as e:
            log(f"IMPORT CRASH: {e}", "red")
            log(traceback.format_exc(), "red")
            btn_load.disabled = False
            btn_load.text = "Retry Load"
            page.update()

    def launch_app_ui():
        log("Rendering App UI...")
        page.add(ft.Divider(), ft.Text("--- Converter Ready ---", color="green", weight="bold"))
        
        # --- APP UI ---
        progress_bar = ft.ProgressBar(width=300, visible=False)
        # Use the Ref defined earlier
        status_txt = ft.Text("Ready.", color="green", size=16, ref=status_txt_ref)
        
        def on_progress(p, msg):
            progress_bar.value = p/100
            if status_txt_ref.current:
                status_txt_ref.current.value = msg
            page.update()
            
        def run_convert(e):
            if not selected_file_path.current:
                status_txt.value = "Select file first!"
                page.update()
                return
            
            src = selected_file_path.current
            dst = src.replace(".cbz", ".pdf")
            
            status_txt.value = "Starting..."
            progress_bar.visible = True
            page.update()
            
            import threading
            def worker():
                try:
                    conversion_engine(src, dst, progress_callback=on_progress)
                    status_txt.value = "Done!"
                    page.update()
                except Exception as e:
                    status_txt.value = f"Error: {e}"
                    page.update()
            
            threading.Thread(target=worker).start()

        def safe_pick_files(e):
            try:
                picker.pick_files(allow_multiple=False, allowed_extensions=["cbz"])
            except Exception as ex:
                log(f"PICKER ERROR: {ex}", "red")

        page.add(
            ft.Column([
                ft.ElevatedButton("Select CBZ File", on_click=safe_pick_files),
                ft.ElevatedButton("Convert to PDF", on_click=run_convert),
                progress_bar,
                status_txt
            ])
        )
        page.update()
    
    btn_load = ft.ElevatedButton("LOAD ENGINE", on_click=load_engine_click, bgcolor="blue", color="white")
    page.add(btn_load)
    page.update()

if __name__ == "__main__":
    ft.app(target=main)
