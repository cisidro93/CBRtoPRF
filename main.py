import flet as ft
import sys
import traceback

def main(page: ft.Page):
    page.title = "CBZ to PDF"
    page.scroll = "auto"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window.width = 400
    page.padding = 20
    
    # Tiny helper to show initialization progress
    init_log = ft.Column()
    page.add(init_log)
    
    def log(msg):
        init_log.controls.append(ft.Text(msg, size=12, color="grey"))
        page.update()

    log("Engine started. Initializing UI...")

    try:
        import os
        import threading
        import traceback
        
        log("Imports base complete. Loading converter module...")
        try:
            from cbz_to_pdf import convert_cbz_to_pdf
            log("Converter module loaded.")
        except Exception as e:
            log(f"CRITICAL: Converter module failed: {e}")
            page.add(ft.Text(f"Full Error:\n{traceback.format_exc()}", color="red"))
            return

        # State
        selected_file_path = ft.Ref[str]()
        
        # UI Components
        status_text = ft.Text("Ready", size=16, weight="bold")
        progress_bar = ft.ProgressBar(width=300, value=0, visible=False)
        selected_file_text = ft.Text("No file selected", italic=True)
        
        def update_progress(percentage, message):
            progress_bar.value = percentage / 100
            status_text.value = message
            page.update()

        def run_conversion_thread(src, dst, compress):
            try:
                success = convert_cbz_to_pdf(
                    src, dst, 
                    progress_callback=update_progress,
                    compress=compress
                )
                
                def finish_ui():
                    progress_bar.visible = False
                    status_text.value = "Done: " + os.path.basename(dst)
                    status_text.color = "green"
                    btn_convert.disabled = False
                    btn_pick.disabled = False
                    page.update()
                    
                finish_ui()
                
            except Exception as e:
                print(e)
                def fail_ui():
                    progress_bar.visible = False
                    status_text.value = f"Error: {e}"
                    status_text.color = "red"
                    btn_convert.disabled = False
                    btn_pick.disabled = False
                    page.update()
                fail_ui()

        def on_convert_click(e):
            if not selected_file_path.current:
                status_text.value = "Please select a file first"
                status_text.color = "red"
                page.update()
                return

            src = selected_file_path.current
            dst = os.path.splitext(src)[0] + ".pdf"

            btn_convert.disabled = True
            btn_pick.disabled = True
            progress_bar.visible = True
            status_text.value = "Starting..."
            status_text.color = "black"
            page.update()

            t = threading.Thread(target=run_conversion_thread, args=(src, dst, chk_compress.value))
            t.start()
        
        def on_file_picked(e: ft.FilePickerResultEvent):
            if e.files and len(e.files) > 0:
                file_path = e.files[0].path
                selected_file_path.current = file_path
                selected_file_text.value = os.path.basename(file_path)
                selected_file_text.color = "black"
                status_text.value = "Ready to convert"
                page.update()

        log("Setting up FilePicker...")
        file_picker = ft.FilePicker(on_result=on_file_picked)
        page.overlay.append(file_picker)

        btn_pick = ft.ElevatedButton(
            "Select CBZ", 
            icon=ft.icons.FOLDER_OPEN,
            on_click=lambda _: file_picker.pick_files(allow_multiple=False, allowed_extensions=["cbz"])
        )

        chk_compress = ft.Checkbox(label="Compress Images", value=False)

        btn_convert = ft.ElevatedButton(
            "Convert to PDF",
            icon=ft.icons.PICTURE_AS_PDF,
            on_click=on_convert_click
        )
        
        log("Building main layout...")
        # Clear init log to make it clean, or keep it? Let's remove it.
        page.controls.remove(init_log)
        
        page.add(
            ft.Column(
                [
                    ft.Text("CBZ to PDF", size=24, weight="bold"),
                    ft.Divider(),
                    btn_pick,
                    selected_file_text,
                    ft.Container(height=10),
                    chk_compress,
                    ft.Container(height=10),
                    btn_convert,
                    ft.Divider(),
                    status_text,
                    progress_bar,
                ],
                alignment=ft.MainAxisAlignment.START
            )
        )
        page.update()
        
    except Exception as e:
        page.add(ft.Text(f"Startup Crash: {e}\n{traceback.format_exc()}", color="red"))
        page.update()

if __name__ == "__main__":
    ft.app(target=main)
