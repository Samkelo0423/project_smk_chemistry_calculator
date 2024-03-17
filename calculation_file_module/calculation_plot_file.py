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
    temperatures = np.arange(temperature_from, temperature_to, temperature_step)
    reaction_equations = [eq.strip() for eq in reaction_equations]

    # Clear the previous plot
    
    plt.clf()
    canvas.figure.clf()
    

    max_delta_G = float("-inf")  # Initialize max_delta_G to negative infinity
    min_delta_G = float("inf")  # Initialize min_delta_G to positive infinity

    if "=" not in reaction_equations[0] and "+" not in reaction_equations[0]:

        for reaction_eq in reaction_equations:

            delta_G_values = []
            heat_capacity_list = []
            enthalpy_list = []
            entropy_list = []
            temperature_list = []

            for temperature in temperatures:

                delta_G, heat_capacity, enthalpy, entropy, temperature_1 = (
                    perform_calculations(file_path, temperature, reaction_eq)
                )
                delta_G_values.append(delta_G)
                heat_capacity_list.append(heat_capacity)
                enthalpy_list.append(enthalpy)
                entropy_list.append(entropy)
                temperature_list.append(temperature_1)
                max_delta_G = max(max_delta_G, delta_G)  # Update max_delta_G
                min_delta_G = min(min_delta_G, delta_G)  # Update min_delta_G

                # Create an empty DataFrame to store calculated values
                df = pd.DataFrame(
                    {
                        "Temperature (K)": temperature_list,
                        "H°298": enthalpy_list,
                        "S°298": entropy_list,
                        "Heat Capacity": heat_capacity_list,
                        "Delta G (kJ/mol)": delta_G_values,
                    }
                )
                print(df)

            color = np.random.rand(
                3,
            )
            plt.plot(temperatures, delta_G_values, label=reaction_eq, color=color)
            label_x = temperatures[0]
            label_y = delta_G_values[0]
            plt.text(
                label_x,
                label_y,
                reaction_eq,
                fontsize=8,
                color=color,
                horizontalalignment="left",
                verticalalignment="bottom",
                fontweight="bold",
            )

    else:

        for reaction_eq in reaction_equations:

            balanced_reactants, balanced_products = balance_equation(reaction_eq)
            balanced_eq = (
                " + ".join(balanced_reactants) + " = " + " + ".join(balanced_products)
            )

            delta_G_values = []
            heat_capacity_list = []
            enthalpy_list = []
            entropy_list = []
            temperature_list = []

            for temperature in temperatures:

                delta_G, heat_capacity, enthalpy, entropy, temperature_1= perform_calculations(
                    file_path, temperature, reaction_eq
                )

                delta_G_values.append(delta_G)
                enthalpy_list.append(enthalpy)
                entropy_list.append(entropy)
                heat_capacity_list.append(heat_capacity)
                temperature_list.append(temperature_1)
                max_delta_G = max(max_delta_G, delta_G)  # Update max_delta_G
                min_delta_G = min(min_delta_G, delta_G)  # Update min_delta_G

                # Append calculated values to the DataFrame
                df = pd.DataFrame(
                    {
                        "Temperature (K)": temperature_list,
                        "H°298": enthalpy_list,
                        "S°298": entropy_list,
                        "Heat Capacity": heat_capacity_list,
                        "Delta G (kJ/mol)": delta_G_values,
                    }
                )

            color = np.random.rand(
                3,
            )
            plt.plot(temperatures, delta_G_values, label=balanced_eq, color=color)
            label_x = temperatures[0]
            label_y = delta_G_values[0]
            plt.text(
                label_x,
                label_y,
                balanced_eq,
                fontsize=8,
                color=color,
                horizontalalignment="left",
                verticalalignment="bottom",
                fontweight="bold",
            )

    plt.xlabel("Temperature (K)")
    plt.ylabel("Delta G (kJ/mol)")
    plt.title("Ellingham Diagram")
    plt.ylim(min_delta_G - 50, max_delta_G + 50)  # Adjust y-axis limits
    plt.axhline(y=0, color="k", linestyle="-", linewidth=0.5)

    # Update the canvas with the new plot
    canvas.draw()

    # Return the DataFrame containing calculated values
    return df
