import pandas as pd

# Load the Excel file into a DataFrame
file_path = 'atp_1.1.xlsx'  # Replace with the actual file path
df = pd.read_excel(file_path)

# Convert 'TOURNAMENT_TIME' to datetime if it's in a string format
df['TOURNAMENT_TIME'] = pd.to_datetime(df['TOURNAMENT_TIME'], format='%d.%m.%Y %H:%M')

# Filter rows where 'TOURNAMENT_TIME' is in the year 2022
df_2022 = df[df['TOURNAMENT_TIME'].dt.year == 2022]

# Save the filtered DataFrame to a new Excel file
output_path_2022 = 'filtered_2022.xlsx'  # Replace with the desired output file path
df_2022.to_excel(output_path_2022, index=False)
