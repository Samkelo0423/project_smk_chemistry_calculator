import tkinter as tk
from tkinter import ttk, font
import pandas as pd
from pandastable import Table
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from calculation_file_module.calculation_plot_file import plot_ellingham_diagram


class CustomTable(Table):
    def _configureStyle(self):
        """Override _configureStyle to set row colors."""
        Table._configureStyle(self)
        style = ttk.Style()
        style.configure("Custom.Treeview", font=("Helvetica", 10))  # Change cell font
        for i in range(0, len(self.rows), 2):
            self.tag_configure(self.rows[i], background="lightgray")


def create_ui(root):

    def calculate():
        reaction_equations = (
            reaction_entry.get("1.0", tk.END).strip().split(",")
        )  # Split by commas
        temperature_from = float(from_temp_entry.get())
        temperature_to = float(to_temp_entry.get())
        temperature_step = int(step_temp_entry.get())

        file_path = (
            "Thermodata.xlsx"  # Update with your file path for delta G calculation
        )
        s = plot_ellingham_diagram(
            file_path,
            reaction_equations,
            temperature_from,
            temperature_to,
            temperature_step,
            canvas,
        )
        # Load data from source
        output_excel = "data_from_calculation.xlsx"
        s.to_excel(output_excel, index=False)
        df = pd.read_excel(output_excel)
        # Create the table
        table_frame = ttk.Frame(root)
        table_frame.grid(
            row=3, column=0, columnspan=2, rowspan=200, padx=4, pady=1, sticky="nswe"
        )

        # Create the table
        table = CustomTable(
            table_frame, dataframe=df, showtoolbar=False, showstatusbar=True
        )
        table.show()

        # Add more modern features
        table.autoResizeColumns()

    style = ttk.Style()
    style.theme_use("clam")  # Use a modern theme

    style.configure(
        "TLabel",
        font=("Helvetica", 12, "bold"),
        foreground="black",
        borderwidth=2,
        relief="raised",
    )
    style.configure("TEntry", font=("Helvetica", 11), borderwidth=2, relief="raised")
    style.configure(
        "TButton",
        font=("Helvetica", 12, "bold"),
        foreground="black",
        background="light gray",
        borderwidth=2,
        relief="raised",
    )
    style.configure("TFrame", borderwidth=2, relief="raised")

    custom_font = font.Font(family="Helvetica", size=18, weight="bold")
    reaction_label = ttk.LabelFrame(
        root, text="Reaction Equation or Chemical Formula (separated by commas)"
    )
    reaction_label.grid(row=0, column=0, padx=4, pady=1, sticky="nswe")

    num_columns = pd.read_excel("Thermodata.xlsx").shape[1]
    entry_width = num_columns * 6  # Adjust based on your preference
    reaction_entry = tk.Text(
        reaction_label, width=entry_width, height=1, font=custom_font
    )  
    
    # Increased width
    reaction_entry.insert(1.0, "H2O(g) = H2(g) + O2(g)")
    reaction_entry.grid(row=1, column=0, columnspan=3, padx=5, pady=1, sticky="nswe")

    temp_frame = ttk.LabelFrame(root, text="Temperature", padding=10)
    temp_frame.grid(row=1, column=0, columnspan=3, padx=5, pady=1, sticky="nswe")

    from_temp_label = ttk.Label(temp_frame, text="From (°K)", font=("Helvetica", 11))
    from_temp_label.grid(row=0, column=0, padx=5)

    from_temp_entry = ttk.Entry(temp_frame, width=8)
    from_temp_entry.insert(0, "298")
    from_temp_entry.grid(row=0, column=1, padx=5)

    to_temp_label = ttk.Label(temp_frame, text="To (°K)", font=("Helvetica", 11))
    to_temp_label.grid(row=0, column=2, padx=5)

    to_temp_entry = ttk.Entry(temp_frame, width=8)
    to_temp_entry.insert(0, "2000")
    to_temp_entry.grid(row=0, column=3, padx=5)

    step_temp_label = ttk.Label(temp_frame, text="Step (°K)", font=("Helvetica", 11))
    step_temp_label.grid(row=0, column=4, padx=5)

    step_temp_entry = ttk.Entry(temp_frame, width=8)
    step_temp_entry.insert(1, "100")
    step_temp_entry.grid(row=0, column=5, padx=5)

    calculate_button = ttk.Button(temp_frame, text="Calculate", command=calculate)
    calculate_button.grid(row=0, column=6, padx=5)

    # Ellingham Plot Area
    cmean_frame = ttk.LabelFrame(root, text="Chat", padding=2)
    cmean_frame.grid(row=0, column=4, columnspan=13, padx=(0, 5), pady=2, sticky="nswe")

    from_temp_label = ttk.Label(cmean_frame, text="Y-Axis", font=("Helvetica", 11))
    from_temp_label.grid(row=0, column=4, padx=5)

    calculate_button_h = ttk.Button(cmean_frame, text="Cp(J/(mol*K))")
    calculate_button_h.grid(row=0, column=14, padx=5)

    calculate_button_s = ttk.Button(cmean_frame, text="S°298")
    calculate_button_s.grid(row=0, column=6, padx=5)

    calculate_button_cp = ttk.Button(cmean_frame, text="H°298")
    calculate_button_cp.grid(row=0, column=10, padx=5)

    calculate_button = ttk.Button(cmean_frame, text="Delta_G")
    calculate_button.grid(row=0, column=32, padx=20)
# Create the table
    table_frame = ttk.Frame(root)
    table_frame.grid(
            row=3, column=0, columnspan=2, rowspan=200, padx=4, pady=1, sticky="nswe"
        )
    # Create the table
    table = CustomTable(
            table_frame, showtoolbar=False, showstatusbar=True
        )
    table.show()

    graph_frame = ttk.LabelFrame(root)
    graph_frame.grid(row=1, column=4, rowspan=200, padx=(0, 6), pady=1, sticky="nswe")

    fig, ax = plt.subplots(figsize=(6, 8))
    canvas = FigureCanvasTkAgg(fig, master=graph_frame)
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    # Pre-label the plot
    plt.xlabel("Temperature (K)")
    plt.ylabel("Delta G (kJ/mol)")
    plt.title("Ellingham Diagram")
    plt.axhline(y=0, color="k", linestyle="-", linewidth=0.5)
