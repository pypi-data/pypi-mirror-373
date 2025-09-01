import os
import subprocess
import traceback
from io import StringIO, BytesIO
from time import sleep
from typing import Union
import pdfplumber

import pandas as pd
import pyperclip

from .helper_functions import create_error_log
from .smb_functions import smb_load_file_obj, smb_store_remote_file_by_obj


def strip_str_column(pd_data: pd.DataFrame, str_column_list: list, upper_column: list = None):
    """This function is used to strip columns in str type

    Args:
        upper_column(list): This is the dict that indicates which column need to be transferred into upper format
        pd_data(pd.DataFrame): This is the instance of pandas DataFrame data
        str_column_list(list):This is the list of column in str type

    Returns:
        pd.DataFrame: pd_data
    """
    if upper_column is None:
        upper_column = []
    if not pd_data.empty:
        for column in str_column_list:
            pd_data[column] = pd_data[column].str.strip()
            if column in upper_column:
                pd_data[column] = pd_data[column].str.upper()
    return pd_data


def load_excel_data(file_path: str, sheet_name: str, upper_column_list: list, header: int = 0, to_dict: bool = False, data_index: str = '',
                    replace_na: bool = False, replace_na_value: str = '', used_cols: list = None, auto_locate_header: bool = False,
                    key_header_column: str = ''):
    """This function is used to transform config data into target format

    Args:
        auto_locate_header(bool): This indicates whether to locate the row index of header row
        key_header_column(str): This is the column which will be used to locate header row
        replace_na(bool): Whether to replace na value with given value
        replace_na_value(str): This is the value to fill na range
        header(int): This is the header number of DataFrame data
        file_path(str): This is the file path of Excel file
        sheet_name(str): This is the name of sheet that contains data
        upper_column_list(list): This is the columns whose values need to be in upper format
        to_dict(bool): This is the flag whether transfer data into dict format
        data_index(str): This is the column that will be index column when data need to be transferred into dict format
        used_cols(list): This is the list of column names which will be used for usecols parameter
    """
    target_data = pd.DataFrame()
    is_loop = True
    while is_loop:
        try:
            if sheet_name:
                target_data = pd.read_excel(file_path, sheet_name=sheet_name, dtype=str, header=header, usecols=used_cols)
            else:
                target_data = pd.read_excel(file_path, dtype=str, header=header, usecols=used_cols)
            is_loop = False
        except ValueError:
            sleep(2)

    if auto_locate_header:
        target_header_index = 0
        for row_index in target_data.index:
            row_data = target_data.loc[row_index]
            if key_header_column in row_data.values:
                target_header_index = row_index + 1
                break

        if sheet_name:
            target_data = pd.read_excel(file_path, sheet_name=sheet_name, dtype=str, header=target_header_index, usecols=used_cols)
        else:
            target_data = pd.read_excel(file_path, dtype=str, header=target_header_index, usecols=used_cols)

    if replace_na:
        target_data.fillna(replace_na_value, inplace=True)

    target_data = strip_str_column(target_data, target_data.columns, upper_column_list)
    if to_dict:
        target_data = target_data[target_data[data_index] != '']
        target_data.set_index(data_index, inplace=True)
        target_data = target_data.to_dict(orient='index')
    return target_data


