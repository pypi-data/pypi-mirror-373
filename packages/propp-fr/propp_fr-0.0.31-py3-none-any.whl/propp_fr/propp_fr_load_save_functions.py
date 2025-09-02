import os
import csv
import re
import pandas as pd

# Book_NLP_fr - Basic Loading and Saving functions
def load_sacr_file(file_name, files_directory="", extension=".sacr"):
    if not file_name.endswith(extension):
        file_name = file_name + extension

    sacr_file_path = os.path.join(files_directory, file_name)
    with open(sacr_file_path, 'r', encoding='utf-8') as file:
        sacr_content = file.read()  # Read the entire content of the file
    return sacr_content

def load_text_file(file_name, files_directory="", extension=".txt"):
    if not file_name.endswith(extension):
        file_name = file_name + extension

    text_file_path = os.path.join(files_directory, file_name)
    with open(text_file_path, 'r', encoding='utf-8') as file:
        text_content = file.read()  # Read the entire content of the file
    return text_content
def save_text_file(text_content, file_name, files_directory="", extension=".txt"):
    if not file_name.endswith(extension):
        file_name = file_name + extension

    # Ensure the directory exists; if not, create it
    if files_directory and not os.path.exists(files_directory):
        os.makedirs(files_directory)

    text_file_path = os.path.join(files_directory, file_name)

    with open(text_file_path, 'w', encoding='utf-8') as file:
        file.write(text_content)  # Write the text content to the file

def load_tokens_df(file_name, files_directory="", extension=".tokens"):

    if not file_name.endswith(extension):
        file_name = file_name + extension

    tokens_file_path = os.path.join(files_directory, file_name)
    tokens_df = pd.read_csv(tokens_file_path, delimiter='\t', quoting=csv.QUOTE_MINIMAL)
    return tokens_df
def save_tokens_df(tokens_df, file_name, files_directory="", extension=".tokens"):
    # Check if the directory exists, if not, create it
    if not os.path.exists(files_directory):
        os.makedirs(files_directory)
        print(f"Directory '{files_directory}' created.")

    if not file_name.endswith(extension):
        file_name = file_name + extension
    tokens_file_path = os.path.join(files_directory, file_name)

    # Save the DataFrame as a .tokens file
    tokens_df.to_csv(tokens_file_path, sep='\t', index=False, quoting=csv.QUOTE_MINIMAL)

def load_entities_df(file_name, files_directory="", extension=".entities"):

    if not file_name.endswith(extension):
        file_name = file_name + extension

    entities_df_path = os.path.join(files_directory, file_name)
    entities_df = pd.read_csv(entities_df_path, delimiter='\t', quoting=csv.QUOTE_MINIMAL)
    return entities_df
def save_entities_df(entities_df, file_name, files_directory="", extension=".entities"):
    # Check if the directory exists, if not, create it
    if not os.path.exists(files_directory):
        os.makedirs(files_directory)
        print(f"Directory '{files_directory}' created.")

    if not file_name.endswith(extension):
        file_name = file_name + extension
    entities_file_path = os.path.join(files_directory, file_name)

    # Save the DataFrame as a .tokens file
    entities_df.to_csv(entities_file_path, sep='\t', index=False, quoting=csv.QUOTE_MINIMAL)

def clean_text(raw_text):
    raw_text = re.sub(r'�', ' ', raw_text)
    raw_text = re.sub(r'■', ' ', raw_text)
    raw_text = re.sub(r'•', ' ', raw_text)
    raw_text = raw_text.replace("”", '"')
    raw_text = raw_text.replace("“", '"')
    raw_text = raw_text.replace("’", "'")
    raw_text = raw_text.replace("' ", "'")
    raw_text = raw_text.replace(" , ", ", ")
    raw_text = raw_text.replace("\xa0", " ")
    # Replace multiple spaces (but not newlines) with a single space
    raw_text = re.sub(r'(?<=\S) {2,}(?=\S)', ' ', raw_text)
    raw_text = re.sub(r'[–—―‒]', '-', raw_text)
    raw_text = raw_text.replace(".-", ". -")
    raw_text = raw_text.replace("!-", "! -")
    raw_text = raw_text.replace("?-", "? -")
    return raw_text
