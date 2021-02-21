import tkinter as tk
from tkinter.constants import *

def get_settings():
    window = tk.Tk()
    window.title("Grid trading settings")
    window.resizable(0, 0)

    font = "Arial 15"

    input_frame = tk.Frame(master=window)

    inversion_label = tk.Label(master=input_frame, text="Inversion (USDT)", font=font)
    inversion_label.pack()

    inversion_entry = tk.Entry(master=input_frame)
    inversion_entry.pack()


    range_label = tk.Label(master=input_frame, text="Range (%)", font=font)
    range_label.pack()

    range_scale = tk.Scale(master=input_frame, length=200, from_=1.0, to=100.0, orient=HORIZONTAL, resolution=0.05)
    range_scale.pack()


    levels_label = tk.Label(master=input_frame, text="Number of levels at each side", font=font)
    levels_label.pack()

    levels_scale = tk.Scale(master=input_frame, length=200, from_=1, to=1000, orient=HORIZONTAL)
    levels_scale.pack()

    args = []
    def button_command():
        inversion = inversion_entry.get()
        if(not is_number(inversion)):
            error_message_window("Inversion entry must contain a valid numeric value.")
        else:
            args.append(inversion_entry.get())
            args.append(str(range_scale.get()))
            args.append(str(levels_scale.get()))
            window.destroy()

    input_frame.grid(row=0, column=0, padx=10, pady=10)

    confirm_button = tk.Button(text="Confirm", command=button_command)
    confirm_button.grid(row=0, column=1, padx=10, pady=10, sticky="ns")

    window.mainloop()

    return args


def error_message_window(msg):
    window = tk.Tk()
    label = tk.Label(master=window, text=msg)
    label.pack()
    button = tk.Button(master=window, text="Ok", command=lambda: window.destroy())
    button.pack()

    window.mainloop()


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
