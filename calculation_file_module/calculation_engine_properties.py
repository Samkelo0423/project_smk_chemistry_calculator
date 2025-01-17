import numpy as np
import math
from data_process_file.data_processor_module import parse_excel_data
from data_process_file.equation_processor import parse_reaction_equation


def perform_calculations(file_path, temperature, reaction_equation):
    processed_data = parse_excel_data(file_path)

    if processed_data is None:
        print("Error: Failed to parse Excel data.")
        return None
    
    print("Processed Data for Calculations:")
    print(processed_data.head())  # Log the processed data to confirm its structure

    try:
        # Check if the reaction equation is a single-element formula
        if "=" in reaction_equation and "+" not in reaction_equation:
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
        sum_c_reactants = 0
        sum_d_reactants = 0
        sum_a_products = 0
        sum_b_products = 0
        sum_c_products = 0
        sum_d_products = 0

        for substance_type, substances in [
            ("Reactant", reactants),
            ("Product", products),
        ]:
            for substance in substances:
                coefficient = substance["coefficient"]
                substance_formula = substance["formula"].strip()
                phase = substance["Phase"]

                # Attempt exact match with phase included (e.g, "Al(g)")
                substance_data = processed_data[
                    (processed_data["Formula"] == f"{substance_formula}({phase})")
                    & (processed_data["Phase"] == phase)
                ]

                # if the exact match fails, fallback to formula only search
                if substance_data.empty:
                    substance_data = processed_data[
                        (processed_data["Formula"] == substance_formula)
                        & (processed_data["Phase"] == phase)
                    ]

                if not substance_data.empty:
                    delta_H = substance_data.iloc[0]["H 298 (kcal/mol)"]
                    delta_S = substance_data.iloc[0]["S 298 (cal/mol*K)"]
                    a_value = substance_data.iloc[0]["A"]
                    b_value = substance_data.iloc[0]["B"]
                    c_value = substance_data.iloc[0]["C"]
                    d_value = substance_data.iloc[0]["D"]

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
                    
                    if c_value != 0:
                        c_value /= 1000
                    else:
                        c_value = 1e-6
                    
                    if d_value != 0:
                        d_value /= 1000
                    else:
                        d_value = 1e-6

                    if substance_type == "Reactant":
                        sum_enthalpy_reactants += delta_H
                        sum_entropy_reactants += delta_S
                        sum_a_reactants += a_value
                        sum_b_reactants += b_value
                        sum_c_reactants += c_value
                        sum_d_reactants += d_value
                    else:
                        sum_enthalpy_products += delta_H
                        sum_entropy_products += delta_S
                        sum_a_products += a_value
                        sum_b_products += b_value
                        sum_c_products += c_value
                        sum_d_products += d_value

                    change_in_enthalpy = sum_enthalpy_products - sum_enthalpy_reactants
                    change_in_entropy = sum_entropy_products - sum_entropy_reactants
                    change_in_a = sum_a_products - sum_a_reactants
                    change_in_b = sum_b_products - sum_b_reactants
                    change_in_c = sum_c_products - sum_c_reactants
                    change_in_d = sum_d_products - sum_d_reactants

                    contribution_of_coefficients = (
                        calculate_contribution_of_coefficients(
                            change_in_a, change_in_b, change_in_c, change_in_d, temperature
                        )
                    )

                    heat_capacity = calculate_heat_capacity(
                        a_value, b_value, c_value, d_value, temperature
                    )
                    entropy_calculation = calculate_entropy_change(
                        change_in_entropy, change_in_a, change_in_b, change_in_c, change_in_d, temperature
                    )
                    enthalpy_calculation = calculate_enthalpy_change(
                        change_in_enthalpy, change_in_a, change_in_b, change_in_c, change_in_d, temperature
                    )

                    delta_G = (
                        change_in_enthalpy
                        - temperature * change_in_entropy
                        + contribution_of_coefficients
                    )

                else:
                    print(
                        f"Error: Substance '{substance_formula}' with state '{phase}' not found in the database. Skipping..."
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
                phase = substance_1["Phase"]

                # Attempt exact match with phase included (e.g, "Al(g)")
                substance_data = processed_data[
                    (processed_data["Formula"] == f"{substance_formula}({phase})")
                    & (processed_data["Phase"] == phase)
                ]

                # if the exact match fails, fallback to formula only search
                if substance_data.empty:
                    substance_data = processed_data[
                        (processed_data["Formula"] == substance_formula)
                        & (processed_data["Phase"] == phase)
                    ]

                if not substance_data.empty:
                    delta_H = substance_data.iloc[0]["H 298 (kcal/mol)"]
                    delta_S = substance_data.iloc[0]["S 298 (cal/mol*K)"]
                    a_value = substance_data.iloc[0]["A"]
                    b_value = substance_data.iloc[0]["B"]
                    c_value = substance_data.iloc[0]["C"]
                    d_value = substance_data.iloc[0]["D"]

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
                            a_value, b_value, c_value, d_value, temperature
                        )
                    )

                    heat_capacity = calculate_heat_capacity(
                        a_value, b_value, c_value, d_value, temperature
                    )

                    entropy_calculation = calculate_entropy_change(
                        delta_S, a_value, b_value, c_value, d_value, temperature
                    )
                    enthalpy_calculation = calculate_enthalpy_change(
                        delta_S, a_value, b_value, c_value, d_value, temperature
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
        print(f"Error occurred: {e}")
        return None


def calculate_contribution_of_coefficients(delta_a, delta_b, delta_c, delta_d, temperature):
    """
    Calculate the contribution of coefficients to the Gibbs free energy.

    Args:
        delta_a (float): Change in the 'a' coefficient.
        delta_b (float): Change in the 'b' coefficient.
        delta_c (float): Change in the 'c' coefficient.
        delta_d (float): Change in the 'd' coefficient.
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
    term_3 = delta_c * 10**5 * (-0.5/temperature + 1/298 - 0.5*temperature/298**2)
    term_4 = delta_d * 10**-3 * (-1/6 * temperature**3 - 1/3 * 298**3 + 0.5*298**2 * temperature)
    result_1 = term_1 + term_2 + term_3 + term_4
  

    return result_1

def is_single_element_formula(reaction_equation):
    # Check if the reaction equation contains only the "=" sign
    return "=" in reaction_equation and "+" not in reaction_equation

def calculate_heat_capacity(delta_a, delta_b, delta_c, delta_d, temperature):
    """
    Calculate the heat capacity at a given temperature.

    Args:
        delta_a (float): Change in the 'a' coefficient.
        delta_b (float): Change in the 'b' coefficient.
        delta_c (float): Change in the 'c' coefficient.
        delta_d (float): Change in the 'd' coefficient.
        temperature (float): Temperature in Kelvin.

    Returns:
        float: Heat capacity at the given temperature.
    """
    term_1 = delta_a * (temperature - 298)
    term_2 = delta_b * 10**-3 * 0.5 * (temperature**2 - 298**2)
    term_3 = delta_c * 10**5 * (1/298 - 1/temperature)
    term_4 = delta_d * 10**-6 * 1/3 * (temperature**3 - 298**3)
    result_1 = term_1 + term_2 + term_3 + term_4
    return result_1

def calculate_enthalpy_change(enthalpy_298, delta_a, delta_b, delta_c, delta_d, temperature):
    """
    Calculate the enthalpy change (ΔH°T) at a given temperature T.

    Args:
        enthalpy_298 (float): Enthalpy at 298 K.
        delta_a (float): Change in the 'a' coefficient.
        delta_b (float): Change in the 'b' coefficient.
        delta_c (float): Change in the 'c' coefficient.
        delta_d (float): Change in the 'd' coefficient.
        temperature (float): Temperature in Kelvin.

    Returns:
        float: Enthalpy change (ΔH°T) at the given temperature.
    """
    integral = 0
    for T in range(298, int(temperature + 1), 1):
        integral += calculate_heat_capacity(delta_a, delta_b, delta_c, delta_d, T)

    enthalpy_change = enthalpy_298 + integral

    return enthalpy_change

def calculate_entropy_change(entropy_298, delta_a, delta_b, delta_c, delta_d, temperature):
    """
    Calculate the entropy change (ΔS°T) at a given temperature T.

    Args:
        entropy_298 (float): Entropy at 298 K.
        delta_a (float): Change in the 'a' coefficient.
        delta_b (float): Change in the 'b' coefficient.
        delta_c (float): Change in the 'c' coefficient.
        delta_d (float): Change in the 'd' coefficient.
        temperature (float): Temperature in Kelvin.

    Returns:
        float: Entropy change (ΔS°T) at the given temperature.
    """
    integral = 0
    for T in range(298, int(temperature), 1):
        integral += calculate_heat_capacity(delta_a, delta_b, delta_c, delta_d, T) / T

    entropy_change = entropy_298 + integral

file_path = (
            "HSC_database.xlsx"  # Update with your file path for delta G calculation
        )

reaction_equation = "H2O(g) = H2(g) + O2(g)"

free_gibs = perform_calculations(file_path, 200, reaction_equation)
print(free_gibs)