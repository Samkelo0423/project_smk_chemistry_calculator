import math
from sympy import Matrix, lcm
import re
from sympy import Matrix
from sympy.ntheory import factorint
import pandas as pd


def perform_calculations(file_path, temperature, reaction_equation):
    processed_data = parse_excel_data(file_path)

    if processed_data is None:
        print("Error: Failed to parse Excel data.")
        return None
    
    print("Processed Data for Calculations:")
    print(processed_data.head())  # Log the processed data to confirm its structure

    # Log the DataFrame structure
    print("DataFrame Structure:")
    print(processed_data.info())  # Log the structure of the DataFrame

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
                phase = substance["phase"]  # Corrected to 'phase'

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
                phase = substance_1["phase"]  # Corrected to 'phase'

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
    
    return entropy_change

def parse_excel_data(file_path):
    try:
        # Read Excel file into a Pandas DataFrame
        df = pd.read_excel(file_path)
        
        # Perform data validation checks
        validate_data(df)
        # Preprocess the data if necessary
        # (e.g., convert units, scale values)
        preprocessed_data = preprocess_data(df)
        
        return preprocessed_data # Return the filtered DataFrame
    
    except Exception as e:
        # Handle any errors encountered during data processing
        print(f"Error parsing Excel data: {e}")
        return None


def validate_data(df):
    
    """
    Validates the input DataFrame based on the following criteria:
    1. Required Columns
    2. State Column
    3. Molar Mass Range
    4. Enthalpy and Entropy Columns
    5. Temperature Range Columns
    6. Heat Capacity Coefficients
    """
    missing_columns = []

    # 1. Required Columns
    required_columns= ['Formula', 'MW (g/mol)', 'Melting P. (K)','Boiling P. (K)','T1 (K)','T2 (K)','Phase','H 298 (kcal/mol)','S 298 (cal/mol*K)','A','B','C','D','Density (g/cm3)']

    if not all(col in df.columns for col in required_columns):
        missing_columns.extend(set(required_columns) - set(df.columns))
        raise ValueError(f"Missing required columns in the DataFrame: {' ,'.join(missing_columns)}" )

    # 2. State Column
    valid_states= ['l','s','g','ia','ao']
    
    # Replace invalid values in 'Phase' column with a default value (e.g., 's')
    df['Phase'] = df['Phase'].where(df['Phase'].isin(valid_states), 's')
    
    # Replace missing values in 'Phase' column with the default value 's'
    df['Phase'].fillna('s', inplace=True)

    # Log the number of replacements made
    replaced_count = df['Phase'].isna().sum()
    if replaced_count > 0:
        print(f"Replaced {replaced_count} missing values in the 'Phase' column with default value 's'.")

    # 3. Enthalpy and Entropy Columns
    if df['H 298 (kcal/mol)'].isnull().any() or df['S 298 (cal/mol*K)'].isnull().any():
        df['H 298 (kcal/mol)'] = df['H 298 (kcal/mol)'].fillna(0)
        df['S 298 (cal/mol*K)'] = df['S 298 (cal/mol*K)'].fillna(0)
        missing_columns.append("Missing values in 'H 298' or 'S 298' columns have been replaced with 0.")

    # 4. Temperature Range Columns
    try:
        required_columns = ['T1 (K)', 'T2 (K)']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
        
        # Additional checks for data consistency
        if df['T1 (K)'].isnull().any() or df['T2 (K)'].isnull().any():
            raise ValueError("Missing values found in 'Temperature Range Start' or 'Temperature Range End' columns.")
        
        if (df['T1 (K)'] >= df['T2 (K)']).any():
            raise ValueError("Temperature range start must be less than temperature range end.")
    except Exception as e:
        print(f"An error occurred: {e}")

    # 6. Heat Capacity Coefficients
    try:
        df.fillna(0, inplace=True)
        if df['A'].isnull().any() or df['B'].isnull().any() or df['C'].isnull().any() or df['D'].isnull().any():
            raise ValueError("Missing values found in heat capacity coefficients A, B, C, and D")
    except Exception as e:
        print(f"An error occurred: {e}")

