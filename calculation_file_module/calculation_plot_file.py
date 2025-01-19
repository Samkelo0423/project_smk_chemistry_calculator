import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
from calculation_file_module.calculation_engine_properties import perform_calculations
from data_process_file.equation_processor import balance_equation

def plot_ellingham_diagram(
    file_path,
    reaction_equations,
    temperature_from,
    temperature_to,
    temperature_step,
    canvas,
):
    # Generate temperature range
    temperatures = np.linspace(temperature_from, temperature_to, temperature_step)
    reaction_equations = [eq.strip() for eq in reaction_equations]

    # Clear the previous plot on the canvas
    canvas.figure.clf()
    ax = canvas.figure.add_subplot(111)  # Add a subplot for the plot

    max_delta_G = float("-inf")  # Initialize max_delta_G to negative infinity
    min_delta_G = float("inf")  # Initialize min_delta_G to positive infinity

    for reaction_eq in reaction_equations:
        if "=" not in reaction_eq and "+" not in reaction_eq:
            # If no balancing required
            balanced_eq = reaction_eq
        else:
            # If balancing is required
            balanced_reactants, balanced_products = balance_equation(reaction_eq)
            balanced_eq = (
                " + ".join(balanced_reactants) + " = " + " + ".join(balanced_products)
            )

        # Initialize lists to store calculated values
        delta_G_values = []
        heat_capacity_list = []
        enthalpy_list = []
        entropy_list = []
        temperature_list = []

        for temperature in temperatures:
            # Perform calculations
            delta_G, heat_capacity, enthalpy, entropy, temperature_1 = (
                perform_calculations(file_path, temperature, reaction_eq)
            )

            # Store results
            delta_G_values.append(delta_G)
            heat_capacity_list.append(heat_capacity)
            enthalpy_list.append(enthalpy)
            entropy_list.append(entropy)
            temperature_list.append(temperature_1)

            # Update min/max delta G
            max_delta_G = max(max_delta_G, delta_G)
            min_delta_G = min(min_delta_G, delta_G)

        # Create a DataFrame (if needed for debugging or saving)
        df = pd.DataFrame(
            {
                "Temperature (K)": temperature_list,
                "H°298": enthalpy_list,
                "S°298": entropy_list,
                "Heat Capacity": heat_capacity_list,
                "Delta G (kJ/mol)": delta_G_values,
            }
        )
        print(df)  # For debugging; remove in production

        # Plot data
        color = np.random.rand(3)
        ax.plot(
            temperatures,
            delta_G_values,
            label=balanced_eq,
            color=color,
        )
        # Annotate the start point of the reaction
        ax.text(
            temperatures[0],
            delta_G_values[0],
            balanced_eq,
            fontsize=8,
            color=color,
            horizontalalignment="left",
            verticalalignment="bottom",
            fontweight="bold",
        )

    # Set plot labels, title, and limits
    ax.set_xlabel("Temperature (K)")
    ax.set_ylabel("Delta G (kJ/mol)")
    ax.set_title("Ellingham Diagram")
    ax.set_ylim(min_delta_G - 50, max_delta_G + 50)  # Adjust y-axis limits
    ax.axhline(y=0, color="k", linestyle="-", linewidth=0.5)  # Add y=0 line
    ax.legend(fontsize=8)

    # Draw the updated canvas
    canvas.draw()
