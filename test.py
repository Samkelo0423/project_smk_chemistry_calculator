from sympy import Matrix
import re
from sympy import Matrix, lcm
from sympy.ntheory import factorint


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