def preprocess_data(df):
    try:
        # Convert enthalpy and entropy values to kJ/mol
        df['H 298 (kcal/mol)'] 
        df['S 298 (cal/mol*K)'] 
    except KeyError as e:
        print(f"Error converting enthalpy and entropy values: {e}")
    
    try:
        # Split 'Temperature Range' into 'Temperature Range Start' and 'Temperature Range End'
        df['T1 (K)'] = pd.to_numeric(df['T1 (K)'], errors='coerce').fillna(0)
        df['T2 (K)'] = pd.to_numeric(df['T2 (K)'], errors='coerce').fillna(0)
    except (KeyError, ValueError) as e:
        print(f"Error extracting temperature range data: {e}")
    
    try:
        # Convert heat capacity coefficients to float and replace empty strings with zero
        df['A'] = pd.to_numeric(df['A'], errors='coerce').fillna(0)
        df['B'] = pd.to_numeric(df['B'], errors='coerce').fillna(0)
        df['C'] = pd.to_numeric(df['C'], errors='coerce').fillna(0)
        df['D'] = pd.to_numeric(df['D'], errors='coerce').fillna(0)
    except (KeyError, ValueError) as e:
        print(f"Error extracting heat capacity coefficients: {e}")

    # Select the first occurrence of each unique formula for each specific phase
    unique_values = df[['Formula', 'MW (g/mol)', 'Phase', 'T1 (K)' , 'T2 (K)','H 298 (kcal/mol)', 'S 298 (cal/mol*K)', 'A' , 'B' , 'C', 'D' , 'Density (g/cm3)']].drop_duplicates(subset=['Formula', 'Phase'])
   
    return unique_values

def parse_reaction_equation(reaction_equation):
    try:
        if "=" not in reaction_equation:
            if isinstance(reaction_equation, list):
                # If it's already a list, assume it's a list of formulas
                return parse_formula_list(reaction_equation)
            else:
                # If it's a single formula, convert it to a list
                list_1= []
                list_1.append(reaction_equation)
                return parse_formula_list(list_1)
        
        balanced_reactants, balanced_products = balance_equation(reaction_equation)
        reactants_list = parse_formula_list(balanced_reactants)
        products_list = parse_formula_list(balanced_products)

        return reactants_list, products_list

    except Exception as e:
        print(f"Error parsing reaction equation: {e}")
        return None, None


def parse_formula_list(formulas):
    try:
        parsed_list = []
        
        for item in formulas:
            # Strip leading and trailing whitespace
            item = item.strip()
            # Split the item into coefficient/formula and state
            parts = item.split('(')
            
            # Ensure the parts are in the expected format
            if len(parts) >= 2:
                # Extract the coefficient and formula
                coefficient_formula = parts[0].strip()
                if coefficient_formula[0].isdigit():
                    coefficient_end_index = 1
                    while coefficient_end_index < len(coefficient_formula) and coefficient_formula[coefficient_end_index].isdigit():
                        coefficient_end_index += 1
                    coefficient = int(coefficient_formula[:coefficient_end_index])
                    formula = coefficient_formula[coefficient_end_index:]
                else:
                    coefficient = 1  # If no coefficient specified, assume 1
                    formula = coefficient_formula
                
                # Extract and normalize the state
                phase = parts[1].replace(')', '').strip().lower()  # Convert to lowercase for consistency
                if phase is not None:
                    phase = phase.strip()  # Remove leading or trailing spaces inside single quotes
                
                # Append the parsed formula to the list
                parsed_list.append({'coefficient': coefficient, 'formula': formula, 'phase': phase})
            else:
                raise ValueError("Invalid format")
        
        return parsed_list
    
    except Exception as e:
        print(f"Error parsing formula list: {e}")
        return None


