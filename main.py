import flet as ft
import time

def main(page):
    page.title = "Progressive Boot"
    page.scroll = "auto"
    page.padding = 30
    
    # 1. Immediate Render - Prove we can draw text
    status = ft.Text("STEP 1: App Started\n(If you see this, Flet is alive)", size=20, color="green")
    page.add(status)
    page.update()
    
    # 2. Wait a beat, then try to add the dangerous element
    time.sleep(1.0)
    
    try:
        def on_result(e):
            status.value = f"Selected: {e.files[0].path}" if e.files else "Cancelled"
            page.update()
            
        picker = ft.FilePicker(on_result=on_result)
        page.overlay.append(picker)
        page.update() # Force update after overlay add
        
        page.add(ft.Text("STEP 2: FilePicker Added to Overlay", color="blue"))
        page.update()
        
        def pick_click(e):
            try:
                picker.pick_files(allow_multiple=False, allowed_extensions=["cbz"])
            except Exception as ex:
                status.value = f"Error: {ex}"
                status.color = "red"
                page.update()

        btn = ft.ElevatedButton("TEST PICKER", on_click=pick_click)
        page.add(btn)
        page.update()
        
    except Exception as e:
        page.add(ft.Text(f"CRASH DURING PICKER INIT: {e}", color="red", size=20))
        page.update()

if __name__ == "__main__":
    ft.app(target=main)
