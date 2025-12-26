import flet as ft

def main(page):
    page.title = "Sanity Check"
    page.scroll = "auto"
    page.padding = 50
    
    status = ft.Text("Waiting...", size=20)
    
    def on_result(e):
        if e.files:
            status.value = f"Selected: {e.files[0].path}"
        else:
            status.value = "Cancelled"
        page.update()
        
    # Minimal Setup
    picker = ft.FilePicker(on_result=on_result)
    page.overlay.append(picker)
    page.update()
    
    def pick_click(e):
        try:
            picker.pick_files(allow_multiple=False, allowed_extensions=["cbz"])
        except Exception as ex:
            status.value = f"Error: {ex}"
            status.color = "red"
            page.update()

    btn = ft.ElevatedButton("TEST FILE PICKER", on_click=pick_click, height=50)
    
    page.add(
        ft.Text("FilePicker Sanity Check", size=24, weight="bold"),
        ft.Divider(),
        btn,
        ft.Divider(),
        status
    )
    page.update()

if __name__ == "__main__":
    ft.app(target=main)
