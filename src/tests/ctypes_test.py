import flet as ft
import ctypes, threading

def trigger_fake_error():
    """Spawns a native Windows error dialog."""
    # The message and title
    text = "CRITICAL SYSTEM EXCEPTION: Memory corrupted at 0x000000slack.\n\nImmediate attention required."
    title = "Fatal Error"
    
    # Flags: 0x10 is the red 'Error' (X) icon, 0x0 is the 'OK' button only, 
    # 0x1000 sets it to System Modal (forces it on top of everything)
    style = 0x10 | 0x0 | 0x1000 
    
    # Run it in a background thread so it doesn't freeze Flet!
    threading.Thread(
        target=lambda: ctypes.windll.user32.MessageBoxW(0, text, title, style),
        daemon=True
    ).start()

async def test(page: ft.Page):
    page.title = "Error Popup Test"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    await page.window.center()
    
    async def trigger_popup(e: ft.Event[ft.Button]):
        if isinstance(e.page, ft.Page):
            e.page.run_thread(trigger_fake_error)
    
    page.add(ft.Button("Click for popup!", on_click=trigger_popup))

if __name__ == "__main__":
    ft.run(test)