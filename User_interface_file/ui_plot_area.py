import tkinter as tk
from tkinter import ttk
import pandas as pd
import openpyxl
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
            reaction_entry.get().strip().split(",")
        )  # Split by commas
        temperature_from = float(from_temp_entry.get())
        temperature_to = float(to_temp_entry.get())
        temperature_step = int(step_temp_entry.get())

        file_path = (
            'chemical_species_data_base.json'  # Update with your file path for delta G calculation
        )
        s = plot_ellingham_diagram(
            file_path,
            reaction_equations,
            temperature_from,
            temperature_to,
            temperature_step,
            canvas,
        )
        
        path = "data_from_calculation.xlsx"
        workbook = openpyxl.load_workbook(path)
        sheet = workbook.active

        list_values = list(sheet.values)
        print(list_values)

        for value_tuple in list_values[1:]:
           
           treeview.insert('', tk.END, values=value_tuple)


    def plot_data(data_column):
      
      df = pd.read_excel("data_from_calculation.xlsx")
      plt.figure(figsize=(8, 6))
      plt.plot(df['Temperature (K)'], df[data_column], linestyle='-')
      plt.xlabel('Temperature (K)')
      plt.axhline(y=0, color="k", linestyle="-", linewidth=0.5)
      plt.ylabel(data_column)
      plt.title(f'Plot of {data_column} vs Temperature')
      
      # Calculate the minimum and maximum values of the data column
      min_value = df[data_column].min()
      max_value = df[data_column].max()

      plt.ylim(min_value - 50, max_value + 50)
      
      canvas.figure.clf()  # Clear previous plot
      ax = canvas.figure.add_subplot(111)  # Add subplot
      ax.plot(df['Temperature (K)'], df[data_column], linestyle='-')  # Plot data
      ax.set_xlabel('Temperature (K)')
      ax.axhline(y=0, color="k", linestyle="-", linewidth=2)
      ax.set_ylabel(data_column)
      ax.set_title(f'Plot of {data_column} vs Temperature')
      canvas.draw()  # Update canvas with new plot

    
    frame = ttk.Frame(root)
    frame.pack()

    widgets_frame = ttk.LabelFrame(frame, text = "Reaction Equation or Chemical Formular")
    widgets_frame.grid(row = 0 , column= 0, padx= (5,10), pady=(5,1))

    reaction_entry = ttk.Entry(widgets_frame, width= 86 )
    reaction_entry.insert(0, "H2O(g) = H2(g) + O2(g)")
    reaction_entry.grid(row = 0, column = 0, padx= 5, pady=(0,5), columnspan= 3,sticky="ew")


    # Temperature Frame

    temperature_frame = ttk.LabelFrame(frame, text = "Temperature")
    temperature_frame.grid(row = 1 , column= 0, padx= (5,10), pady= 5)

    from_temp_label = ttk.Label(temperature_frame, text="From (°K)", font=("Helvetica", 11))
    from_temp_label.grid(row=0, column=0, padx=5)

    from_temp_entry = ttk.Entry(temperature_frame, width= 10 )
    from_temp_entry.insert(0, "298")
    from_temp_entry.grid(row = 0, column = 1, padx= 5, pady=5)

    to_temp_label = ttk.Label(temperature_frame, text="To (°K)", font=("Helvetica", 11), borderwidth = 9)
    to_temp_label.grid(row=0, column=2, padx=5)

    to_temp_entry = ttk.Entry(temperature_frame, width= 10 )
    to_temp_entry.insert(0, "1000")
    to_temp_entry.grid(row=0, column=3, padx=5)

    step_temp_label = ttk.Label(temperature_frame, text="Step (°K)", font=("Helvetica", 11), borderwidth = 9)
    step_temp_label.grid(row=0, column=4, padx=5)

    step_temp_entry = ttk.Entry(temperature_frame, width=10)
    step_temp_entry.insert(0, "100")
    step_temp_entry.grid(row=0, column=5, padx=5)

    calculate_button = ttk.Button(temperature_frame, text="Calculate", command= calculate)
    calculate_button.grid(row=0, column=6, padx=5)

    # Data area
    treeFrame = ttk.Frame(frame)
    treeFrame.grid(row = 2 , column= 0, pady= 10, padx =(5,10) )
    treeScroll = ttk.Scrollbar(treeFrame)
    treeScroll.pack(side = "right", fill = "y")


    cols = ("Temperature (K)" , "H°298", "S°298", "Heat Capicity","Delta G (KJ/mol)" )
    treeview = ttk.Treeview(treeFrame, columns=cols,
                        yscrollcommand= treeScroll.set, show="headings", height = 35)

    treeview.column("Temperature (K)", width = 117)
    treeview.column("H°298", width = 117) 
    treeview.column("S°298", width = 117)
    treeview.column("Heat Capicity", width = 117)
    treeview.column("Delta G (KJ/mol)", width = 117)

    for col in cols:
      
      treeview.heading(col , text=col, anchor= tk.W)

    treeview.pack()
    treeScroll.config( command= treeview.yview)



    # Button Plot Area frame
    
    cmean_frame = ttk.LabelFrame(frame, text="Plot Buttons", padding=2)
    cmean_frame.grid(row=0, column=1, padx=(0, 5), pady=(5, 1), sticky="nswe")

    from_temp_label = ttk.Label(cmean_frame, text="Y-Axis", font=("Helvetica", 11), borderwidth = 9 )
    from_temp_label.grid(row=0, column=0, padx=(10,5))

    calculate_button_h = ttk.Button(cmean_frame, text="Cp(J/(mol*K))",command=lambda: plot_data('Heat Capacity') )
    calculate_button_h.grid(row=0, column=1, padx= 27, pady= (0, 1))

    calculate_button_s = ttk.Button(cmean_frame, text="S°298", command=lambda: plot_data('S°298'))
    calculate_button_s.grid(row=0, column=2, padx=27, pady = (0,1))

    calculate_button_cp = ttk.Button(cmean_frame, text="H°298",command=lambda: plot_data('H°298'))
    calculate_button_cp.grid(row=0, column=3, padx= 27, pady = (0,1))

    calculate_button = ttk.Button(cmean_frame, text="Delta_G", command=lambda: plot_data('Delta G (kJ/mol)'))
    calculate_button.grid(row=0, column=4, padx=27, pady = (0, 1))

    #Graph area frame

    graph_area_frame= ttk.LabelFrame(frame, text="Graph Area", padding=2)
    graph_area_frame.grid(row=1, column=1, rowspan= 200,padx=(1, 5), pady=(5,10), sticky="nswe")

    graph_frame = tk.Frame(graph_area_frame)
    graph_frame.grid(row=0, column=0,padx=(1, 5), pady=1, sticky="nswe")


    fig, ax = plt.subplots(figsize=(7, 8))
    canvas = FigureCanvasTkAgg(fig, master=graph_frame)
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    # Pre-label the plot
    plt.xlabel("Temperature (K)")
    plt.ylabel("Delta G (kJ/mol)")
    plt.title("Ellingham Diagram")
    plt.axhline(y=0, color="k", linestyle="-", linewidth=0.5)


