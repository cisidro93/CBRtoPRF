import flet as ft
import sys
import traceback

def main(page: ft.Page):
    page.title = "Debug Mode"
    page.scroll = "auto"
    
    page.add(ft.Text("Application Started!", size=30, weight="bold", color="green"))
    page.add(ft.Text("If you see this, the core Flet engine is working.", size=20))
    
    # Print system info
    page.add(ft.Text(f"Python Info: {sys.version}", size=12))
    
    try:
        import PIL
        page.add(ft.Text(f"Pillow imported: {PIL.__version__}", color="blue"))
    except ImportError:
        page.add(ft.Text("Pillow import failed", color="red"))
        
    try:
        from cbz_to_pdf import convert_cbz_to_pdf
        page.add(ft.Text("Core module imported successfully", color="blue"))
    except Exception as e:
        page.add(ft.Text(f"Core module import failed: {e}\n{traceback.format_exc()}", color="red"))

    page.update()

if __name__ == "__main__":
    ft.app(target=main)
