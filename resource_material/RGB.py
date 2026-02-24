import tkinter as tk
import math

# Approx color database (can expand to 1000 later)
COLOR_DB = {
    "Red": (255, 0, 0),
    "Green": (0, 255, 0),
    "Blue": (0, 0, 255),
    "Yellow": (255, 255, 0),
    "Cyan": (0, 255, 255),
    "Magenta": (255, 0, 255),
    "Orange": (255, 165, 0),
    "Purple": (128, 0, 128),
    "Pink": (255, 192, 203),
    "Brown": (165, 42, 42),
    "White": (255, 255, 255),
    "Black": (0, 0, 0),
    "Gray": (128, 128, 128),
    "Sky Blue": (135, 206, 235),
    "Lime": (50, 205, 50),
    "Gold": (255, 215, 0),
    "Navy": (0, 0, 128),
    "Olive": (128, 128, 0),
    "Teal": (0, 128, 128),
    "Maroon": (128, 0, 0),
}

def closest_color(r, g, b):
    min_dist = float("inf")
    closest_name = "Unknown"

    for name, (cr, cg, cb) in COLOR_DB.items():
        dist = math.sqrt((r-cr)**2 + (g-cg)**2 + (b-cb)**2)
        if dist < min_dist:
            min_dist = dist
            closest_name = name

    return closest_name

def update_color(event=None):
    r, g, b = red.get(), green.get(), blue.get()
    color = f"#{r:02x}{g:02x}{b:02x}"

    preview.config(bg=color)
    name = closest_color(r, g, b)

    label.config(text=f"RGB: ({r},{g},{b})  HEX: {color}\nClosest Name: {name}")

root = tk.Tk()
root.title("RGB Color Name Picker")
root.geometry("400x350")

red = tk.IntVar()
green = tk.IntVar()
blue = tk.IntVar()

tk.Label(root, text="Red").pack()
tk.Scale(root, from_=0, to=255, orient="horizontal",
         variable=red, command=update_color).pack(fill="x")

tk.Label(root, text="Green").pack()
tk.Scale(root, from_=0, to=255, orient="horizontal",
         variable=green, command=update_color).pack(fill="x")

tk.Label(root, text="Blue").pack()
tk.Scale(root, from_=0, to=255, orient="horizontal",
         variable=blue, command=update_color).pack(fill="x")

preview = tk.Label(root, bg="black", width=40, height=5)
preview.pack(pady=10)

label = tk.Label(root, text="")
label.pack()

update_color()
root.mainloop()
