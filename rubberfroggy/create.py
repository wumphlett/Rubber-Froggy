import sys
import tkinter as tk
from tkinter import Toplevel

from PIL import Image
from pystray import Icon, MenuItem
from screeninfo import get_monitors

from rubberfroggy.animate import Animator, Canvas, State
from rubberfroggy.pet import Pet
from rubberfroggy.util import BASE_PATH, OFFSET, X_RES, Y_RES


STATIC_PATH = BASE_PATH / "static"


def show_in_taskbar(root):
    root.wm_withdraw()
    root.after(10, lambda: root.wm_deiconify())


def hide_window(window):
    def exit_action(icon):
        icon.stop()
        window.destroy()

    def show():
        window.deiconify()
        window.mainloop()

    window.withdraw()
    icon = Icon("DesktopPet")
    icon.menu = (MenuItem("Exit", lambda: exit_action(icon)), MenuItem("Show", show))
    icon.icon = Image.open(STATIC_PATH / "icon.ico")
    icon.title = "RubberFroggy"
    icon.run()


def create_pet() -> Pet:
    monitor = get_monitors()[0]
    resolution = (X_RES, Y_RES)
    x, y = monitor.width, monitor.height - OFFSET
    window = tk.Tk()

    if sys.platform == "darwin":
        toplevel = Toplevel(window)
        toplevel.overrideredirect(True)
        toplevel.wm_attributes("-topmost", True)
        toplevel.update()
        toplevel.lift()
        toplevel.attributes("-alpha", 1)
        toplevel.attributes("-topmost", 1)
        toplevel.wm_attributes("-transparent", True)
        toplevel.config(bg="systemTransparent")
        window.attributes("-alpha", 0)
        label = tk.Label(toplevel)
    else:
        window.overrideredirect(True)
        window.wm_attributes("-topmost", True)
        background_color = "#FFFFFF"
        window.config(highlightbackground=background_color)
        label = tk.Label(window, bd=0, bg=background_color, height=resolution[0], width=resolution[1])
        window.wm_attributes("-transparentcolor", background_color)
        window.update()

    window.update_idletasks()
    label.pack()

    window.winfo_toplevel().title("RubberFroggy")
    window.iconbitmap(STATIC_PATH / "icon.ico")

    window.overrideredirect(True)
    window.after(10, lambda: show_in_taskbar(window))
    canvas = Canvas(window, label, width=x, height=y)

    window.protocol("WM_DELETE_WINDOW", lambda: hide_window(window))

    animations = Animator.get_animations(resolution)
    animator = Animator(state=State.IDLE, number=0, animations=animations)

    pet = Pet(canvas.width // 2, canvas.height, canvas, animator)
    label.bind("<ButtonPress-1>", pet.start_hold)
    label.bind("<B1-Motion>", pet.while_hold)
    label.bind("<ButtonRelease-1>", pet.stop_hold)
    label.bind("<Enter>", pet.start_hover)
    label.bind("<Leave>", pet.stop_hover)

    window.after(1, pet.tick)
    window.mainloop()
    return pet
