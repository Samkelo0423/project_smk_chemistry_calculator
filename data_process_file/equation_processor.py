from sympy import Matrix,lcm
import re
from sympy import Matrix
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
                Phase = parts[1].replace(')', '').strip().lower()  # Convert to lowercase for consistency
                if Phase is not None:
                    Phase = Phase.strip()  # Remove leading or trailing spaces inside single quotes
                
                # Append the parsed formula to the list
                parsed_list.append({'coefficient': coefficient,'formula': formula, 'phase': Phase})
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