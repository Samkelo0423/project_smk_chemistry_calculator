from tkinter import ttk
import tkinter as tk
import pandas as pd
import openpyxl
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from calculation_file_module.calculation_plot_file import plot_ellingham_diagram


def create_ui(root):


    def calculate():
        try:
            reaction_equations = (
                reaction_entry.get().strip().split(",")
            )  # Split by commas
            temperature_from = float(from_temp_entry.get().strip())
            temperature_to = float(to_temp_entry.get().strip())
            temperature_step = int(step_temp_entry.get().strip())

            file_path = (
                'chemical_species_data_base.json'  # Update with your file path for delta G calculation
            )
            
            s = plot_ellingham_diagram(
                file_path,
                reaction_equations,
                temperature_from,
                temperature_to,
                temperature_step,
                canvas_2
            )

            plot_data('Heat Capacity')

            path = "data_from_calculation.xlsx"
            workbook = openpyxl.load_workbook(path)
            sheet = workbook.active
            list_values = list(sheet.values)
            print(list_values)
        except ValueError:
            tk.messagebox.showerror("Input Error", "Please enter valid numerical values for temperature.")
        except Exception as e:
            tk.messagebox.showerror("Error", str(e))

    def plot_data(data_column):
         # Read the data
        df = pd.read_excel("data_from_calculation.xlsx")

        # Optional: Generate a standalone plot and save it (if needed)
        plt.figure(figsize=(7, 8.2))
        plt.plot(df['Temperature (K)'], df[data_column], linestyle='-')
        plt.xlabel('Temperature (K)')
        plt.ylabel(data_column)
        plt.title(f'Plot of {data_column} vs Temperature')
        #plt.savefig(f"{data_column}_plot.png")  # Save if required
        plt.close()  # Close the standalone plot

        # Calculate min and max values for y-axis limits
        min_value = df[data_column].min()
        max_value = df[data_column].max()

        # Clear the previous plot on canvas_1
        canvas_1.figure.clf()  # Clear previous figure from canvas
        ax = canvas_1.figure.add_subplot(111)  # Add a new subplot
        ax.plot(df['Temperature (K)'], df[data_column], linestyle='-')  # Plot on canvas
        ax.set_xlabel('Temperature (K)')
        ax.set_ylabel(data_column)
        ax.set_title(f'Plot of {data_column} vs Temperature')
        ax.set_ylim(min_value - 50, max_value + 50)  # Set y-axis limits
        canvas_1.draw()  # Update the canvas with the new plot

    frame = ttk.Frame(root)
    frame.pack()

    widgets_frame = ttk.LabelFrame(frame, text="Reaction Equation or Chemical Formula")
    widgets_frame.grid(row=0, column=0, padx=(5, 10), pady=(5, 1))

    reaction_entry = ttk.Entry(widgets_frame, width=86)
    reaction_entry.insert(0, "H2O(g) = H2(g) + O2(g)")
    reaction_entry.grid(row=0, column=0, padx=5, pady=(0, 5), columnspan=3, sticky="ew")

    # Temperature Frame
    temperature_frame = ttk.LabelFrame(frame, text="Temperature")
    temperature_frame.grid(row=0, column=1, padx=(5, 10), pady=5, sticky='nwes')

    from_temp_label = ttk.Label(temperature_frame, text="From (°K)", font=("Helvetica", 11))
    from_temp_label.grid(row=0, column=0, padx=7)

    from_temp_entry = ttk.Entry(temperature_frame, width=10)
    from_temp_entry.insert(0, "298")
    from_temp_entry.grid(row=0, column=1, padx=5, pady=5)

    to_temp_label = ttk.Label(temperature_frame, text="To (°K)", font=("Helvetica", 11))
    to_temp_label.grid(row=0, column=2, padx=5)

    to_temp_entry = ttk.Entry(temperature_frame, width=10)
    to_temp_entry.insert(0, "1000")
    to_temp_entry.grid(row=0, column=3, padx=5)

    step_temp_label = ttk.Label(temperature_frame, text="Step (°K)", font=("Helvetica", 11))
    step_temp_label.grid(row=0, column=4, padx=5)

    step_temp_entry = ttk.Entry(temperature_frame, width=10)
    step_temp_entry.insert(0, "100")
    step_temp_entry.grid(row=0, column=5, padx=5)

    calculate_button = ttk.Button(temperature_frame, text="Calculate", command=calculate, width= 20)
    calculate_button.grid(row=0, column=6, padx=(20 , 1))

    # Button Plot Area frame
    cmean_frame = ttk.LabelFrame(frame, text="Plot Buttons", padding=1)
    cmean_frame.grid(row=1, column=0, padx=(0, 4), pady=5 )

    from_temp_label = ttk.Label(cmean_frame, text="Y-Axis", font=("Helvetica", 11))
    from_temp_label.grid(row=0, column=0, padx=(10, 5))

    calculate_button_h = ttk.Button(cmean_frame, text="Cp(J/(mol*K))", command=lambda: plot_data('Heat Capacity'), width=18)
    calculate_button_h.grid(row=0, column=1, padx=20, pady=(1, 1))

    calculate_button_s = ttk.Button(cmean_frame, text="S°298", command=lambda: plot_data('S°298'), width=18)
    calculate_button_s.grid(row=0, column=2, padx=20, pady=(1, 1))

    calculate_button_cp = ttk.Button(cmean_frame, text="H°298", command=lambda: plot_data('H°298'), width=18)
    calculate_button_cp.grid(row=0, column=3, padx=20, pady=(1, 1))

    # Graph area frame 1
    graph_area_frame_1 = ttk.LabelFrame(frame, text="Cp , S , H plot Area", padding=2)
    graph_area_frame_1.grid(row=2, column=0, ipadx=1, pady=5, padx=(5, 10), sticky='nswe')

    frame.rowconfigure(2, weight=1)
    frame.columnconfigure(0, weight=10)

    graph_frame_1 = tk.Frame(graph_area_frame_1)
    graph_frame_1.grid(row=0, column=0, pady=0, padx=0, sticky="nsew")

    graph_area_frame_1.rowconfigure(0, weight=1)
    graph_area_frame_1.columnconfigure(0, weight=10)

    fig_1, ax = plt.subplots(figsize=(7, 8.1))
    canvas_1 = FigureCanvasTkAgg(fig_1, master=graph_frame_1)
    canvas_1.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    # Pre-label the plot
    plt.xlabel("Temperature (K)")
    plt.ylabel("Heat Capacity")
    plt.title("Plot of Heat Capacity vs Temperature")
    plt.axhline(y=0, color="k", linestyle="-", linewidth=0.5)

    # Graph area frame 2
    graph_area_frame_2 = ttk.LabelFrame(frame, text="Ellingham Diagram Plot", padding=2)
    graph_area_frame_2.grid(row=1, column=1, rowspan=200, padx=(1, 5), pady=(5, 10), sticky="nswe")

    graph_frame_2 = tk.Frame(graph_area_frame_2)
    graph_frame_2.grid(row=0, column=0, padx=(1, 5), pady=1, sticky="nswe")

    fig_2, ax = plt.subplots(figsize=(7, 8.2))
    canvas_2 = FigureCanvasTkAgg(fig_2, master=graph_frame_2)
    canvas_2.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    plt.xlabel("Temperature (K)")
    plt.ylabel("Delta G (kJ/mol)")
    plt.title("Plot of Delta G vs Temperature")
    plt.axhline(y=0, color="k", linestyle="-", linewidth=0.5)