from io import BytesIO

import pymysql
import traceback
import pandas as pd

from .smb_functions import smb_store_remote_file_by_obj


def start_mysql_server_connection(mysql_host, mysql_port, mysql_user, mysql_password, mysql_database_name):
    """ This function is used to connect to the MySQL server.

    Args:
        mysql_host(str): The host of the MySQL server.
        mysql_port(int): The port of the MySQL server.
        mysql_user(str): The user of the MySQL server.
        mysql_password(str): The password of the MySQL server.
        mysql_database_name(str): The database of the MySQL server.

    """
    connection = pymysql.connect(
        host=mysql_host,
        port=mysql_port,
        user=mysql_user,
        password=mysql_password,
        database=mysql_database_name,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    print('MySQL connection is ready!')
    return connection


def close_mysql_server_connection(connection):
    """ This function is used to close the MySQL server connection.

    Args:
        connection(pymysql.connections.Connection): The MySQL server connection.
    """
    if connection:
        connection.close()
        print("MySQL connection is closed!")
    else:
        print("No MySQL connection to close!")


def execute_mysql_query(connection, sql_query, sql_query_params=None):
    """ This function is used to execute a MySQL query.

    Args:
        connection(pymysql.connections.Connection): The MySQL server connection.
        sql_query(str): The SQL query to execute.
        sql_query_params(tuple): The parameters for the SQL query.

    """
    try:
        with connection.cursor() as cursor:
            if sql_query_params is not None:
                cursor.execute(sql_query, sql_query_params)
            else:
                cursor.execute(sql_query)
            results = cursor.fetchall()
            cursor.close()
            return results
    except:
        print(f"Error executing query: {traceback.format_exc()}")
        return None


def fetch_data_from_mysql_server(mysql_host, mysql_port, mysql_user, mysql_password, mysql_database_name, sql_query, sql_query_params):
    """

    Args:
        mysql_host(str): The host of the MySQL server.
        mysql_port(int): The port of the MySQL server.
        mysql_user(str): The user of the MySQL server.
        mysql_password(str): The password of the MySQL server.
        mysql_database_name(str): The database of the MySQL server.
        sql_query(str): The SQL query to execute.
        sql_query_params(tuple): The parameters for the SQL query.

    """
    connection = None
    try:
        connection = start_mysql_server_connection(mysql_host, mysql_port, mysql_user, mysql_password, mysql_database_name)
        if connection:
            results = execute_mysql_query(connection, sql_query, sql_query_params)
            # close_mysql_server_connection(connection)
            return results
        else:
            print("Failed to connect to MySQL server.")
            return None
    except:
        print(f"Error connecting to MySQL server:\n{traceback.format_exc()}")
        # close_mysql_server_connection(connection)
        return None


def save_mysql_data_to_excel(mysql_host, mysql_port, mysql_user, mysql_password, mysql_database_name, sql_query, username, password, server_name, share_name, remote_file_path,
                             port=445, sheet_name='Sheet1', sql_query_params=None):
    """
    This function is used to save MySQL data to an Excel file.

    Args:
        mysql_host(str): The host of the MySQL server.
        mysql_port(int): The port of the MySQL server.
        mysql_user(str): The user of the MySQL server.
        mysql_password(str): The password of the MySQL server.
        mysql_database_name(str): The database of the MySQL server.
        sql_query(str): The SQL query to execute.
        username(str): This is the username
        password(str): This is the password
        server_name(str):This is the server name (url), e.g. szh0fs06.apac.bosch.com
        share_name(str): This is the share_name of public folder, e.g. GS_ACC_CN$
        remote_file_path(str): This is the public file path that file will be saved under share name folder
        port(int): This is the port number of the server name
        sheet_name(str): The name of the sheet in the Excel file.
        sql_query_params(tuple): The parameters for the SQL query.

    """
    try:
        fetch_data = fetch_data_from_mysql_server(mysql_host, mysql_port, mysql_user, mysql_password, mysql_database_name, sql_query, sql_query_params)
        if fetch_data is not None:
            df_data = pd.DataFrame(fetch_data)
            file_obj = BytesIO()

            with pd.ExcelWriter(file_obj, engine='xlsxwriter') as writer:
                df_data.to_excel(writer, index=False, sheet_name=sheet_name)
            file_obj.seek(0)

            smb_store_remote_file_by_obj(username, password, server_name, share_name, remote_file_path, file_obj, port)
        else:
            print("No data fetched from MySQL server.")
    except:
        print(f"Error saving MySQL data to Excel:\n{traceback.format_exc()}")
