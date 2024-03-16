from sympy import Matrix
import re
from sympy.ntheory import factorint


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
        state_mapping = {'g': 'gas', 'l': 'liq', 's': 'sol'}  # Updated state mapping
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
                state = parts[1].replace(')', '').strip().lower()  # Convert to lowercase for consistency
                state = state_mapping.get(state, None)  # Map the state to its standardized form
                if state is not None:
                    state = state.strip()  # Remove leading or trailing spaces inside single quotes
                
                # Append the parsed formula to the list
                parsed_list.append({'coefficient': coefficient,'formula': formula, 'state': state})
            else:
                raise ValueError("Invalid format")
        
        # Print the final parsed list
        print("Parsed Formula List:")
        for idx, entry in enumerate(parsed_list, 1):
            # Format the output string without leading or trailing spaces inside single quotes
            formatted_entry = {key: f"{value.strip()}" if isinstance(value, str) else value for key, value in entry.items()}
            print(f"Entry{idx}: {formatted_entry}")
        
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

    def parse_state(compound):
        state_match = re.search(r'\((\w+)\)', compound.strip())
        return state_match.group(1) if state_match else None

    def remove_state(compound):
        return re.sub(r'\(\w+\)', '', compound.strip())  # Updated to remove leading/trailing spaces

    def remove_coefficient(compound):
        return re.sub(r'^\d+', '', compound.strip())  # Remove only the leading numerical coefficient

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

    def addToMatrix(element, index, count, side):
        if index == len(elementMatrix):
            elementMatrix.append([])
            for x in elementList:
                elementMatrix[index].append(0)
        if element not in elementList:
            elementList.append(element)
            for i in range(len(elementMatrix)):
                elementMatrix[i].append(0)
        column = elementList.index(element)
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

    def compoundDecipher(compound, index, side):
        segments = re.split('(\([A-Za-z0-9]*\)[0-9]*)', compound)
        for segment in segments:
            if segment.startswith("("):
                segment = re.split('\)([0-9]*)', segment)
                if len(segment) > 1 and segment[1] != '':
                    multiplier = int(segment[1])
                else:
                    multiplier = 1
                segment = segment[0][1:]
            else:
                multiplier = 1
            segment = segment.strip()  # Remove leading and trailing whitespace
            findElements(segment, index, multiplier, side)

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
