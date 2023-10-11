import pandas as pd
import os


# Function to remove newlines from a value
def remove_newlines(value):
    if isinstance(value, str):
        return value.replace('\n', ' ')
    return value


# Function to merge Excel files
def merge_excel_files(input_folder, output_file):
    all_data = pd.DataFrame()

    # Iterate through each file in the input folder
    for filename in os.listdir(input_folder):
        if filename.endswith('.xlsx') or filename.endswith('.xls'):
            filepath = os.path.join(input_folder, filename)
            # Read each Excel file into a DataFrame
            df = pd.read_excel(filepath)
            # Remove newlines from all cells
            df = df.applymap(remove_newlines)
            # Concatenate data from this file to the merged DataFrame
            all_data = pd.concat([all_data, df], ignore_index=True)

    # Write the merged DataFrame to a new Excel file
    all_data.to_excel(output_file, index=False)


# Specify the input folder containing Excel files and the output file
input_folder = 'global'
output_file = 'local/merged_output.xlsx'

# Merge Excel files
merge_excel_files(input_folder, output_file)

print("Excel files merged and saved to:", output_file)
