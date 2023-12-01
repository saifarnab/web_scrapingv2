import pandas as pd


def run():
    # Read your original Excel file
    file_path = 'file.xlsx'
    df = pd.read_excel(file_path)

    # Calculate the number of rows in each chunk
    chunk_size = len(df) // 4

    # Split the DataFrame into four equal parts
    chunks = [df[i * chunk_size:(i + 1) * chunk_size] for i in range(4)]

    # Save each chunk as a separate Excel file
    for i, chunk in enumerate(chunks, start=1):
        chunk.to_excel(f'file_part_{i}.xlsx', index=False)


run()
