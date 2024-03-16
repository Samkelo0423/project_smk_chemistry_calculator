import pandas as pd

def parse_excel_data(file_path):
    try:
        # Read Excel file into a Pandas DataFrame
        df = pd.read_excel(file_path)
        
        # Perform data validation checks
        # (e.g., check for required columns, data types, missing values)
        validate_data(df)
        
        # Preprocess the data if necessary
        # (e.g., convert units, scale values)
        preprocessed_data = preprocess_data(df)
        
        return preprocessed_data
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
    required_columns = ['Name', 'Formula', 'State', 'Mol Mass', 'H°298', 'S°298', 'a', 'b', 'C mean','Temperature Range',]
    if not all(col in df.columns for col in required_columns):
        missing_columns.extend(set(required_columns) - set(df.columns))
        raise ValueError(f"Missing required columns in the DataFrame: {' ,'.join(missing_columns)}" )

    # 2. State Column
    valid_states = ['sol', 'liq', 'gas']
    if not df['State'].isin(valid_states).all():
        missing_columns.append("Invalid values in the 'State' column. Allowed values are: 'sol', 'liq', 'gas'.")


    # 3. Molar Mass Range
    out_of_range_values = df.loc[(df['Mol Mass'] < 0) | (df['Mol Mass'] > 500), 'Mol Mass'].tolist()
    if out_of_range_values:
     error_msg = "Molar mass values outside the expected range (0-500 g/mol): " + ', '.join(map(str, out_of_range_values))
     missing_columns.append(error_msg)

    # 4. Enthalpy and Entropy Columns
    if df['H°298'].isnull().any() or df['S°298'].isnull().any():
     df['H°298'] = df['H°298'].fillna(0)
     df['S°298'] = df['S°298'].fillna(0)
     missing_columns.append("Missing values in 'H°298' or 'S°298' columns have been replaced with 0.")

    # 5. Temperature Range Columns
     
    try:
     required_columns = ['Temperature Range']
     missing_columns = [col for col in required_columns if col not in df.columns]
     if missing_columns:
        raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
    
    # Split 'Temperature Range' into 'Temperature Range Start' and 'Temperature Range End'
     df[['Temperature Range Start', 'Temperature Range End']] = df['Temperature Range'].str.split('-', expand=True).astype(float)
    
    # Additional checks for data consistency
    # Check for missing values in 'Temperature Range Start' or 'Temperature Range End'
     if df['Temperature Range Start'].isnull().any() or df['Temperature Range End'].isnull().any():
        raise ValueError("Missing values found in 'Temperature Range Start' or 'Temperature Range End' columns.")
    
    # Check temperature range values
     if (df['Temperature Range Start'] < 0).any() or (df['Temperature Range End'] > 5000).any():
        raise ValueError("Temperature range values outside the expected range (0-5000 K).")
    
    # Check if 'Temperature Range Start' is less than 'Temperature Range End'
     if (df['Temperature Range Start'] >= df['Temperature Range End']).any():
        raise ValueError("Temperature range start must be less than temperature range end.")
    except Exception as e:
      print(f"An error occurred: {e}")

    # 6. Heat Capacity Coefficients
    try:
     # Replace empty values with zero
      df.fillna(0, inplace=True)
      if df['a'].isnull().any() or df['b'].isnull().any() or df['C mean'].isnull().any():
        raise ValueError("Missing values found in heat capacity coefficients (a, b,) or C mean.")
     
    except Exception as e:
     print(f"An error occurred: {e}")

    
def preprocess_data(df):
   
    try:
        # Convert enthalpy and entropy values to kJ/mol
        df['H°298'] /= 1000
        df['S°298'] /= 1000
    except KeyError as e:
        print(f"Error converting enthalpy and entropy values: {e}")
    
    
    try:
        # Split 'Temperature Range' into 'Temperature Range Start' and 'Temperature Range End'
        df[['Temperature Range Start', 'Temperature Range End']] = df['Temperature Range'].str.split('-', expand=True)
        df['Temperature Range Start'] = pd.to_numeric(df['Temperature Range Start'], errors='coerce').fillna(0)
        df['Temperature Range End'] = pd.to_numeric(df['Temperature Range End'], errors='coerce').fillna(0)
    except (KeyError, ValueError) as e:
        print(f"Error extracting temperature range data: {e}")
    
    try:
        # Convert heat capacity coefficients to float and replace empty strings with zero
        df['a'] = pd.to_numeric(df['a'], errors='coerce').fillna(0)
        df['b'] = pd.to_numeric(df['b'], errors='coerce').fillna(0)
        df['C mean'] = pd.to_numeric(df['C mean'], errors='coerce').fillna(0)
    except (KeyError, ValueError) as e:
        print(f"Error extracting heat capacity coefficients: {e}")
    
    return df