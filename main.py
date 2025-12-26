import flet as ft
import os
import threading
import time
import traceback
import sys

# Global reference to the converter logic, loaded lazily
converter_func = None

def main(page):
    page.title = "CBZ to PDF"
    page.scroll = "auto"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window.width = 400
    page.padding = 20

    # SECTION: BOOT LOADER UI
    boot_log = ft.Column()
    boot_status = ft.Text("Initializing...", size=16, weight="bold")
    page.add(ft.Container(height=20), boot_status, ft.Divider(), boot_log)

    def log(msg, color="grey"):
        print(msg)
        boot_log.controls.append(ft.Text(msg, size=12, color=color))
        page.update()

    def load_backend():
        global converter_func
        try:
            log("Loading conversion engine...")
            time.sleep(0.5) # Give UI time to breathe
            
            # Intentional lazy import
            from cbz_to_pdf import convert_cbz_to_pdf
            converter_func = convert_cbz_to_pdf
            
            log("Engine loaded successfully.", "green")
            time.sleep(0.5)
            
            # Switch to Main UI
            page.clean()
            init_main_ui()
            
        except Exception as e:
            log(f"CRITICAL ERROR: {e}", "red")
            boot_log.controls.append(ft.Text(traceback.format_exc(), color="red", size=10))
            page.update()

    # SECTION: MAIN UI
    def init_main_ui():
        selected_file_path = ft.Ref[str]()
        
        status_text = ft.Text("Ready", size=16, weight="bold")
        progress_bar = ft.ProgressBar(width=300, value=0, visible=False)
        selected_file_text = ft.Text("No file selected", italic=True)

        def update_progress(percentage, message):
            progress_bar.value = percentage / 100
            status_text.value = message
            page.update()

        def run_conversion_thread(src, dst, compress):
            try:
                if not converter_func:
                    raise Exception("Converter engine not loaded.")

                success = converter_func(
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

    # Start separate thread for loading to avoid blocking UI frame 1
    t = threading.Timer(0.1, load_backend)
    t.start()

if __name__ == "__main__":
    ft.app(target=main)
