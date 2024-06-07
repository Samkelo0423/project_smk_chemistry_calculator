The provided code consists: 
data_processor_module.py, equation_processor.py, and calculation_engine_properties.py, 
and one script: calculation_plot_file.py.


data_processor_module.py 
contains a function validate_data(df) that validates the input DataFrame based on certain criteria such as required columns,
state column, molar mass range, enthalpy and entropy columns, temperature range columns, and heat capacity coefficients.
If any of the criteria are not met, the function raises a ValueError with an appropriate error message.

equation_processor.py contains two functions: 
parse_reaction_equation(reaction_equation) and balance_equation(full_equation, given_coefficients=None). 
The parse_reaction_equation function takes a reaction equation as input and returns a list of dictionaries containing the coefficients, 
formulas, and states of the reactants and products. The balance_equation function takes a full equation as input and balances it using a matrix-based approach.
If given_coefficients are provided, the function replaces the calculated coefficients with the given ones.

calculation_engine_properties.py contains several functions that perform calculations related to thermodynamics such as calculating free Gibbs energy, 
heat capacity, entropy change, and enthalpy change. These functions take processed data, reaction equation, and temperature as inputs and return the calculated values.

calculation_plot_file.py contains a function plot_ellingham_diagram that plots an Ellingham diagram for a given set of reaction equations. 
The function uses the perform_calculations function from calculation_engine_properties.py to calculate the free Gibbs energy for each temperature in a given range.
The calculated values are then plotted using matplotlib.
