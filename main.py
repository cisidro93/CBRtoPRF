import flet as ft
import os
import threading
from cbz_to_pdf import convert_cbz_to_pdf

def main(page: ft.Page):
    page.title = "CBZ to PDF Converter"
    page.theme_mode = ft.ThemeMode.LIGHT # Good for Eink
    page.window.width = 400
    page.window.height = 700
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.padding = 20

    # State
    selected_file_path = ft.Ref[str]()
    processing = ft.Ref[bool]()
    
    # UI Components
    status_text = ft.Text("Ready", size=16)
    progress_bar = ft.ProgressBar(width=300, value=0, visible=False)
    
    selected_file_text = ft.Text("No file selected", color=ft.colors.GREY_700, size=12, italic=True)

    def update_progress(percentage, message):
        progress_bar.value = percentage / 100
        status_text.value = message
        page.update()

    def result_handler(success, message):
        progress_bar.visible = False
        status_text.value = "Done" if success else "Error"
        color = ft.colors.GREEN if success else ft.colors.RED
        status_text.color = color
        
        # Show snackbar
        page.show_snack_bar(ft.SnackBar(content=ft.Text(message)))
        
        # Reset UI partial
        btn_convert.disabled = False
        btn_pick.disabled = False
        page.update()

    def run_conversion_thread(src, dst, compress):
        try:
            success = convert_cbz_to_pdf(
                src, dst, 
                progress_callback=update_progress,
                compress=compress
            )
            result_handler(success, f"Saved to {os.path.basename(dst)}")
        except Exception as e:
            result_handler(False, str(e))

    def on_convert_click(e):
        if not selected_file_path.current:
            page.show_snack_bar(ft.SnackBar(content=ft.Text("Please select a CBZ file first.")))
            return
            
        src = selected_file_path.current
        # Simple output: same folder, same name .pdf
        # On Android, we might need to be careful with paths. 
        # But for now, let's try same directory or Downloads.
        # Actually on Android strict file permissions apply.
        # For this MVP, we rely on the fact that Flet's file picker returns a path we can read.
        # Writing might need a specific directory (like get_external_storage).
        # We will try writing to the same dir and see.
        dst = os.path.splitext(src)[0] + ".pdf"

        btn_convert.disabled = True
        btn_pick.disabled = True
        progress_bar.visible = True
        status_text.color = ft.colors.BLACK
        page.update()

        compress = chk_compress.value
        
        # Thread
        t = threading.Thread(target=run_conversion_thread, args=(src, dst, compress))
        t.start()

    def on_file_picked(e: ft.FilePickerResultEvent):
        if e.files and len(e.files) > 0:
            file_path = e.files[0].path
            selected_file_path.current = file_path
            selected_file_text.value = os.path.basename(file_path)
            # Reset status
            status_text.value = "Ready to convert"
            status_text.color = ft.colors.BLACK
            page.update()

    file_picker = ft.FilePicker(on_result=on_file_picked)
    page.overlay.append(file_picker)

    btn_pick = ft.ElevatedButton(
        "Select CBZ File", 
        icon=ft.icons.FOLDER_OPEN, 
        on_click=lambda _: file_picker.pick_files(allow_multiple=False, allowed_extensions=["cbz"])
    )
    
    chk_compress = ft.Checkbox(label="Compress Images (Simpe)", value=False)
    
    btn_convert = ft.ElevatedButton(
        "Convert to PDF", 
        icon=ft.icons.PICTURE_AS_PDF, 
        on_click=on_convert_click
    )

    page.add(
        ft.Column(
            [
                ft.Container(height=20),
                ft.Icon(ft.icons.BOOK, size=64, color=ft.colors.BLUE),
                ft.Text("CBZ Converter", size=24, weight=ft.FontWeight.BOLD),
                ft.Container(height=20),
                btn_pick,
                selected_file_text,
                ft.Container(height=10),
                chk_compress,
                ft.Container(height=10),
                btn_convert,
                ft.Container(height=20),
                progress_bar,
                status_text,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
        )
    )

if __name__ == "__main__":
    ft.app(target=main)