def load_sap_text_data(file_path: str, dtype: Union[dict, type], key_word: str, remove_unname: bool = True, replace_na: bool = False,
                       replace_na_value: str = '', error_log_folder_path: str = ''):
    """This function is used to load data from txt file

    Args:
        replace_na(bool): This indicates whether to fill NAN value
        replace_na_value(str): This is the value to fill NAN value
        file_path(str): This is the text file path
        dtype(dict | type): This is dtype which will be read as string
        key_word(str): This is the key word to locate column header
        remove_unname(bool): This is the flag whether delete column with 'Unname'
        error_log_folder_path(str): This is the path to record error log

    Returns:
        dict: load_result
    """
    load_result = {'sap_text_data': None, 'has_sap_text_data': False}

    with open(file_path, 'r', encoding='utf-8') as file:
        doc = file.readlines()
        index = 0
        row_length = 0
        text_index = 0
        is_text = False
        for line in doc:
            if key_word in line:
                doc[index] = '\t'.join([i.strip() for i in line.split('\t')])
                row_length = len(doc[index].split('\t'))
                if 'Text' in doc[index].split('\t'):
                    text_index = doc[index].split('\t').index('Text')
                    is_text = True
                if not is_text and 'Document Header Text' in doc[index].split('\t'):
                    text_index = doc[index].split('\t').index('Document Header Text')
                    is_text = True
                break
            index += 1

        if is_text:
            for index, value in enumerate(doc):
                value_list = value.split('\t')
                value_length = len(value_list)
                if value_length > row_length:
                    for j in range(value_length - row_length):
                        value_list[text_index] += value_list[text_index + 1]
                        del value_list[text_index + 1]
                    doc[index] = '\t'.join(value_list)

        doc = '\n'.join(doc)

        for i in range(100):
            try:
                sap_text_data = pd.read_csv(StringIO(doc), dtype=dtype, sep='\t', header=i, quoting=3, low_memory=False)
                sap_text_data_column_list = [str(column).strip() for column in sap_text_data.columns]
                if key_word in sap_text_data_column_list:
                    sap_text_data_column_dict = {column: str(column).strip() for column in sap_text_data.columns}
                    sap_text_data.rename(columns=sap_text_data_column_dict, inplace=True)
                    if remove_unname:
                        sap_text_data_columns = [i for i in sap_text_data.columns if 'Unnamed' not in str(i)]
                        sap_text_data = sap_text_data.loc[:, sap_text_data_columns]
                    if type(dtype) == dict:
                        for column, column_type in dtype.items():
                            if column_type == str:
                                sap_text_data[column] = sap_text_data[column].str.strip()
                    elif dtype == str:
                        for column in sap_text_data.columns:
                            sap_text_data[column] = sap_text_data[column].str.strip()

                    if replace_na:
                        sap_text_data.fillna(replace_na_value, inplace=True)

                    load_result['sap_text_data'] = sap_text_data
                    load_result['has_sap_text_data'] = True
                    break
                else:
                    pass
            except:
                if error_log_folder_path:
                    print(traceback.format_exc())
                    create_error_log(error_log_folder_path, traceback.format_exc())
                pass
    return load_result


def open_sap_with_system_code(system_code: str):
    """This function is used to open sap with system code

    Args:
        system_code(str): POE,PRP ....
    """
    os.system(f'start sapshcut -system={system_code}')


def check_file_download_status(save_folder_path: str, file_name: str):
    """This function is used to check whether file has been downloaded successfully

    Args:
        file_name(str): This is the file name of file that will be saved in save folder
        save_folder_path(str): This is the folder path of save folder
    """
    save_file_path = save_folder_path + os.sep + file_name
    sleep(4)
    is_loop = True
    while is_loop:
        for current_file_name in os.listdir(save_folder_path):
            current_save_file_path = save_folder_path + os.sep + current_file_name
            if os.path.getsize(current_save_file_path) != 0 and file_name.upper().strip() in current_file_name.upper().strip():
                try:
                    os.rename(save_folder_path + os.sep + current_file_name, save_file_path)
                except:
                    pass
                else:
                    is_loop = False
                    break
        sleep(4)


def check_done_indicators_complete(done_file_path: str, key_word: str, wait_time: int = 30):
    """This function is used to check whether all data has been downloaded

    Args:
        done_file_path(str): This is the done file path
        key_word(str): This is the key word to show type
        wait_time(int): This is the wait time duration for checking whether sap data downloaded

    """
    if not os.path.exists(done_file_path):
        print(key_word)
        print(
            f'Wait {wait_time} seconds and will continue to check whether related done file has been downloaded.')
        sleep(wait_time)
        check_done_indicators_complete(done_file_path, key_word, wait_time)
    else:
        return True


