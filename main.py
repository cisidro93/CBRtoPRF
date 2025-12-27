import flet as ft
import sys
import os
import traceback
import time

# Global var for the engine
conversion_engine = None

def main(page):
    page.title = "CBZ Converter (iOS Safe)"
    # page.scroll = "auto"  <-- REMOVED to prevent Red Screen
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 10
    
    # Global State
    state = {
        "current_path": "/storage/emulated/0/Download",
        "selected_file": "/storage/emulated/0/Download",
        "compress_enabled": False,
        "email_sender": "",
        "email_password": "",
        "email_recipient": ""
    }
    
    # --- GLOBAL UI COMPONENTS ---
    # ListView is safe for potentially infinite logs inside a fixed container
    log_list = ft.ListView(expand=True, spacing=2, auto_scroll=True)
    
    # 1. Boot Message
    boot_text = ft.Text("System Boot: Initializing...", color="blue", size=16, weight="bold")
    
    # Main Container
    main_layout = ft.Column(expand=True, controls=[
        boot_text,
        ft.Container(content=log_list, expand=True, border=ft.border.all(1, "#eeeeee"), padding=5)
    ])
    page.add(main_layout)
    
    def log(msg, color="black"):
        print(msg)
        log_list.controls.append(ft.Text(msg, color=color, size=12))
        try:
            page.update()
        except:
            pass 

    log(f"Python: {sys.version}")
    
    # Native Picker (Global Init)
    file_picker = None
    try:
        log("Init: FilePicker...")
        def on_dialog_result(e):
            if e.files:
                selected_path = e.files[0].path
                state["selected_file"] = selected_path
                state["current_path"] = os.path.dirname(selected_path)
                log(f"Selected: {selected_path}", "blue")
                show_main_ui()

        # Fix for kwargs error: set property after init
        file_picker = ft.FilePicker()
        file_picker.on_result = on_dialog_result
        page.overlay.append(file_picker)
        page.update()
        log("Init: FilePicker Success", "green")
    except Exception as e:
        log(f"CRITICAL: FilePicker Init Failed: {e}", "red")
        log(traceback.format_exc(), "red")

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

    # --- SETTINGS SCREEN ---
    def show_settings_ui():
        # Clear main layout controls but keep structure if possible
        main_layout.controls.clear()
        
        txt_sender = ft.TextField(label="Your Gmail", value=state["email_sender"])
        txt_pass = ft.TextField(label="App Password", value=state["email_password"], password=True, can_reveal_password=True)
        txt_kindle = ft.TextField(label="Kindle Email", value=state["email_recipient"])
        
        def save_settings(e):
            state["email_sender"] = txt_sender.value
            state["email_password"] = txt_pass.value
            state["email_recipient"] = txt_kindle.value
            show_main_ui()
            
        def cancel_settings(e):
            show_main_ui()
            
        main_layout.controls.extend([
            ft.Text("Settings", size=24, weight="bold"),
            ft.Text("Kindle / Email Configuration", size=16, weight="bold"),
            txt_sender,
            txt_pass,
            txt_kindle,
            ft.Container(height=20),
            ft.Row([
                ft.ElevatedButton("Save", on_click=save_settings, bgcolor="blue", color="white"),
                ft.TextButton("Cancel", on_click=cancel_settings)
            ]),
            ft.Divider(),
            ft.Text("Logs:", weight="bold"),
            ft.Container(content=log_list, height=100, border=ft.border.all(1, "grey"))
        ])
        page.update()

    # --- MAIN CONVERTER SCREEN ---
    def show_main_ui():
        try:
            log("Entering UI Build...")
            # SAFE LAYOUT: 
            # 1. Scrollable Content Area (Top)
            # 2. Fixed Divider
            # 3. Fixed Log Area (Bottom)
            
            main_layout.controls.clear()
            
            content_col = ft.Column(scroll="auto", expand=True)
            
            log("Building Controls...")
            path_input = ft.TextField(
                label="File Path", 
                value=state["selected_file"], 
            )
            
            # New Feature Controls
            sw_compress = ft.Switch(
                label="Compress PDF (Max 50MB)", 
                value=state["compress_enabled"],
                on_change=lambda e: state.update({"compress_enabled": e.control.value})
            )
            
            progress_bar = ft.ProgressBar(width=300, visible=False)
            status_txt = ft.Text("Ready. Browse or type path.", color="green")
            percent_txt = ft.Text("", weight="bold")
            
            def on_browse_click(e):
                show_browser_ui(state["current_path"])

            def on_settings_click(e):
                show_settings_ui()
                
            def on_native_pick_click(e):
                log("Opening Native Picker...")
                file_picker.pick_files(allow_multiple=False, allowed_extensions=["cbz"])

            def on_progress(p, msg):
                progress_bar.value = p/100
                status_txt.value = msg
                percent_txt.value = f"{int(p)}%"
                page.update()
                
            def run_convert(e):
                src = path_input.value
                if not src:
                    status_txt.value = "Enter a path first."
                    status_txt.color = "red"
                    page.update()
                    return
                
                state["selected_file"] = src 
                dst = src.replace(".cbz", ".pdf")
                
                status_txt.value = f"Starting..."
                status_txt.color = "black"
                percent_txt.value = "0%"
                progress_bar.visible = True
                page.update()
                
                import threading
                def worker():
                    try:
                        success = conversion_engine(
                            src, 
                            dst, 
                            progress_callback=on_progress,
                            compress=state["compress_enabled"],
                            max_size_mb=50
                        )
                        
                        if success is False:
                             raise Exception("Conversion returned False")

                        status_txt.value = "Conversion Complete!"
                        status_txt.color = "green"
                        page.update()
                        
                        if state["email_sender"] and state["email_recipient"]:
                            on_progress(100, "Sending to Kindle...")
                            try:
                                import email_sender
                                sent, msg = email_sender.send_email(
                                    dst, 
                                    state["email_sender"], 
                                    state["email_password"], 
                                    state["email_recipient"]
                                )
                                if sent:
                                    status_txt.value = "Done + Sent to Kindle!"
                                else:
                                    status_txt.value = f"Done, but Email Failed: {msg}"
                            except Exception as e:
                                 status_txt.value = f"Done (Email error: {e})"
                            page.update()

                    except Exception as e:
                        status_txt.value = f"Error: {e}"
                        status_txt.color = "red"
                        page.update()
                
                threading.Thread(target=worker).start()
                
            log("Adding Controls to Page...")
            
            content_col.controls.extend([
                ft.Row([
                    ft.Text("CBZ to PDF", size=24, weight="bold"),
                    ft.TextButton("[Settings]", on_click=on_settings_click) 
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Container(height=10),
                path_input,
                ft.Container(height=5),
                ft.Row([
                    ft.ElevatedButton("Browse (Android)", on_click=on_browse_click, expand=True, bgcolor="orange", color="white"),
                    ft.ElevatedButton("System Picker (iOS)", on_click=on_native_pick_click, expand=True, bgcolor="blue", color="white")
                ]),
                sw_compress,
                ft.Container(height=10),
                ft.ElevatedButton("Convert to PDF", on_click=run_convert, width=200),
                ft.Container(height=20),
                progress_bar,
                ft.Row([percent_txt, status_txt], spacing=10)
            ])
            
            # Add to Main Layout: Content (Top, Expand), Divider, Logs (Bottom, Fixed)
            main_layout.controls.append(content_col)
            main_layout.controls.append(ft.Divider())
            main_layout.controls.append(ft.Container(content=log_list, height=120, border=ft.border.all(1, "#eeeeee")))
            
            page.update()
            log("UI Build Complete!", "green")
            
        except Exception as e:
            log(f"UI ERROR: {e}", "red")
            log(traceback.format_exc(), "red")

    # --- HELPER: Detect SD Cards ---
    def get_android_drives():
        drives = set()
        drives.add("/storage/emulated/0") # Internal Default
        
        try:
            with open("/proc/mounts", "r") as f:
                for line in f:
                    parts = line.split()
                    if len(parts) > 1:
                        mount_point = parts[1]
                        # Look for storage mounts
                        if mount_point.startswith("/storage") and mount_point != "/storage":
                            # Avoid duplicates like /storage/self/primary
                            if "self" not in mount_point and "emulated" not in mount_point:
                                drives.add(mount_point)
        except Exception as e:
            print(f"Error reading mounts: {e}")
            
        return sorted(list(drives))

    # --- FULL PAGE FILE BROWSER ---
    def show_browser_ui(start_path):
        page.clean()
        
        # State Update
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
            # SPECIAL CASE: ROOT STORAGE SELECTION
            if start_path == "/storage":
                file_list.controls.append(ft.Text("Detected Storage Volumes:", weight="bold"))
                
                drives = get_android_drives()
                for drive in drives:
                     file_list.controls.append(
                        ft.ElevatedButton(f"💾 {drive}", on_click=lambda _, p=drive: navigate(p), width=300, bgcolor="orange", color="white")
                    )
            else:
                # Normal Directory Listing
                parent = os.path.dirname(start_path)
                
                # Navigation Helpers
                file_list.controls.append(
                    ft.Row([
                        ft.ElevatedButton(".. (UP)", on_click=lambda _: navigate(parent), expand=True, bgcolor="grey", color="white"),
                        ft.ElevatedButton("Switch Drive", on_click=lambda _: navigate("/storage"), expand=True, bgcolor="orange", color="white"),
                    ])
                )
                
                items = sorted(os.listdir(start_path))
                for item in items:
                    full_path = os.path.join(start_path, item)
                    is_dir = os.path.isdir(full_path)
                    
                    if is_dir:
                        file_list.controls.append(
                            ft.OutlinedButton(f"📂 {item}", on_click=lambda _, p=full_path: navigate(p), width=300)
                        )
                    else:
                        # IT IS A FILE - Show all of them
                        if item.lower().endswith('.cbz'):
                            # Valid CBZ
                            file_list.controls.append(
                                ft.ElevatedButton(f"📄 {item}", on_click=lambda _, p=full_path: select(p), width=300, bgcolor="blue", color="white")
                            )
                        else:
                            # Other File (Debug visibility)
                            file_list.controls.append(
                                ft.ElevatedButton(f"⬜ {item}", on_click=lambda _, p=full_path: select(p), width=300, bgcolor="grey", color="white")
                            )
                        
        except Exception as e:
            file_list.controls.append(ft.Text(f"Access Error: {e}", color="red"))
            # Fallback to drive list if we hit a wall
            file_list.controls.append(ft.ElevatedButton("Go to Detected Drives", on_click=lambda _: navigate("/storage"), bgcolor="orange", color="white"))

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
