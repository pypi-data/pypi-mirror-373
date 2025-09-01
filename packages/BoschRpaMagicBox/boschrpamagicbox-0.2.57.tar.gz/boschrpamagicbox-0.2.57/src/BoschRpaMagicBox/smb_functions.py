import io
import os
import uuid
import smbclient
import pandas as pd
from smbprotocol.connection import Connection
from smbprotocol.session import Session
from smbprotocol.tree import TreeConnect
from smbprotocol.open import Open
from smbprotocol.file_info import FileInformationClass
from smbprotocol.exceptions import SMBResponseException, NtStatus


def smb_copy_file_local_to_remote(username, password, server_name, share_name, local_file_path, remote_file_path, port=445):
    """ This function is used to copy local file to public folder

    Args:
        username(str): This is the username
        password(str): This is the password
        server_name(str):This is the server name (url), e.g. szh0fs06.apac.bosch.com
        share_name(str): This is the share_name of public folder, e.g. GS_ACC_CN$
        local_file_path(str): This is the local file path
        remote_file_path(str): This is the public file path that file will be saved under share name folder
        port(int): This is the port number of the server name
    """
    connection_cache = {}
    smbclient.register_session(server_name, username=username, password=password, port=port, encrypt=True, connection_cache=connection_cache)

    try:
        with open(local_file_path, 'rb') as local_file:
            with smbclient.open_file(fr'{server_name}/{share_name}/{remote_file_path}', mode='wb', connection_cache=connection_cache) as remote_file:
                remote_file.write(local_file.read())

        print("Copy successfully!")

    except Exception as e:
        print(f"Ops, error is: {e}")
    finally:
        smbclient.reset_connection_cache(connection_cache=connection_cache)


def smb_store_remote_file_by_obj(username, password, server_name, share_name, remote_file_path, file_obj, port=445):
    """ This function is used to store file to public folder

    Args:
        file_obj(io.BytesIO): This is the file object
        username(str): This is the username
        password(str): This is the password
        server_name(str):This is the server name (url), e.g. szh0fs06.apac.bosch.com
        share_name(str): This is the share_name of public folder, e.g. GS_ACC_CN$
        remote_file_path(str): This is the public file path that file will be saved under share name folder
        port(int): This is the port number of the server name
    """
    connection_cache = {}
    smbclient.register_session(server_name, username=username, password=password, port=port, encrypt=True, connection_cache=connection_cache)

    try:
        with smbclient.open_file(fr'{server_name}/{share_name}/{remote_file_path}', mode='wb', connection_cache=connection_cache) as remote_file:
            file_obj.seek(0)
            remote_file.write(file_obj.read())

        print("File is saved successfully!")

    except Exception as e:
        print(f"Ops, error is: {e}")

    finally:
        smbclient.reset_connection_cache(connection_cache=connection_cache)


def smb_check_file_exist(username, password, server_name, share_name, remote_file_path, port=445):
    """ This function is used to check whether remote file is existed

    Args:
        username(str): This is the username
        password(str): This is the password
        server_name(str):This is the server name (url), e.g. szh0fs06.apac.bosch.com
        share_name(str): This is the share_name of public folder, e.g. GS_ACC_CN$
        remote_file_path(str): This is the public file path that file will be saved under share name folder
        port(int): This is the port number of the server name
    """
    connection_cache = {}
    is_file_exist = False
    file_obj = io.BytesIO()
    full_remote_file_path = f'{server_name}/{share_name}/{remote_file_path}'

    smbclient.register_session(server_name, username=username, password=password, port=port, encrypt=True, connection_cache=connection_cache)
    try:
        smbclient.stat(full_remote_file_path, connection_cache=connection_cache)
        is_file_exist = True

        with smbclient.open_file(full_remote_file_path, 'rb', connection_cache=connection_cache) as remote_file:
            file_obj.write(remote_file.read())
            file_obj.seek(0)
        print(f"File {remote_file_path} exist.")

    except Exception as e:
        print(f'Ops, error is {e}')
        print('File with current path does not exist!')
    finally:
        smbclient.reset_connection_cache(connection_cache=connection_cache)

    return is_file_exist, file_obj


