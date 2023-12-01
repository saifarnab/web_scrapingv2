import os

import PyPDF2
import pandas as pd

file_path = '04_ANAMBRA_WEST-01_EZI_ANAM.xlsx'
folder_path = '04_ANAMBRA/04_ANAMBRA_WEST/01_EZI_ANAM'


def insert_save(single_row_data):
    try:
        try:
            df = pd.read_excel(file_path)
        except FileNotFoundError:
            columns = list(single_row_data.keys())
            df = pd.DataFrame(columns=columns)
        df = pd.concat([df, pd.DataFrame([single_row_data])], ignore_index=True)
        df.to_excel(file_path, index=False)
    except Exception as e:
        print(f"Error: {e}")


def create_excel():
    if os.path.isfile(file_path):
        return
    columns = ['Name', 'State', 'LGA', 'Ward', 'Delim', 'Gender', 'DOB', 'VIN', 'PU Code', 'PU Name']
    df = pd.DataFrame(columns=columns)
    df.to_excel(file_path, index=False)
    print(f"Excel file '{file_path}' created successfully with headers.")


def extract_text_from_pdf(pdf_path: str):
    state, lga, ward, pu, delim = '', '', '', '', ''
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            if page_num == 0:
                text_list = page.extract_text().split('\n')
                for text in text_list:
                    if 'State' in text:
                        state = text.replace('State', '').strip()
                    elif 'LGA' in text:
                        lga = text.replace('LGA', '').strip()
                    elif 'Ward' in text:
                        ward = text.replace('Ward', '').strip()
                    elif 'PU' in text:
                        pu = text.replace('PU', '').strip()
                    elif 'Delim' in text:
                        delim = text.replace('Delim', '').strip()

            else:
                text = page.extract_text().split('\n')
                data = text[8:]

                # Initialize the list of lists
                list_of_lists = []
                current_list = []

                # Iterate through the data
                for item in data:
                    if 'PAGE' in item:
                        # Start a new list when 'Page: 1 of' is encountered
                        if current_list:
                            list_of_lists.append(current_list)
                            current_list = []
                    else:
                        # Add item to the current list
                        current_list.append(item)

                # Add the last list to the list of lists
                if current_list:
                    list_of_lists.append(current_list)

                # Print the list of lists
                for index, sublist in enumerate(list_of_lists):
                    concatenated_data = ' '.join(sublist[:-2])
                    result = ''.join(char for char in concatenated_data if char.isalpha() or char.isspace())
                    name = result.strip()
                    vin = sublist[-2].replace('VIN:', '').strip()
                    dob = sublist[-1].replace('DOB-Y:', '').replace('|', '').replace('Gender: F', '').replace(
                        'Gender: M', '').strip()
                    gender = 'M' if 'Gender: M' in sublist[-1] else 'F'
                    insert_save(
                        {'Name': name, 'State': state, 'LGA': lga, 'Ward': ward, 'Delim': delim, 'Gender': gender,
                         'DOB': dob, 'VIN': vin, 'PU Code': pu, 'PU Name': pu})
                    print(f"{index}. insert --> {vin}")


def iterate_pdfs_in_folder():
    flag = 0
    for root, dirs, files in os.walk(folder_path):
        for ind, file in enumerate(files):
            if file.endswith(".pdf"):
                print(f'----------------------- {ind + 1}. {file} --------------------------')
                file_path = os.path.join(root, file)
                extract_text_from_pdf(file_path)
                # flag = 1
        #         break
        # if flag == 1:
        #     break



if __name__ == '__main__':
    create_excel()
    iterate_pdfs_in_folder()