def lcm(arr):
    lcm = 1
    factors = {}
    for num in arr:
        num_factors = factorint(num)
        for factor, power in num_factors.items():
            factors[factor] = max(factors.get(factor, 0), power)
    for factor, power in factors.items():
        lcm *= factor ** power
    return lcm


def balance_equation(full_equation, given_coefficients=None):

    # Split the full equation into reactants and products
    equation_parts = full_equation.split("=")
    reactants_str = equation_parts[0].strip()
    products_str = equation_parts[1].strip()

    # Helper functions

    def parse_state(compound):
        state_match = re.search(r'\((\w+)\)', compound.strip())
        return state_match.group(1) if state_match else None

    def remove_state(compound):
        return re.sub(r'\(\w+\)', '', compound.strip()) 

    def remove_coefficient(compound):
        return re.sub(r'^\d+', '', compound.strip()) 

    def print_equation(compound, coeff):
        state = parse_state(compound)

        if state:
            return f"{coeff} {remove_state(compound).strip()} ({state.strip()})"
        else:
            return f"{coeff} {remove_state(compound).strip()}"

    reactants = reactants_str.replace(' ', '').split("+")
    products = products_str.replace(' ', '').split("+")

    elementList = []
    elementMatrix = []

    def addToMatrix(element, index, count, side, is_charge=False):
        if is_charge:  # Special case for charges
            if "Charge" not in elementList:
                elementList.append("Charge")  # Add charge as a pseudo-element
                for i in range(len(elementMatrix)):
                    elementMatrix[i].append(0)
            column = elementList.index("Charge")
        else:
            # Ensure the matrix has enough rows
            while index >= len(elementMatrix):
                # Initialize new row with zeros for all current elements
                elementMatrix.append([0] * len(elementList))

            if element not in elementList:
                elementList.append(element)
                # Add a new column for the new element in each existing row
                for i in range(len(elementMatrix)):
                    elementMatrix[i].append(0)

            column = elementList.index(element)

            # Now we can safely access elementMatrix[index]
            elementMatrix[index][column] += count * side

    def findElements(segment, index, multiplier, side):
        elementsAndNumbers = re.split('([A-Z][a-z]?)', segment)
        i = 0
        while i < len(elementsAndNumbers) - 1:  # last element always blank
            i += 1
            if len(elementsAndNumbers[i]) > 0:
                if elementsAndNumbers[i + 1].isdigit():
                    count = int(elementsAndNumbers[i + 1]) * multiplier
                    addToMatrix(elementsAndNumbers[i], index, count, side)
                    i += 1
                else:
                    addToMatrix(elementsAndNumbers[i], index, multiplier, side)

    for i in range(len(reactants)):
        compoundDecipher(reactants[i], i, 1)
    for i in range(len(products)):
        compoundDecipher(products[i], i + len(reactants), -1)

    elementMatrix = Matrix(elementMatrix)
    elementMatrix = elementMatrix.transpose()
    solution = elementMatrix.nullspace()[0]
    multiple = lcm([val.q for val in solution])
    solution = multiple * solution
    coefficients = solution.tolist()

    # If given coefficients are provided, replace them
    if given_coefficients:
        for i in range(len(given_coefficients)):
            coefficients[i][0] = given_coefficients[i]

    balanced_reactants = [
        print_equation(remove_coefficient(reactants[i]), coefficients[i][0]) for i in range(len(reactants))
    ]
    balanced_products = [
        print_equation(remove_coefficient(products[i]), coefficients[i + len(reactants)][0])
        for i in range(len(products))
    ]

    return balanced_reactants, balanced_products


file_path = (
            "HSC_database.xlsx"  # Update with your file path for delta G calculation
        )

reaction_equation = "H2O(g) = H2(g) + O2(g)"

free_gibs = perform_calculations(file_path, 200, reaction_equation)
print(free_gibs)