def smb_check_folder_exist(username, password, server_name, share_name, remote_folder_path, port=445):
    """ This function is used to check whether remote folder is existed

    Args:
        username(str): This is the username
        password(str): This is the password
        server_name(str):This is the server name (url), e.g. szh0fs06.apac.bosch.com
        share_name(str): This is the share_name of public folder, e.g. GS_ACC_CN$
        remote_folder_path(str): This is the public folder path that folder will be saved under share name folder
        port(int): This is the port number of the server name
    """
    connection_cache = {}
    is_folder_exist = False
    full_remote_folder_path = f'{server_name}/{share_name}/{remote_folder_path}'

    smbclient.register_session(server_name, username=username, password=password, port=port, encrypt=True, connection_cache=connection_cache)
    try:
        # Check if the directory exists
        dir_info = smbclient.stat(full_remote_folder_path, connection_cache=connection_cache)
        if dir_info.st_file_attributes & 0x10:
            is_folder_exist = True
            print("Directory exists.")
        else:
            print("The path exists, but it is not a directory.")

    except Exception as e:
        print(e)
        print('Folder with current path does not exist!')

    finally:
        # Reset connection cache
        smbclient.reset_connection_cache(connection_cache=connection_cache)

    return is_folder_exist


def smb_traverse_remote_folder(username, password, server_name, share_name, remote_folder_path, port=445):
    """ This function is list all files or folders within remote folder

    Args:
        username(str): This is the username
        password(str): This is the password
        server_name(str):This is the server name (url), e.g. szh0fs06.apac.bosch.com
        share_name(str): This is the share_name of public folder, e.g. GS_ACC_CN$
        remote_folder_path(str): This is the public folder path that folder will be saved under share name folder
        port(int): This is the port number of the server name
    """

    traverse_result_list = []
    client_guid = uuid.uuid4()
    connection = Connection(guid=client_guid, server_name=server_name, port=port)
    connection.connect()

    session = Session(connection, username, password)
    session.connect()

    tree = TreeConnect(session, f"\\\\{server_name}\\{share_name}")
    tree.connect()

    folder_open = Open(tree, remote_folder_path)
    folder_open.create(impersonation_level=0,
                       desired_access=0x00000001,  # read only
                       file_attributes=0,
                       share_access=0x00000001,  # allow other process
                       create_disposition=1,  # OPEN_EXISTING
                       create_options=0
                       )
    try:
        pattern = "*"  # match all
        file_information_class = FileInformationClass.FILE_DIRECTORY_INFORMATION
        # file_info = folder_open.query_directory(pattern, file_information_class)

        all_file_info = []
        while True:
            try:
                batch = folder_open.query_directory(pattern, file_information_class)
                if not batch:
                    break
                all_file_info.extend(batch)
            except SMBResponseException as e:
                if e.status == NtStatus.STATUS_NO_MORE_FILES:
                    break
                raise

        for item in all_file_info:
            item_name = item.fields.get('file_name').value.decode('utf-16')
            if item_name not in ['.', '..']:
                creation_time = item.fields.get('creation_time').value
                last_access_time = item.fields.get('last_access_time').value
                last_write_time = item.fields.get('last_write_time').value
                change_time = item.fields.get('change_time').value

                if item.fields.get('file_attributes').value & 0x10:  # check whether item is folder
                    traverse_result_list.append({'name': item_name,
                                                 'is_folder': True, 'is_file': False, 'creation_time': creation_time, 'last_access_time': last_access_time,
                                                 'last_write_time': last_write_time, 'change_time': change_time})
                else:
                    traverse_result_list.append({'name': item_name,
                                                 'is_folder': False, 'is_file': True, 'creation_time': creation_time, 'last_access_time': last_access_time,
                                                 'last_write_time': last_write_time, 'change_time': change_time})
    finally:
        connection.disconnect()
        session.disconnect()
        tree.disconnect()

    return traverse_result_list


def smb_copy_file_remote_to_local(username, password, server_name, share_name, local_file_path, remote_file_path, port=445):
    """ This function is used to copy local file to public folder

    Args:
        username(str): This is the username
        password(str): This is the password
        server_name(str):This is the server name (url), e.g. szh0fs06.apac.bosch.com
        share_name(str): This is the share_name of public folder, e.g. GS_ACC_CN$
        local_file_path(str): This is the local file path
        remote_file_path(str): This is the public file path that file will be saved under share name folder
        port(int): This is the port number of the server name
    """
    connection_cache = {}
    smbclient.register_session(server_name, username=username, password=password, port=port, encrypt=True, connection_cache=connection_cache)

    try:
        with smbclient.open_file(fr'{server_name}/{share_name}/{remote_file_path}', 'rb', connection_cache=connection_cache) as remote_file:
            with open(local_file_path, mode='wb') as local_file:
                local_file.write(remote_file.read())

        print("Copy successfully!")

    except Exception as e:
        print(f"Ops, error is: {e}")
    finally:
        smbclient.reset_connection_cache(connection_cache=connection_cache)


