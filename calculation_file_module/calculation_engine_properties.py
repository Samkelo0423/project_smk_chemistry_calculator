import numpy as np
import math
from data_process_file.data_processor_module import parse_excel_data
from data_process_file.equation_processor import parse_reaction_equation


def perform_calculations(file_path, temperature, reaction_equation):
    processed_data = parse_excel_data(file_path)

    if processed_data is None:
        print("Error: Failed to parse Excel data.")
        return None
    try:

        # Check if the reaction equation is a single-element formula
        if "=" and "+" not in reaction_equation:
            delta_G_reaction, heat_capacity, enthalpy, entropy, temperature_1 = (
                calculate_freegibbs_single_element(
                    processed_data, reaction_equation, temperature
                )
            )
        else:
            delta_G_reaction, heat_capacity, enthalpy, entropy, temperature_1 = (
                calculate_freegibbs(processed_data, reaction_equation, temperature)
            )

        return delta_G_reaction, heat_capacity, enthalpy, entropy, temperature_1

    except Exception as e:
        print(f"Calculation error: {e}")
        return None


def calculate_freegibbs(processed_data, reaction_equation, temperature):
    try:
        reactants, products = parse_reaction_equation(reaction_equation)

        sum_enthalpy_reactants = 0
        sum_entropy_reactants = 0
        sum_enthalpy_products = 0
        sum_entropy_products = 0
        sum_a_reactants = 0
        sum_b_reactants = 0
        sum_a_products = 0
        sum_b_products = 0

        for substance_type, substances in [
            ("Reactant", reactants),
            ("Product", products),
        ]:
            for substance in substances:
                coefficient = substance["coefficient"]
                substance_formula = substance["formula"].strip()
                state = substance["state"]
                substance_data = processed_data[
                    (processed_data["Formula"] == substance_formula)
                    & (processed_data["State"] == state)
                ]

                if not substance_data.empty:

                    delta_H = substance_data.iloc[0]["H°298"]
                    delta_S = substance_data.iloc[0]["S°298"]
                    a_value = substance_data.iloc[0]["a"]
                    b_value = substance_data.iloc[0]["b"]

                    delta_H *= coefficient
                    delta_S *= coefficient

                    if a_value != 0:
                        a_value /= 1000
                    else:
                        a_value = 1e-6

                    if b_value != 0:
                        b_value /= 1000
                    else:
                        b_value = 1e-6

                    if substance_type == "Reactant":
                        sum_enthalpy_reactants += delta_H
                        sum_entropy_reactants += delta_S
                        sum_a_reactants += a_value
                        sum_b_reactants += b_value
                    else:
                        sum_enthalpy_products += delta_H
                        sum_entropy_products += delta_S
                        sum_a_products += a_value
                        sum_b_products += b_value

                    change_in_enthalpy = sum_enthalpy_products - sum_enthalpy_reactants
                    change_in_entropy = sum_entropy_products - sum_entropy_reactants
                    change_in_a = sum_a_products - sum_a_reactants
                    change_in_b = sum_b_products - sum_b_reactants

                    contribution_of_coefficients = (
                        calculate_contribution_of_coefficients(
                            change_in_a, change_in_b, temperature
                        )
                    )

                    heat_capacity = calculate_heat_capacity(

                        a_value, b_value, temperature

                    )
                    entropy_calculation = calculate_entropy_change(
                        change_in_entropy, change_in_a, change_in_b, temperature
                    )
                    enthalpy_calculation = calculate_enthalpy_change(
                        change_in_enthalpy, change_in_a, change_in_b, temperature
                    )

                    delta_G = (

                        change_in_enthalpy
                        - temperature * change_in_entropy
                        + contribution_of_coefficients

                    )

                else:
                    print(
                        f"Error: Substance '{substance_formula}' with state '{state}' not found in the database. Skipping..."
                    )
        return (

                 delta_G,
                 heat_capacity,
                 enthalpy_calculation,
                 entropy_calculation,
                 
                 temperature

                 )

    except KeyError as e:
        print(f"KeyError occurred while accessing the DataFrame columns: {e}")
        return None

    except IndexError as e:
        print(f"IndexError occurred while accessing DataFrame elements: {e}")
        return None

    except ValueError as e:
        print(f"ValueError occurred: {e}")
        return None

    except Exception as e:
        print(f"Error occurred: {e}")
        return None


