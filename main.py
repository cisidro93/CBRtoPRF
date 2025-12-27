import flet as ft
import sys
import os
import traceback
import time

# Global var for the engine
conversion_engine = None

def main(page):
    page.title = "CBZ Converter (No Picker)"
    page.scroll = "auto" 
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20
    
    # 1. Boot Message
    page.add(ft.Text("System Boot: Build #56 (Plist Debug)", color="blue", size=16, weight="bold"))
    
    # Global State
    # FIXED: Use expanduser("~") for iOS compatibility (sandbox root)
    default_path = os.path.expanduser("~")
    # Fallback for Android if needed (though ~ usually works)
    if os.path.exists("/storage/emulated/0/Download"):
        default_path = "/storage/emulated/0/Download"
    
    state = {
        "current_path": default_path,
        "selected_file": "Select a file...",
        "compress_enabled": False,
        "email_sender": "",
        "email_password": "",
        "email_recipient": ""
    }

    def log(msg, color="black"):
        print(msg)
        page.add(ft.Text(msg, color=color, size=12))
        try:
            page.update()
        except:
            pass 

    # --- INIT: FORCE STORAGE CREATION ---
    def init_storage():
        try:
           docs = os.path.join(os.path.expanduser("~"), "Documents")
           if not os.path.exists(docs):
               os.makedirs(docs)
           
           readme = os.path.join(docs, "README.txt")
           with open(readme, "w") as f:
               f.write("Welcome to CBZ Converter!\n\nPlace your .cbz files in this folder to see them in the app.\n")
               
           log(f"Storage Init: Wrote {readme}")
           
        except Exception as e:
            log(f"Storage Error: {e}", "red")

    init_storage()

    log(f"Python: {sys.version}")
    log(f"Home Dir: {os.path.expanduser('~')}")
    log(f"CWD: {os.getcwd()}")
    
    # --- EXORCISM: NO FILE PICKER ---
    log("Debug: FilePicker is DISABLED.")
    file_picker = None 
    
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
        page.clean()
        
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
            
        page.add(
            ft.Text("Settings", size=24, weight="bold"),
            ft.Text("Kindle / Email Configuration", size=16, weight="bold"),
            txt_sender,
            txt_pass,
            txt_kindle,
            ft.Container(height=20),
            ft.Row([
                ft.ElevatedButton("Save", on_click=save_settings, bgcolor="blue", color="white"),
                ft.TextButton("Cancel", on_click=cancel_settings)
            ])
        )
        page.update()

    # --- MAIN CONVERTER SCREEN ---
    def show_main_ui():
        try:
            log("Entering UI Build...")
            page.clean()
            
            log("Building Controls...")
            path_input = ft.TextField(
                label="File Path", 
                value=state["selected_file"]
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
                log("NATIVE PICKER IS DISABLED IN THIS BUILD", "red")

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
            
            page.add(
                ft.Row([
                    ft.Text("CBZ to PDF", size=24, weight="bold"),
                    ft.TextButton("[Settings]", on_click=on_settings_click) 
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Container(height=10),
                path_input,
                ft.Container(height=5),
                ft.Row([
                    ft.ElevatedButton("Browse Files", on_click=on_browse_click, expand=True, bgcolor="orange", color="white"),
                    # ft.ElevatedButton("System Picker (Disabled)", on_click=on_native_pick_click, expand=True, bgcolor="grey", color="white")
                ]),
                sw_compress,
                ft.Container(height=10),
                ft.ElevatedButton("Convert to PDF", on_click=run_convert, width=200),
                ft.Container(height=20),
                progress_bar,
                ft.Row([percent_txt, status_txt], spacing=10),
                ft.Divider(),
                ft.Text("Logs (No Overlay)", weight="bold")
            )
            
            page.update()
            log("UI Build Complete!", "green")
            
        except Exception as e:
            log(f"UI ERROR: {e}", "red")
            log(traceback.format_exc(), "red")

    # --- HELPER: Detect SD Cards (or iOS Home) ---
    def get_valid_drives():
        drives = set()
        
        # 1. Add Home Directory (Universal)
        home = os.path.expanduser("~")
        drives.add(home)
        
        # 2. Add CWD (Universal)
        drives.add(os.getcwd())
        
        # 3. Android Specifics
        if os.path.exists("/proc/mounts"):
            try:
                with open("/proc/mounts", "r") as f:
                    for line in f:
                        parts = line.split()
                        if len(parts) > 1:
                            mount_point = parts[1]
                            if mount_point.startswith("/storage") and mount_point != "/storage":
                                if "self" not in mount_point and "emulated" not in mount_point:
                                    drives.add(mount_point)
                # Ensure primary android storage is there
                if os.path.exists("/storage/emulated/0"):
                    drives.add("/storage/emulated/0")
            except:
                pass
            
        return sorted(list(drives))
    
    # --- FULL PAGE FILE BROWSER ---
    def show_browser_ui(start_path):
        page.clean()
        
        # Validate path
        if not os.path.exists(start_path):
            log(f"Path not found: {start_path}, resetting to Home.", "red")
            start_path = os.path.expanduser("~")
            
        # State Update
        state["current_path"] = start_path
        
        file_list = ft.Column() # No expand, just simple column
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
            # SPECIAL CASE: ROOT SELECTION
            if start_path == "ROOT_SELECTION":
                file_list.controls.append(ft.Text("Select Storage Root:", weight="bold"))
                
                drives = get_valid_drives()
                for drive in drives:
                     file_list.controls.append(
                        ft.ElevatedButton(f"💾 {drive}", on_click=lambda _, p=drive: navigate(p), width=300, bgcolor="orange", color="white")
                    )
                     
                # Add Documents specifically for iOS if easily guessable?
                docs = os.path.join(os.path.expanduser("~"), "Documents")
                if os.path.exists(docs):
                     file_list.controls.append(
                        ft.ElevatedButton(f"📂 Documents", on_click=lambda _, p=docs: navigate(p), width=300, bgcolor="blue", color="white")
                    )
            else:
                # Normal Directory Listing
                parent = os.path.dirname(start_path)
                
                # Navigation Helpers
                file_list.controls.append(
                    ft.Row([
                        ft.ElevatedButton(".. (UP)", on_click=lambda _: navigate(parent), expand=True, bgcolor="grey", color="white"),
                        ft.ElevatedButton("Switch Drive", on_click=lambda _: navigate("ROOT_SELECTION"), expand=True, bgcolor="orange", color="white"),
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
                        if item.lower().endswith('.cbz'):
                            file_list.controls.append(
                                ft.ElevatedButton(f"📄 {item}", on_click=lambda _, p=full_path: select(p), width=300, bgcolor="blue", color="white")
                            )
                        else:
                            file_list.controls.append(
                                ft.ElevatedButton(f"⬜ {item}", on_click=lambda _, p=full_path: select(p), width=300, bgcolor="grey", color="white")
                            )
                        
        except Exception as e:
            file_list.controls.append(ft.Text(f"Access Error: {e}", color="red"))
            file_list.controls.append(ft.ElevatedButton("Go Home", on_click=lambda _: navigate(os.path.expanduser("~")), bgcolor="orange", color="white"))

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