def smb_load_file_obj(username, password, server_name, share_name, remote_file_path, port=445):
    """ This function is used to get file object from public folder

    Args:
        username(str): This is the username
        password(str): This is the password
        server_name(str):This is the server name (url), e.g. szh0fs06.apac.bosch.com
        share_name(str): This is the share_name of public folder, e.g. GS_ACC_CN$
        remote_file_path(str): This is the public file path that file will be saved under share name folder
        port(int): This is the port number of the server name
    """
    connection_cache = {}
    smbclient.register_session(server_name, username=username, password=password, port=port, encrypt=True, connection_cache=connection_cache)

    file_obj = io.BytesIO()
    try:
        with smbclient.open_file(fr'{server_name}/{share_name}/{remote_file_path}', mode='rb', connection_cache=connection_cache) as remote_file:
            file_obj.write(remote_file.read())
            file_obj.seek(0)
        print("Load successfully!")
    except Exception as e:
        print(f"Ops, error is: {e}")
    finally:
        smbclient.reset_connection_cache(connection_cache=connection_cache)

    return file_obj


def smb_delete_file(username, password, server_name, share_name, remote_file_path, port=445):
    """ This function is used to copy local file to public folder

    Args:
        username(str): This is the username
        password(str): This is the password
        server_name(str):This is the server name (url), e.g. szh0fs06.apac.bosch.com
        share_name(str): This is the share_name of public folder, e.g. GS_ACC_CN$
        remote_file_path(str): This is the public file path that file will be saved under share name folder
        port(int): This is the port number of the server name
    """
    connection_cache = {}
    # Register session with SMB server
    smbclient.register_session(server_name, username=username, password=password, port=port, encrypt=True, connection_cache=connection_cache)

    try:
        # Delete the specified remote file
        smbclient.remove(fr'//{server_name}/{share_name}/{remote_file_path}', connection_cache=connection_cache)
        print("File deleted successfully!")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Reset connection cache
        smbclient.reset_connection_cache(connection_cache=connection_cache)


