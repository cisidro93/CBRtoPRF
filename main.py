import flet as ft
import os
import threading
import time

# MOCK LOGIC for UI Testing
def mock_convert(src, dst, progress_callback):
    for i in range(11):
        if progress_callback:
            progress_callback(i * 10, f"Simulating conversion {i*10}%...")
        time.sleep(0.5)
    return True

def main(page: ft.Page):
    page.title = "UI Test Mode"
    page.scroll = "auto"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window.width = 400
    page.padding = 20
    
    page.add(ft.Text("UI Test Build", size=20, weight="bold", color="blue"))
    page.add(ft.Text("If you see this, the UI is safe. Try the buttons.", size=14))

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

    def run_conversion_thread(src, dst):
        try:
            # CALLING MOCK
            success = mock_convert(src, dst, update_progress)
            
            def finish_ui():
                progress_bar.visible = False
                status_text.value = "Done (Simulated)"
                status_text.color = "green"
                btn_convert.disabled = False
                btn_pick.disabled = False
                page.update()
                
            finish_ui()
            
        except Exception as e:
            print(e)
            
    def on_convert_click(e):
        if not selected_file_path.current:
            status_text.value = "Please select a file first"
            status_text.color = "red"
            page.update()
            return

        btn_convert.disabled = True
        btn_pick.disabled = True
        progress_bar.visible = True
        status_text.value = "Starting..."
        status_text.color = "black"
        page.update()

        t = threading.Thread(target=run_conversion_thread, args=("mock_src", "mock_dst"))
        t.start()
    
    def on_file_picked(e: ft.FilePickerResultEvent):
        if e.files and len(e.files) > 0:
            file_path = e.files[0].path
            selected_file_path.current = file_path
            selected_file_text.value = os.path.basename(file_path)
            selected_file_text.color = "black"
            status_text.value = "File Selected"
            page.update()

    file_picker = ft.FilePicker(on_result=on_file_picked)
    page.overlay.append(file_picker)

    btn_pick = ft.ElevatedButton(
        "Select CBZ (Test)", 
        icon=ft.icons.FOLDER_OPEN,
        on_click=lambda _: file_picker.pick_files(allow_multiple=False, allowed_extensions=["cbz"])
    )

    btn_convert = ft.ElevatedButton(
        "Convert to PDF (Test)",
        icon=ft.icons.PICTURE_AS_PDF,
        on_click=on_convert_click
    )
    
    page.add(
        ft.Column(
            [
                ft.Divider(),
                btn_pick,
                selected_file_text,
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

if __name__ == "__main__":
    ft.app(target=main)
