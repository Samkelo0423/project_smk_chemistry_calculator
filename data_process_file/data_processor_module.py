import pandas as pd

def parse_database_chemical_speacies(file_path):
    try:
        # Read Excel file into a Pandas DataFrame
        df = pd.read_json(file_path)
        
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

    # 3. Enthalpy and Entropy Columns - Log missing values

    if df['H 298 (kcal/mol)'].isnull().any() or df['S 298 (cal/mol*K)'].isnull().any():
        df['H 298 (kcal/mol)'] = df['H 298 (kcal/mol)'].fillna(0)
        df['S 298 (cal/mol*K)'] = df['S 298 (cal/mol*K)'].fillna(0)
        missing_columns.append("Missing values in 'H 298' or 'S 298' columns have been replaced with 0.")

    # 4. Temperature Range Columns - Log missing values

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

    # 6. Heat Capacity Coefficients - Log missing values

    try:
        df.fillna(0, inplace=True)
        if df['A'].isnull().any() or df['B'].isnull().any() or df['C'].isnull().any() or df['D'].isnull().any():
            raise ValueError("Missing values found in heat capacity coefficients A, B, C, and D")
    except Exception as e:
        print(f"An error occurred: {e}")

def preprocess_data(df):
    try:
        # Convert enthalpy and entropy values to kJ/mol and kj/mol*K because the data is in cal
        df['H 298 (kcal/mol)']*4.184
        df['S 298 (cal/mol*K)']*0.004184
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


