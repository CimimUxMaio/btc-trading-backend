import tkinter as tk
from tkinter.constants import *

class NotNumericValueException(Exception):
    def __init__(self, name):
        super().__init__(f"{name} entry must contain a valid numeric value.")


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

    range_scale = tk.Scale(master=input_frame, length=200, from_=0.0, to=100.0, orient=HORIZONTAL, resolution=0.5)
    range_scale.pack()


    levels_label = tk.Label(master=input_frame, text="Number of levels at each side", font=font)
    levels_label.pack()

    levels_entry = tk.Entry(master=input_frame)
    levels_entry.pack()

    display_graphs = tk.BooleanVar()
    display_graphs_check = tk.Checkbutton(master=input_frame, variable=display_graphs, text="Display graphs?")
    display_graphs_check.pack()

    args = []
    def button_command():
        inversion = inversion_entry.get()
        levels = levels_entry.get()
        try:
            check_if_number("Inversion", inversion)
            check_if_number("Levels", levels)
            args.append(inversion)
            args.append(str(range_scale.get()))
            args.append(levels)
            args.append(str(display_graphs.get()))
            window.destroy()
        except NotNumericValueException as e:
            error_message_window(str(e))


    input_frame.grid(row=0, column=0, padx=10, pady=10)

    confirm_button = tk.Button(text="Confirm", command=button_command)
    confirm_button.grid(row=0, column=1, padx=10, pady=10, sticky="ns")

    window.mainloop()

    return args


def check_if_number(name, entry):
    if not is_number(entry):
        raise NotNumericValueException(name)


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