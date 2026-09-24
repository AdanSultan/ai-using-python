import tkinter as tk

window = tk.Tk()
window.title("Wikipedia Table Viewer")
window.geometry("300x200")

def on_click():
    label.config(text="Button Clicked!")

label = tk.Label(window, text="Click the button to see the message.")
label.pack(pady=10)

entry = tk.Entry(window)
entry.pack(pady=10)

button = tk.Button(window, text="Click Me", command=on_click)
button.pack(pady=10)

window.mainloop()
