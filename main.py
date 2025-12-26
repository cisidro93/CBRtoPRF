import flet as ft
import sys
import os
import traceback
import time

# Global var for the engine
conversion_engine = None

def main(page):
    page.title = "CBZ Converter (Text Only)"
    page.scroll = "auto"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20
    
    # 1. Boot Message
    boot_text = ft.Text("System Boot: Initializing...", color="blue", size=16, weight="bold")
    log_column = ft.Column(scroll="auto")
    page.add(boot_text, log_column)

    def log(msg, color="black"):
        print(msg)
        log_column.controls.append(ft.Text(msg, color=color, size=12))
        page.update()

    log(f"Python: {sys.version}")
    log("Mode: Text-Only Browser (Safe)")
    
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
        try:
            page.clean()
            page.add(ft.Text("CBZ to PDF Converter", size=24, weight="bold"))
            
            # UI Components
            path_input = ft.TextField(label="File Path", value="/storage/emulated/0/Download", expand=True)
            progress_bar = ft.ProgressBar(width=300, visible=False)
            status_txt = ft.Text("Ready. Browse or type path.", color="green")
            
            # --- CUSTOM FILE BROWSER LOGIC ---
            current_browser_path = "/storage/emulated/0/Download"
            if not os.path.exists(current_browser_path):
                current_browser_path = "/storage/emulated/0" # Fallback
                
            browser_list = ft.ListView(expand=True, spacing=10, padding=10, height=300)
            browser_path_display = ft.Text(current_browser_path, size=12, color="grey")
            
            def close_browser(e):
                browser_dialog.open = False
                page.update()
                
            def select_file(path):
                path_input.value = path
                status_txt.value = f"Selected: {os.path.basename(path)}"
                browser_dialog.open = False
                page.update()
                
            def navigate_to(path):
                nonlocal current_browser_path
                try:
                    items = sorted(os.listdir(path))
                    browser_list.controls.clear()
                    
                    # Add ".." for parent
                    parent = os.path.dirname(path)
                    browser_list.controls.append(
                        ft.ElevatedButton(".. (Up)", on_click=lambda _: navigate_to(parent), bgcolor="grey", color="white")
                    )
                    
                    for item in items:
                        full_path = os.path.join(path, item)
                        if os.path.isdir(full_path):
                            # Directory
                             browser_list.controls.append(
                                ft.OutlinedButton(f"[DIR] {item}", on_click=lambda _, p=full_path: navigate_to(p))
                            )
                        elif item.lower().endswith('.cbz'):
                            # CBZ File
                            browser_list.controls.append(
                                ft.ElevatedButton(f"[FILE] {item}", on_click=lambda _, p=full_path: select_file(p), bgcolor="blue", color="white")
                            )
                    
                    current_browser_path = path
                    browser_path_display.value = path
                    browser_dialog.update()
                    
                except PermissionError:
                    browser_path_display.value = f"Access Denied: {path}"
                    browser_path_display.color = "red"
                    browser_dialog.update()
                except Exception as e:
                    browser_path_display.value = f"Error: {e}"
                    browser_dialog.update()

            browser_dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text("Select CBZ File"),
                content=ft.Column([
                    browser_path_display,
                    ft.Divider(),
                    browser_list
                ], height=400, width=300),
                actions=[
                    ft.TextButton("Cancel", on_click=close_browser)
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )

            def open_browser(e):
                page.dialog = browser_dialog
                browser_dialog.open = True
                navigate_to(current_browser_path) # Initial load
                page.update()

            # Input Row - REPLACED ICON WITH BUTTON
            input_row = ft.Row([
                path_input,
                ft.ElevatedButton("Browse", on_click=open_browser)
            ])

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
                ft.Column([
                    ft.Container(height=10),
                    input_row,
                    ft.Container(height=10),
                    ft.ElevatedButton("Convert to PDF", on_click=run_convert),
                    ft.Container(height=20),
                    progress_bar,
                    status_txt
                ])
            )
            page.update()
            
        except Exception as e:
            # THIS IS CRITICAL
            page.add(ft.Text(f"CRASH: {e}", color="red", size=20, weight="bold"))
            page.add(ft.Text(traceback.format_exc(), color="red", size=10))
            page.update()

    btn_load = ft.ElevatedButton("LOAD ENGINE", on_click=load_engine_click, bgcolor="blue", color="white")
    page.add(ft.Divider(), btn_load)
    page.update()

if __name__ == "__main__":
    ft.app(target=main)
