# import pandas as pd
# import os
#
#
# # Function to remove newlines from a value
# def remove_newlines(value):
#     if isinstance(value, str):
#         return value.replace('\n', ' ')
#     return value
#
#
# # Function to merge Excel files
# def merge_excel_files(input_folder, output_file):
#     all_data = pd.DataFrame()
#
#     # Iterate through each file in the input folder
#     for filename in os.listdir(input_folder):
#         if filename.endswith('.xlsx'):
#             filepath = os.path.join(input_folder, filename)
#             print(f'working file {filepath}')
#             # Read each Excel file into a DataFrame
#             df = pd.read_excel(filepath)
#             # Remove newlines from all cells
#             df = df.applymap(remove_newlines)
#             # Concatenate data from this file to the merged DataFrame
#             all_data = pd.concat([all_data, df], ignore_index=True)
#
#     # Write the merged DataFrame to a new Excel file
#     all_data.to_excel(output_file, index=False)
#
#
# # Specify the input folder containing Excel files and the output file
# input_folder = '_applibs'
# output_file = 'global/wta_2023.xlsx'
#
# # Merge Excel files
# merge_excel_files(input_folder, output_file)
#
# print("Excel files merged and saved to:", output_file)


# import os
# import pandas as pd
#
# # Folder containing Excel files
# folder_path = '_applibs'
#
# # Get a list of Excel files in the folder
# excel_files = [f for f in os.listdir(folder_path) if f.endswith('.xlsx') or f.endswith('.xls')]
#
# # Sort the file names in ascending order
# sorted_files = sorted(excel_files)
#
# # Initialize an empty DataFrame to store the merged data
# merged_data = pd.DataFrame()
#
# # Merge the Excel files in ascending order
# for file in sorted_files:
#     file_path = os.path.join(folder_path, file)
#     print(file_path)
#     df = pd.read_excel(file_path)  # Read the Excel file into a DataFrame
#     merged_data = pd.concat([merged_data, df], ignore_index=True)  # Concatenate DataFrames
#
# # Save the merged data to a new Excel file
# merged_data.to_excel('local/atp_4.xlsx', index=False)
#
# print('Excel files merged and saved to merged_excel_files.xlsx.')

import os
import pandas as pd

# Folder containing Excel files
folder_path = '_applibs'

# Get a list of Excel files in the folder
excel_files = [f for f in os.listdir(folder_path) if f.endswith('.xlsx') or f.endswith('.xls')]

# Sort the file names in ascending order
sorted_files = sorted(excel_files)

# Initialize an empty DataFrame to store the merged data
merged_data = pd.DataFrame()

# Merge the Excel files in ascending order
for file in sorted_files:
    file_path = os.path.join(folder_path, file)
    print(file_path)
    df = pd.read_excel(file_path)  # Read the Excel file into a DataFrame

    # Remove spaces from column names starting from "PBP_SET_1_GAME_1"
    gb_index = df.columns.get_loc("PBP_SET_1_GAME_1")
    for i in range(gb_index, len(df.columns)):
        df.rename(columns={df.columns[i]: df.columns[i].replace(' ', '')}, inplace=True)

    # Remove spaces from column values starting from "PBP_SET_1_GAME_1"
    for column in df.columns[gb_index:]:
        if df[column].dtype == 'object':
            df[column] = df[column].str.replace(' ', '')

    merged_data = pd.concat([merged_data, df], ignore_index=True)  # Concatenate DataFrames

# Save the merged and cleaned data to a new Excel file
merged_data.to_excel('wta_v2.xlsx', index=False)

print('Excel files merged and cleaned, and saved to merged_and_cleaned_excel_files.xlsx.')
