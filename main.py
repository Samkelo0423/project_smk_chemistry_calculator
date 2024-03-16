import tkinter as tk
from User_interface_file.ui_plot_area import create_ui



if __name__ == "__main__":

    root = tk.Tk()
    root.title("Specifications")
    root.geometry("1422x900")  # Set the initial window size
    root.resizable(False, False) # Disable window resizing
    root.configure(bg="light gray")  # Set the background color

    create_ui(root)

    root.mainloop()
