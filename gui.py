import tkinter as tk
from tkinter.constants import *

def get_settings():
    window = tk.Tk()

    font = "Arial 15"

    inversion_frame = tk.Frame(window)
    inversion_label = tk.Label(master=inversion_frame, text="Inversion (USDT)", font=font)
    inversion_label.pack()

    inversion_entry = tk.Entry(master=inversion_frame)
    inversion_entry.pack()

    inversion_frame.grid(row=0, column=0)

    range_frame = tk.Frame(window)
    range_label = tk.Label(master=range_frame, text="Range (%)", font=font)
    range_label.pack()

    range_scale = tk.Scale(master=range_frame, length=200, from_=0.0, to=100.0, orient=HORIZONTAL, resolution=0.05)
    range_scale.pack()

    range_frame.grid(row=1, column=0)


    levels_frame = tk.Frame(window)
    levels_label = tk.Label(master=levels_frame, text="Number of levels at each side", font=font)
    levels_label.pack()

    levels_scale = tk.Scale(master=levels_frame, length=200, from_=1, to=1000, orient=HORIZONTAL)
    levels_scale.pack()

    levels_frame.grid(row=2, column=0)


    args = []
    def button_command():
        inversion = inversion_entry.get()
        if(not is_number(inversion)):
            error_message_window("Inversion entry mus contain a valid numeric value.")
        else:
            args.append(inversion_entry.get())
            args.append(str(range_scale.get()))
            args.append(str(levels_scale.get()))
            window.destroy()

    confirm_button = tk.Button(text="Confirm", command=button_command)
    confirm_button.grid(row=1, column=3)

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