def calculate_freegibbs_single_element(processed_data, reaction_equation, temperature):

    single_element = parse_reaction_equation(reaction_equation)


    try:
        for substances_1 in [(single_element)]:
            for substance_1 in substances_1:
                substance_formula = substance_1["formula"].strip()
                state = substance_1["state"]

                substance_data = processed_data[
                    (processed_data["Formula"] == substance_formula)
                    & (processed_data["State"] == state)
                ]

                if not substance_data.empty:

                    delta_H = substance_data.iloc[0]["H°298"]
                    delta_S = substance_data.iloc[0]["S°298"]
                    a_value = substance_data.iloc[0]["a"]
                    b_value = substance_data.iloc[0]["b"]

                    if a_value != 0:
                        a_value /= 1000
                    else:
                        a_value = 1e-6

                    if b_value != 0:
                        b_value /= 1000
                    else:
                        b_value = 1e-6

                    delta_G = (
                        delta_H
                        - temperature * delta_S
                        + calculate_contribution_of_coefficients(
                            a_value, b_value, temperature
                        )
                    )

                    heat_capacity = calculate_heat_capacity(
                        a_value, b_value, temperature
                    )

                    entropy_calculation = calculate_entropy_change(
                        delta_S, a_value, b_value, temperature
                    )
                    enthalpy_calculation = calculate_enthalpy_change(
                        delta_S, a_value, b_value, temperature
                    )

                else:
                    print(
                        
                        f"Error: Substance '{substance_formula}' not found in the database."
                    )
                    return None

        return delta_G, heat_capacity, enthalpy_calculation, entropy_calculation, temperature

    except KeyError as e:
        print(f"KeyError occurred while accessing the DataFrame columns: {e}")
        return None

    except IndexError as e:
        print(f"IndexError occurred while accessing DataFrame elements: {e}")
        return None

    except ValueError as e:
        print(f"ValueError occurred: {e}")
        return None

    except Exception as e:
        print(f"Error occurred : {e}")
        return None


def calculate_contribution_of_coefficients(delta_a, delta_b, temperature):
    """
    Calculate the contribution of coefficients to the Gibbs free energy.

    Args:
        delta_a (float): Change in the 'a' coefficient.
        delta_b (float): Change in the 'b' coefficient.
        temperature (float): Temperature in Kelvin.

    Returns:
        float: Contribution of coefficients to the Gibbs free energy.
    """
    term_1 = delta_a * (
        temperature
        - 298
        - temperature * math.log(temperature)
        + temperature * math.log(298)
    )
    term_2 = delta_b * 10**-3 * (298 * temperature - 0.5 * temperature**2 - 0.5 * 298**2)
    result_1 = term_1 + term_2
  

    return result_1

def is_single_element_formula(reaction_equation):
    # Check if the reaction equation contains only the "=" sign
    return "=" in reaction_equation and "+" not in reaction_equation

def calculate_heat_capacity(delta_a, delta_b, temperature):
    """
    Calculate the heat capacity at a given temperature.

    Args:
        delta_a (float): Change in the 'a' coefficient.
        delta_b (float): Change in the 'b' coefficient.
        temperature (float): Temperature in Kelvin.

    Returns:
        float: Heat capacity at the given temperature.
    """
    term_1 = delta_a * (temperature - 298)
    term_2 = delta_b * 0.5 * (temperature**2 - 298**2)
    result_1 = term_1 + term_2
    return result_1

def calculate_enthalpy_change(enthalpy_298, delta_a, delta_b, temperature):
    """
    Calculate the enthalpy change (ΔH°T) at a given temperature T.

    Args:
        enthalpy_298 (float): Enthalpy at 298 K.
        delta_a (float): Change in the 'a' coefficient.
        delta_b (float): Change in the 'b' coefficient.
        temperature (float): Temperature in Kelvin.

    Returns:
        float: Enthalpy change (ΔH°T) at the given temperature.
    """
    integral = 0
    for T in range(298, int(temperature + 1), 1):
        integral += calculate_heat_capacity(delta_a, delta_b, T)

    enthalpy_change = enthalpy_298 + integral

    return enthalpy_change

def calculate_entropy_change(entropy_298, delta_a, delta_b, temperature):
    """
    Calculate the entropy change (ΔS°T) at a given temperature T.

    Args:
        entropy_298 (float): Entropy at 298 K.
        delta_a (float): Change in the 'a' coefficient.
        delta_b (float): Change in the 'b' coefficient.
        temperature (float): Temperature in Kelvin.

    Returns:
        float: Entropy change (ΔS°T) at the given temperature.
    """
    integral = 0
    for T in range(298, int(temperature), 1):
        integral += calculate_heat_capacity(delta_a, delta_b, T) / T

    entropy_change = entropy_298 + integral

    return entropy_change