def generate_multiple_input_sap_script(multiple_input_list: list, script_header: str = '// Multiple Selection for Company code',
                                       set_value_script: str = '  Set cell[Table,Single value,'):
    """This function is used to generate sap scripts for multiple input of company codes, document number and so on

    Args:
        script_header(str): This is the script header for script function description
        set_value_script(str): This is the set value part sap script
        multiple_input_list(list): This is the list of multiple input values
    """
    start_index = 1
    multiple_input_script_list = [
        f'{script_header}\n', 'Screen SAPLALDB.3000\n']
    for multiple_input in multiple_input_list:
        multiple_input_script_list.append(f'{set_value_script}{start_index}]    	"{multiple_input}"\n')

        if start_index % 7 == 1 and start_index == 8:
            multiple_input_script_list.append('Enter "/82"\n')
            multiple_input_script_list.append(f'{script_header}\n')
            multiple_input_script_list.append('Screen SAPLALDB.3000\n')
            start_index = 1

        start_index += 1
    multiple_input_script_list.append('  Enter "/8"\n')
    return multiple_input_script_list


def collect_table_from_pdf_page(tables, table_index, first_column_name, find_first_row=False, table_header_dict=None, pdf_table_dict=None, extract_all_tables=False):
    """ This function is used to extract tables from a PDF file.
    Args:
        tables(list): A list of tables extracted from the PDF file. Each table is a list of lists.
        table_index(int): The index of the table to be extracted.
        first_column_name(str): The name of the first column to be used for locating first row.
        extract_all_tables(bool): If True, extract all tables from the specified page. Defaults to False.
        find_first_row(bool): If True, find the first row based on the first column name. Defaults to False.
        table_header_dict(dict): A dictionary to store the header of the table. Defaults to None.
        pdf_table_dict(dict): A dictionary to store the extracted table data. Defaults to None.
    """
    if pdf_table_dict is None:
        pdf_table_dict = {}

    if table_header_dict is None:
        table_header_dict = {}

    is_normal_table = True
    for table in tables:
        if not (isinstance(table, list) and all(isinstance(row, list) for row in table)):
            is_normal_table = False
            break

    if is_normal_table:
        if not extract_all_tables:
            tables = [tables[table_index - 1]]
    else:
        tables = [tables]
    for table in tables:
        for row in table:
            if row and row[0] == first_column_name and not find_first_row:
                for column_index, column_name in enumerate(row):
                    pdf_table_dict[column_name] = []
                    table_header_dict[column_index] = column_name
                find_first_row = True
                continue
            if find_first_row and row[0] != first_column_name:
                for column_index, column_value in enumerate(row):
                    if column_index in table_header_dict:
                        pdf_table_dict[table_header_dict[column_index]].append(column_value)

    return pdf_table_dict, find_first_row, table_header_dict


def collect_tables_from_pdf_file(user_name, password, server_name, share_name, pdf_file_path, port, page_number=1, table_index=1, first_column_name='', extract_all_pages=False,
                                 extract_all_tables=False):
    """
    Check whether the tables on the given page of a PDF file are in standard 2D list format.

    Args:
        pdf_file_path (str or file-like): Path to PDF file, or a file-like object (e.g. BytesIO).
        page_number (int): The page number to check (1-based). Defaults to 1.
        table_index(int): The index of the table to be extracted
        first_column_name(str): The name of the first column to be used for locating first row.
        extract_all_pages(bool): If True, extract tables from all pages. Defaults to False.
        extract_all_tables(bool): If True, extract all tables from the specified page. Defaults to False.
        user_name(str): Username for accessing the file.
        password(str): Password for accessing the file.
        server_name(str): Server name (URL) where the file is located, e.g. szh0fs06.apac.bosch.com.
        share_name(str): Share name of the public folder, e.g. GS_ACC_CN$.
        port(int): Port number of the server, default is 445.


    Returns:
        pdf_table_df (pd.Dataframe): A DataFrame containing the extracted table data.
    """
    find_first_row = False
    table_header_dict = {}
    pdf_table_dict = {}
    page_number = int(page_number)

    pdf_obj = smb_load_file_obj(user_name, password, server_name, share_name, pdf_file_path, port)

    with pdfplumber.open(pdf_obj) as pdf:
        if page_number < 1 or page_number > len(pdf.pages):
            return None

        if not extract_all_pages:
            page = pdf.pages[page_number - 1]
            tables = page.extract_tables()
            pdf_table_dict, *_ = collect_table_from_pdf_page(tables, table_index, first_column_name, find_first_row, table_header_dict, pdf_table_dict, extract_all_tables)
            table_df = pd.DataFrame(pdf_table_dict)

        else:
            for page in pdf.pages:
                tables = page.extract_tables()
                pdf_table_dict, find_first_row, *_ = collect_table_from_pdf_page(tables, table_index, first_column_name, find_first_row, table_header_dict, pdf_table_dict,
                                                                                 extract_all_tables)
            table_df = pd.DataFrame(pdf_table_dict)
        return table_df


