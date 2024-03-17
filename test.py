import math


def calculate_entropy(entropy, delta_a, delta_b, temperature):

    term_1 = float(delta_a * (math.log(temperature) - math.log(298)))
    term_2 = float(delta_b * 10**-3 * (temperature - 298))

    entropy_1 = entropy + term_1 + term_2

    return entropy_1

s = calculate_entropy(201 , 50.20 , 14.20, 500)
print(s)