import flet as ft
import sys
import traceback
import time

# Global var for the engine
conversion_engine = None

def main(page):
    page.title = "CBZ Converter (Hybrid)"
    page.scroll = "auto"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 30
    
    # 1. Boot Message
    boot_text = ft.Text("System Boot: Initializing...", color="blue", size=20, weight="bold")
    log_column = ft.Column(scroll="auto")
    page.add(boot_text, log_column)

    def log(msg, color="black"):
        print(msg)
        log_column.controls.append(ft.Text(msg, color=color, size=14))
        page.update()

    log(f"Python: {sys.version}")
    log("Mode: Hybrid (Manual + Optional Picker)")
    
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
        page.clean()
        page.add(ft.Text("CBZ to PDF Converter", size=24, weight="bold"))
        
        # UI Components
        path_input = ft.TextField(label="File Path", width=300, hint_text="/storage/emulated/0/Download/comic.cbz")
        progress_bar = ft.ProgressBar(width=300, visible=False)
        status_txt = ft.Text("Ready. Select file or type path.", color="green")
        
        # --- PICKER LOGIC ---
        picker_ref = ft.Ref[ft.FilePicker]()
        
        def on_picker_result(e):
            if e.files:
                path_input.value = e.files[0].path
                status_txt.value = "File Selected!"
                page.update()
        
        def enable_picker_click(e):
            try:
                status_txt.value = "Initializing Picker..."
                status_txt.color = "blue"
                page.update()
                
                # Dynamic Creation
                p = ft.FilePicker()
                p.on_result = on_picker_result
                picker_ref.current = p
                
                page.overlay.append(p)
                page.update() # This is the critical moment
                
                # If we get here, it worked
                status_txt.value = "Picker Enabled!"
                status_txt.color = "green"
                
                # Show Select Button
                btn_pick_container.content = ft.ElevatedButton("Select CBZ File", on_click=lambda _: p.pick_files(allow_multiple=False, allowed_extensions=["cbz"]))
                page.update()
                
            except Exception as ex:
                status_txt.value = f"Picker Failed: {ex}"
                status_txt.color = "red"
                page.update()
                
        # Container to swap "Enable" -> "Select"
        btn_pick_container = ft.Container(
            content=ft.ElevatedButton("Enable File Picker", on_click=enable_picker_click)
        )

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
            
            dst = src.replace(".cbz", ".pdf")
            
            status_txt.value = f"Converting: {src}"
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
            ft.Column([
                path_input,
                ft.Container(height=10),
                btn_pick_container, # Dynamic button
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