def smb_traverse_delete_file(username, password, server_name, share_name, report_save_path, port=445, exception_str='', need_smbclient=True, connection_cache=None):
    """ This function is used to copy local file to public folder

    Args:
        username(str): This is the username
        password(str): This is the password
        server_name(str):This is the server name (url), e.g. szh0fs06.apac.bosch.com
        share_name(str): This is the share_name of public folder, e.g. GS_ACC_CN$
        port(int): This is the port number of the server name
        report_save_path(str): This is the folder path of save folder
        exception_str(str): This is the string to exclude when file name or folder name contains current string
        need_smbclient(bool): This is the flag to indicate whether to register session with SMB server
        connection_cache(dict): This is the connection cache
    """
    # Register session with SMB server
    if connection_cache is None:
        connection_cache = {}

    if need_smbclient:
        smbclient.register_session(server_name, username=username, password=password, port=port, encrypt=True, connection_cache=connection_cache)

    try:
        except_str_list = [item.upper().strip() for item in exception_str.replace('，', ',').split(',') if item.strip()]
        traverse_result_list = smb_traverse_remote_folder(username, password, server_name, share_name, report_save_path)
        for traverse_item_dict in traverse_result_list:
            item_name = traverse_item_dict['name']
            item_name_upper = item_name.upper()
            if traverse_item_dict['is_folder']:
                if not any(keyword in item_name_upper for keyword in except_str_list):
                    folder_path = f"{report_save_path}/{item_name}"
                    smb_traverse_delete_file(username, password, server_name, share_name, folder_path, port, exception_str, False, connection_cache)
            else:
                if not any(keyword in item_name_upper for keyword in except_str_list):
                    remote_file_path = f"{report_save_path}/{item_name}"
                    try:
                        # Delete the specified remote file
                        smbclient.remove(fr'//{server_name}/{share_name}/{remote_file_path}', connection_cache=connection_cache)
                        print("File deleted successfully!")

                    except Exception as e:
                        print(f"An error occurred: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Reset connection cache
        if need_smbclient:
            smbclient.reset_connection_cache(connection_cache=connection_cache)


def smb_traverse_delete_file_by_keyword(username, password, server_name, share_name, report_save_path, port=445, deletion_keyword='', need_smbclient=True, connection_cache=None):
    """ This function is used to copy local file to public folder

    Args:
        username(str): This is the username
        password(str): This is the password
        server_name(str):This is the server name (url), e.g. szh0fs06.apac.bosch.com
        share_name(str): This is the share_name of public folder, e.g. GS_ACC_CN$
        port(int): This is the port number of the server name
        report_save_path(str): This is the folder path of save folder
        deletion_keyword(str): This is the string to keyword to match file or folder
        need_smbclient(bool): This is the flag to indicate whether to register session with SMB server
        connection_cache(dict): This is the connection cache
    """
    # Register session with SMB server
    if connection_cache is None:
        connection_cache = {}

    if need_smbclient:
        smbclient.register_session(server_name, username=username, password=password, port=port, encrypt=True, connection_cache=connection_cache)

    try:
        keyword_str_list = [item.upper().strip() for item in deletion_keyword.replace('，', ',').split(',') if item.strip()]
        traverse_result_list = smb_traverse_remote_folder(username, password, server_name, share_name, report_save_path)
        for traverse_item_dict in traverse_result_list:
            item_name = traverse_item_dict['name']
            item_name_upper = item_name.upper()
            if traverse_item_dict['is_folder']:
                if any(keyword in item_name_upper for keyword in keyword_str_list):
                    folder_path = f"{report_save_path}/{item_name}"
                    smb_traverse_delete_file_by_keyword(username, password, server_name, share_name, folder_path, port, deletion_keyword, False, connection_cache)
            else:
                if any(keyword in item_name_upper for keyword in keyword_str_list):
                    remote_file_path = f"{report_save_path}/{item_name}"
                    try:
                        # Delete the specified remote file
                        smbclient.remove(fr'//{server_name}/{share_name}/{remote_file_path}', connection_cache=connection_cache)
                        print("File deleted successfully!")

                    except Exception as e:
                        print(f"An error occurred: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Reset connection cache
        if need_smbclient:
            smbclient.reset_connection_cache(connection_cache=connection_cache)


def smb_create_folder(username, password, server_name, share_name, remote_folder_path, port=445):
    """ This function is used to copy local file to public folder

    Args:
        username(str): This is the username
        password(str): This is the password
        server_name(str):This is the server name (url), e.g. szh0fs06.apac.bosch.com
        share_name(str): This is the share_name of public folder, e.g. GS_ACC_CN$
        remote_folder_path(str): This is the public folder path that folder will be created under share name folder
        port(int): This is the port number of the server name
    """
    connection_cache = {}
    # Register session with SMB server
    smbclient.register_session(server_name, username=username, password=password, port=port, encrypt=True, connection_cache=connection_cache)

    try:
        # Create the specified remote directory
        smbclient.makedirs(fr'//{server_name}/{share_name}/{remote_folder_path}', connection_cache=connection_cache, exist_ok=True)
        print("Directory created successfully!")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Reset connection cache
        smbclient.reset_connection_cache(connection_cache=connection_cache)


def smb_delete_folder(username, password, server_name, share_name, remote_folder_path, port=445, connection_cache=None):
    """ This function is used to delete remote folder

    Args:
        username(str): This is the username
        password(str): This is the password
        server_name(str):This is the server name (url), e.g. szh0fs06.apac.bosch.com
        share_name(str): This is the share_name of public folder, e.g. GS_ACC_CN$
        remote_folder_path(str): This is the public folder path that folder will be created under share name folder
        port(int): This is the port number of the server name
        connection_cache(dict): This is the connection cache
    """
    if connection_cache is None:
        connection_cache = {}
    smbclient.register_session(server_name, username=username, password=password, port=port, encrypt=True, connection_cache=connection_cache)
    try:
        # Iterate over the folder contents
        remote_folder_path = f'{server_name}/{share_name}/{remote_folder_path}'
        for entry in smbclient.scandir(remote_folder_path, connection_cache=connection_cache):
            entry_path = f"{remote_folder_path}/{entry.name}"
            if entry.is_dir():
                # Recursively delete subfolders
                smb_delete_folder(username, password, server_name, share_name, entry_path, connection_cache=connection_cache)
            else:
                # Delete files
                smbclient.remove(entry_path, connection_cache=connection_cache)

        # Remove the now-empty folder
        smbclient.rmdir(remote_folder_path, connection_cache=connection_cache)
        print(f"Folder {remote_folder_path} and its contents have been successfully deleted.")
    except FileNotFoundError:
        print(f"Folder {remote_folder_path} does not exist.")
    except OSError as e:
        print(f"Failed to delete folder {remote_folder_path}: {e}")
    finally:
        # Reset connection cache
        smbclient.reset_connection_cache(connection_cache=connection_cache)


def smb_move_remote_file(username, password, from_server_name, from_share_name, from_remote_file_path, to_server_name, to_share_name, to_remote_file_path, port=445):
    """ This function is used to move remote file to another folder

    Args:
        username(str): This is the username
        password(str): This is the password
        from_server_name(str):This is the source server name (url), e.g. szh0fs06.apac.bosch.com
        from_share_name(str): This is the source share_name of public folder, e.g. GS_ACC_CN$
        from_remote_file_path(str): This is the source public file path that file will be saved under share name folder
        to_server_name(str):This is the destination server name (url), e.g. szh0fs06.apac.bosch.com
        to_share_name(str): This is the  destination share_name of public folder, e.g. GS_ACC_CN$
        to_remote_file_path(str): This is the destination new public file path that file will be saved under share name folder
        port(int): This is the port number of the server name
    """

    is_from_file_exist, file_obj = smb_check_file_exist(username, password, from_server_name, from_share_name, from_remote_file_path, port=port)
    if is_from_file_exist:
        smb_store_remote_file_by_obj(username, password, to_server_name, to_share_name, to_remote_file_path, file_obj, port=port)
        smb_delete_file(username, password, from_server_name, from_share_name, from_remote_file_path, port=port)
        print("Move successfully!")
    else:
        print("Source file does not exist!")


def smb_move_remote_folder(username, password, from_server_name, from_share_name, from_remote_folder_path, to_server_name, to_share_name, to_remote_folder_path, port=445):
    """ This function is used to move remote folder to another folder

    Args:
        username(str): This is the username
        password(str): This is the password
        from_server_name(str):This is the source server name (url), e.g. szh0fs06.apac.bosch.com
        from_share_name(str): This is the source share_name of public folder, e.g. GS_ACC_CN$
        from_remote_folder_path(str): This is the source public folder path that folder will be saved under share name folder
        to_server_name(str):This is the destination server name (url), e.g. szh0fs06.apac.bosch.com
        to_share_name(str): This is the  destination share_name of public folder, e.g. GS_ACC_CN$
        to_remote_folder_path(str): This is the destination new public folder path that folder will be saved under share name folder
        port(int): This is the port number of the server name
    """
    is_from_folder_exist = smb_check_folder_exist(username, password, from_server_name, from_share_name, from_remote_folder_path, port=port)
    if is_from_folder_exist:
        smb_create_folder(username, password, to_server_name, to_share_name, to_remote_folder_path, port=port)
        for item in smb_traverse_remote_folder(username, password, from_server_name, from_share_name, from_remote_folder_path, port=port):
            if item['is_folder']:
                smb_move_remote_folder(username, password, from_server_name, from_share_name, f"{from_remote_folder_path}/{item['name']}", to_server_name, to_share_name,
                                       f"{to_remote_folder_path}/{item['name']}", port=port)
            else:
                smb_move_remote_file(username, password, from_server_name, from_share_name, f"{from_remote_folder_path}/{item['name']}", to_server_name, to_share_name,
                                     f"{to_remote_folder_path}/{item['name']}", port=port)
        smb_delete_folder(username, password, from_server_name, from_share_name, from_remote_folder_path, port=port)
        print("Move successfully!")
    else:
        print("Source folder does not exist!")


def smb_copy_remote_file(username, password, from_server_name, from_share_name, from_remote_file_path, to_server_name, to_share_name, to_remote_file_path, port=445):
    """ This function is used to copy remote file to another folder

    Args:
        username(str): This is the username
        password(str): This is the password
        from_server_name(str):This is the source server name (url), e.g. szh0fs06.apac.bosch.com
        from_share_name(str): This is the source share_name of public folder, e.g. GS_ACC_CN$
        from_remote_file_path(str): This is the source public file path that file will be saved under share name folder
        to_server_name(str):This is the destination server name (url), e.g. szh0fs06.apac.bosch.com
        to_share_name(str): This is the  destination share_name of public folder, e.g. GS_ACC_CN$
        to_remote_file_path(str): This is the destination new public file path that file will be saved under share name folder
        port(int): This is the port number of the server name
    """

    is_from_file_exist, file_obj = smb_check_file_exist(username, password, from_server_name, from_share_name, from_remote_file_path, port=port)
    if is_from_file_exist:
        smb_store_remote_file_by_obj(username, password, to_server_name, to_share_name, to_remote_file_path, file_obj, port=port)
        print("Copy successfully!")
    else:
        print("Source file does not exist!")


def smb_copy_remote_folder(username, password, from_server_name, from_share_name, from_remote_folder_path, to_server_name, to_share_name, to_remote_folder_path, port=445):
    """ This function is used to copy remote folder to another folder

    Args:
        username(str): This is the username
        password(str): This is the password
        from_server_name(str):This is the source server name (url), e.g. szh0fs06.apac.bosch.com
        from_share_name(str): This is the source share_name of public folder, e.g. GS_ACC_CN$
        from_remote_folder_path(str): This is the source public folder path that folder will be saved under share name folder
        to_server_name(str):This is the destination server name (url), e.g. szh0fs06.apac.bosch.com
        to_share_name(str): This is the  destination share_name of public folder, e.g. GS_ACC_CN$
        to_remote_folder_path(str): This is the destination new public folder path that folder will be saved under share name folder
        port(int): This is the port number of the server name
    """
    is_from_folder_exist = smb_check_folder_exist(username, password, from_server_name, from_share_name, from_remote_folder_path, port=port)
    if is_from_folder_exist:
        smb_create_folder(username, password, to_server_name, to_share_name, to_remote_folder_path, port=port)
        for item in smb_traverse_remote_folder(username, password, from_server_name, from_share_name, from_remote_folder_path, port=port):
            if item['is_folder']:
                smb_copy_remote_folder(username, password, from_server_name, from_share_name, f"{from_remote_folder_path}/{item['name']}", to_server_name, to_share_name,
                                       f"{to_remote_folder_path}/{item['name']}", port=port)
            else:
                smb_copy_remote_file(username, password, from_server_name, from_share_name, f"{from_remote_folder_path}/{item['name']}", to_server_name, to_share_name,
                                     f"{to_remote_folder_path}/{item['name']}", port=port)
        print("Copy successfully!")
    else:
        print("Source folder does not exist!")


def smb_rename_remote_file(username, password, server_name, share_name, remote_file_path, new_remote_file_path, port=445):
    """ This function is used to rename remote file

    Args:
        username(str): This is the username
        password(str): This is the password
        server_name(str):This is the server name (url), e.g. szh0fs06.apac.bosch.com
        share_name(str): This is the share_name of public folder, e.g. GS_ACC_CN$
        remote_file_path(str): This is the public file path that file will be saved under share name folder
        new_remote_file_path(str): This is the new public file path that file will be saved under share name folder
        port(int): This is the port number of the server name
    """
    connection_cache = {}
    smbclient.register_session(server_name, username=username, password=password, port=port, encrypt=True, connection_cache=connection_cache)

    try:
        # Rename the specified remote file
        smbclient.rename(fr'//{server_name}/{share_name}/{remote_file_path}', fr'//{server_name}/{share_name}/{new_remote_file_path}', connection_cache=connection_cache)
        print("File renamed successfully!")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Reset connection cache
        smbclient.reset_connection_cache(connection_cache=connection_cache)


def smb_rename_remote_folder(username, password, server_name, share_name, remote_folder_path, new_remote_folder_path, port=445):
    """ This function is used to rename remote folder

    Args:
        username(str): This is the username
        password(str): This is the password
        server_name(str):This is the server name (url), e.g. szh0fs06.apac.bosch.com
        share_name(str): This is the share_name of public folder, e.g. GS_ACC_CN$
        remote_folder_path(str): This is the public folder path that folder will be saved under share name folder
        new_remote_folder_path(str): This is the new public folder path that folder will be saved under share name folder
        port(int): This is the port number of the server name
    """
    connection_cache = {}
    smbclient.register_session(server_name, username=username, password=password, port=port, encrypt=True, connection_cache=connection_cache)

    try:
        # Rename the specified remote directory
        smbclient.rename(fr'//{server_name}/{share_name}/{remote_folder_path}', fr'//{server_name}/{share_name}/{new_remote_folder_path}', connection_cache=connection_cache)
        print("Folder renamed successfully!")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Reset connection cache
        smbclient.reset_connection_cache(connection_cache=connection_cache)
