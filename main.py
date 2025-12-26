import flet as ft
import time
import threading
import sys
import traceback

# Global var for the engine
conversion_engine = None

def main(page):
    page.title = "Bootloader"
    page.scroll = "auto"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 30
    
    # Text buffer
    log_column = ft.Column(scroll="auto")
    title = ft.Text("System Boot", size=24, weight="bold", color="blue")
    
    page.add(title, ft.Divider(), log_column)
    page.update()

    def log(msg, color="black"):
        # Append text safely
        print(msg)
        log_column.controls.append(ft.Text(msg, color=color, size=14, selectable=True))
        page.update()

    log(f"Python: {sys.version}")
    log("UI Rendered. Starting loader thread...")

    def loader_task():
        global conversion_engine
        try:
            log("Thread: Started. Waiting 1s...")
            time.sleep(1.0)
            
            log("Thread: Attempting import of cbz_to_pdf...")
            try:
                # 1. Import module
                import cbz_to_pdf
                log("Thread: Module imported. Checking function...")
                
                # 2. Check function
                if hasattr(cbz_to_pdf, 'convert_cbz_to_pdf'):
                    conversion_engine = cbz_to_pdf.convert_cbz_to_pdf
                    log("Thread: Engine validated.", "green")
                else:
                    log("Thread: ERROR - Function convert_cbz_to_pdf not found!", "red")
                    return
                    
            except Exception as e:
                 log(f"Thread: IMPORT FAIL: {e}", "red")
                 log(traceback.format_exc(), "red")
                 return
            
            log("Thread: Ready to launch App. Switching UI in 1s...")
            time.sleep(1.0)
            
            # RUN UI SWAP ON MAIN THREAD
            # Flet is usually thread-safe for page.clean() but let's be careful.
            # We'll just append the real UI below the log for now to avoid clearing 'useful' crash info.
            
            # Actually, let's clear to test if that works.
            # page.clean() 
            # If page.clean() crashes, we'll know.
            
            launch_app_ui()
            
        except Exception as e:
            log(f"Thread: CRASH: {e}", "red")
            log(traceback.format_exc(), "red")
    
    def launch_app_ui():
        try:
            log("Launching Main UI...")
            page.clean()
            
            # --- APP UI ---
            page.title = "CBZ Converter"
            
            selected_file = ft.Ref[str]()
            status_txt = ft.Text("Engine Ready.", color="green", size=16)
            progress_bar = ft.ProgressBar(width=300, visible=False)
            
            def on_progress(p, msg):
                progress_bar.value = p/100
                status_txt.value = msg
                page.update()
                
            def run_convert():
                if not selected_file.current:
                    status_txt.value = "Select file first!"
                    page.update()
                    return
                
                src = selected_file.current
                dst = src.replace(".cbz", ".pdf")
                
                status_txt.value = "Starting..."
                progress_bar.visible = True
                page.update()
                
                def worker():
                    try:
                        conversion_engine(src, dst, progress_callback=on_progress)
                        status_txt.value = "Done!"
                        page.update()
                    except Exception as e:
                        status_txt.value = f"Error: {e}"
                        page.update()
                
                threading.Thread(target=worker).start()

            def on_pick(e):
                if e.files:
                    path = e.files[0].path
                    selected_file.current = path
                    status_txt.value = f"Selected: {path}"
                    page.update()

            picker = ft.FilePicker(on_result=on_pick)
            page.overlay.append(picker)
            
            page.add(
                ft.Column([
                    ft.Text("CBZ -> PDF", size=30),
                    ft.ElevatedButton("Select File", on_click=lambda _: picker.pick_files(allow_multiple=False, allowed_extensions=["cbz"])),
                    ft.ElevatedButton("Convert", on_click=lambda _: run_convert()),
                    progress_bar,
                    status_txt
                ])
            )
            page.update()
            # --- END APP UI ---
            
        except Exception as e:
            # If UI launch fails, we probably cleaned the page, so add text back
            page.add(ft.Text(f"UI Launch Failed: {e}", color="red"))
            page.update()

    # Start thread
    t = threading.Thread(target=loader_task, daemon=True)
    t.start()

if __name__ == "__main__":
    ft.app(target=main)
