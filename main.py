import argparse
import os
import json
import re
from pprint import pprint
import pandas as pd


def process_line(line):
    data = {}
    float_count = 0
    string_count = 0
    null_count = 0
    for attribute in line:
        # Strip leading/trailing spaces
        attribute = attribute.strip()

        if attribute.replace('.', '', 1).isdigit() and attribute.count('.') <= 1:
            data[f'number_{float_count}'] = float(attribute)
            float_count += 1
        elif attribute:  # Non-empty strings
            data[f'text_{string_count}'] = attribute
            string_count += 1
        else:
            data[f'null_{null_count}'] = 'Null'
            null_count += 1

    return data


def check_same_attributes(mapped_lines):
    """
    Check if all dictionaries in the list have the same amount of attributes.
    """
    if not mapped_lines:
        print("The list is empty. No dictionaries to compare.")
        return

    seen_keys = {}

    for data in mapped_lines:
        key_set = len(data.keys())
        seen_keys[key_set] = seen_keys.get(key_set, 0) + 1

    print("Unique key sets and their counts:")
    pprint(seen_keys)

    if len(seen_keys) == 1:
        print("All dictionaries have the same attributes.")
    else:
        print("Dictionaries have different attributes.")


def write_to_json(data, output_dir, name):
    """
    Write processed data to a JSON file.
    """
    ensure_folder_exists(output_dir)
    output_path = os.path.join(output_dir, f"{name}.json")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)


def split_list(input_list, chunk_size):
    """
    Splits a list into smaller lists of a given chunk size.

    Args:
        input_list (list): The list to be split.
        chunk_size (int): The size of each smaller list.

    Returns:
        list: A list of smaller lists.
    """
    return [input_list[i:i + chunk_size] for i in range(0, len(input_list), chunk_size)]


def find_divisors(number):
    """
    Finds all divisors of a given number.

    Args:
        number (int): The number for which divisors are to be found.

    Returns:
        list: A list of all divisors of the number.
    """
    if number <= 0:
        raise ValueError("The number must be positive.")
    return [i for i in range(1, number + 1) if number % i == 0]


def ensure_folder_exists(folder_path):
    if not os.path.exists(folder_path):
        print(f"Folder does not exist. Creating: {folder_path}")
        os.makedirs(folder_path)


def save_to_excel(mapped_lines, output_dir, name):
    # Convert the processed data to a DataFrame
    df = pd.DataFrame(mapped_lines)
    df = df.loc[:, ~df.columns.str.contains('null', case=False)]

    ensure_folder_exists(output_dir)

    # Save the DataFrame to an Excel file
    output_path = os.path.join(output_dir, f"{name}.xlsx")
    df.to_excel(output_path, index=False)

    print(f"Processed data saved to {output_path}")


def split_by_semicolon(file_path, output_dir, suspects):
    """
    Process a semicolon-delimited file and save the result as a JSON file.
    """
    name = os.path.splitext(os.path.basename(file_path))[0]
    print(f'\n\nProcessing file: {name}')
    try:
        with open(file_path, 'r') as file:
            sql_content = file.read()

        attributes = sql_content.split(';')

        divisors = find_divisors(len(attributes) - 1)

        chunks = divisors[len(divisors) // 2]
        if name in suspects.keys():
            chunks = suspects[name]
            if chunks not in divisors:
                print(f'{chunks} is not a divisor for {len(attributes) - 1}')

        lines = split_list(attributes, chunks)
        mapped_lines = list(map(process_line, lines))
        check_same_attributes(mapped_lines)

        # write_to_json(mapped_lines, output_dir, name)
        save_to_excel(mapped_lines, output_dir, name)

    except Exception as e:
        print(f"Error processing file {file_path}: {e}")


def split_by_dot(file_path, output_dir):
    name = os.path.splitext(os.path.basename(file_path))[0]
    print(f'\n\nProcessing file: {name}')
    try:
        with open(file_path, 'r') as file:
            sql_content = file.read()

        lines = sql_content.split(';.')
        lines = [line.split(';') for line in lines]

        mapped_lines = list(map(process_line, lines))
        check_same_attributes(mapped_lines)
        # write_to_json(mapped_lines, output_dir, name)
        save_to_excel(mapped_lines, output_dir, name)

    except Exception as e:
        print(f"Error processing file {file_path}: {e}")


def process_folder(folder_path, output_dir):
    """
    Process all SQL files in a folder and save their processed data as JSON.
    """
    suspects = {
        'barrios': 8,
        'notlog': 12,
        'prog': 10,
        'mat': 24,
        'defhora': 43,
        'derprofe': 72,
        'dianot': 110,
        'HOJAMA': 172
    }
    if not os.path.exists(folder_path):
        print(f"Folder does not exist: {folder_path}")
        return

    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)

        if os.path.isfile(file_path) and file_name.lower().endswith('.sql'):
            split_by_dot(file_path, output_dir)
            # split_by_semicolon(file_path, output_dir, suspects)


if __name__ == "__main__":

    # Append the name of the downloaded and decompressed zip file
    closures_downloaded = [
        '12013',
        '21998',
        '12022'
    ]
    for closure in closures_downloaded:

        #  Replace with your actual route
        input_folder = rf"D:\Projects\Akros\alzate.edu.co\{closure}\{closure}"
        output_folder = rf"D:\Projects\Akros\alzate.edu.co\{closure}\output"

        process_folder(input_folder, output_folder)

