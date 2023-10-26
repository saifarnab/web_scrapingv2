import os
import pandas as pd

# Folder path containing the Excel files
folder_path = '_applibs'  # Replace with the actual path to your folder

# Get a list of Excel files in the folder
excel_files = [f for f in os.listdir(folder_path) if f.endswith('.xlsx')]

# Sort the Excel files in ascending order by name
excel_files.sort()

# Initialize an empty list to store DataFrames
dfs = []

# Iterate through each Excel file and read into a DataFrame
for file in excel_files:
    file_path = os.path.join(folder_path, file)
    df = pd.read_excel(file_path)
    dfs.append(df)

# Concatenate all DataFrames into one
merged_data = pd.concat(dfs, ignore_index=True)

# Save the merged data to a new Excel file
merged_file_path = 'local/wta.xlsx'  # Replace with the desired output file path
merged_data.to_excel(merged_file_path, index=False)

print(f'Merged data saved to {merged_file_path}')