def save_pdf_table_into_excel(user_name, password, server_name, share_name, port, pdf_file_path, page_number, table_index, first_column_name, save_column_names, excel_file_path,
                              sheet_name='Sheet1', extract_all_pages=False, extract_all_tables=False):
    """
    Save the extracted table from a PDF file into an Excel file.

    Args:
        pdf_file_path (str): Path to the PDF file.
        page_number (int): The page number to extract the table from.
        table_index (int): The index of the table to extract.
        first_column_name (str): The name of the first column to locate the first row.
        save_column_names(str): List of column names to save in the Excel file.
        excel_file_path (str): Path to save the Excel file.
        sheet_name(str): Name of the sheet in the Excel file. Default is 'Sheet1'.
        user_name(str): Username for accessing the file.
        password(str): Password for accessing the file.
        server_name(str): Server name (URL) where the file is located, e.g. szh0fs06.apac.bosch.com.
        share_name(str): Share name of the public folder, e.g. GS_ACC_CN$.
        port(int): Port number of the server, default is 445.
        extract_all_pages(bool): If True, extract tables from all pages. Defaults to False.
        extract_all_tables(bool): If True, extract all tables from the specified page. Defaults to False.
    """
    if not sheet_name:
        sheet_name = 'Sheet1'
    pdf_table_df = collect_tables_from_pdf_file(user_name, password, server_name, share_name, pdf_file_path, port, page_number, table_index, first_column_name, extract_all_pages,
                                                extract_all_tables)

    save_column_name_list = save_column_names.replace('，', ',').split(',')
    save_column_name_list = [name.strip() for name in save_column_name_list if name.strip()]
    if save_column_name_list:
        pdf_table_df = pdf_table_df.loc[:, save_column_name_list]

    file_obj = BytesIO()

    with pd.ExcelWriter(file_obj, engine='xlsxwriter') as writer:
        pdf_table_df.to_excel(writer, sheet_name=sheet_name, index=False, float_format='%.2f')

    file_obj.seek(0)
    smb_store_remote_file_by_obj(user_name, password, server_name, share_name, excel_file_path, file_obj, port)


def save_excel_data_into_text(user_name, password, server_name, share_name, port, excel_file_path, text_file_path, sheet_name='Sheet1', save_column_names='', keep_header=True):
    """ Save specified columns from an Excel sheet into a text file.

    Args:
        excel_file_path(str): Path to the Excel file.
        sheet_name(str): Name of the sheet to read from. Default is 'Sheet1'.
        save_column_names(str): Comma-separated list of column names to save. If empty, all columns are saved.
        text_file_path(str): Path to save the text file.
        user_name(str): Username for accessing the file.
        password(str): Password for accessing the file.
        server_name(str): Server name (URL) where the file is located, e.g. szh0fs06.apac.bosch.com.
        share_name(str): Share name of the public folder, e.g. GS_ACC_CN$.
        port(int): Port number of the server, default is 445.
        keep_header(bool): Whether to keep the header in the text file. Default is True.
    """
    if not sheet_name:
        sheet_name = 'Sheet1'

    save_column_name_list = save_column_names.replace('，', ',').split(',')
    save_column_name_list = [name.strip() for name in save_column_name_list if name.strip()]

    excel_file_obj = smb_load_file_obj(user_name, password, server_name, share_name, excel_file_path, port)
    excel_data = pd.read_excel(excel_file_obj, sheet_name=sheet_name, dtype=str)
    if save_column_name_list:
        excel_data = excel_data.loc[:, save_column_name_list]

    file_obj = BytesIO()

    excel_data.to_csv(file_obj, index=False, sep='\t', header=keep_header, encoding='utf-8')
    file_obj.seek(0)

    smb_store_remote_file_by_obj(user_name, password, server_name, share_name, text_file_path, file_obj, port)
