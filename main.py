import tkinter as tk
from tkinter import ttk
from User_interface_file.ui_plot_area import create_ui



if __name__ == "__main__":

    root = tk.Tk()

    style = ttk.Style(root)
    root.tk.call("source", "forest-light.tcl")
    root.tk.call("source", "forest-dark.tcl") 
    style.theme_use("forest-light")
    root.title("Specifications")
    root.geometry("1370x911")  # Set the initial window size
    root.resizable(False, False) # Disable window resizing
    root.configure(bg="White")  # Set the background color
    create_ui(root)
    root.mainloop()