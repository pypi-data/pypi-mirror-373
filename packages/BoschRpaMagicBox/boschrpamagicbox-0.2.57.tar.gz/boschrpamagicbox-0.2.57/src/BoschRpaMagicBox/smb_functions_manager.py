import io
import uuid
import smbclient
from smbprotocol.connection import Connection
from smbprotocol.session import Session
from smbprotocol.tree import TreeConnect
from smbprotocol.open import Open
from smbprotocol.file_info import FileInformationClass
from smbprotocol.exceptions import SMBResponseException, NtStatus


class SmbFunctionsManager:

    def __init__(self, username, password, server_name, share_name, port=445, encrypt=True):
        self.username = username
        self.password = password
        self.server_name = server_name
        self.share_name = share_name
        self.port = port
        self.encrypt = encrypt
        self.connection_cache = {}

    def __enter__(self):
        self.initialize_smb_connection()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_smb_connection()

    def __del__(self):
        try:
            self.close_smb_connection()
        except Exception:
            # ignore all errors during object finalization
            pass

    def close_smb_connection(self):
        """Safely close SMB connection without raising confusing warnings."""
        cache = getattr(self, "connection_cache", None)

        # If cache is None, nothing to do
        if cache is None:
            return

        # Reset the connection cache if the function is available
        if hasattr(smbclient, "reset_connection_cache") and cache:
            try:
                smbclient.reset_connection_cache(connection_cache=cache)
            except Exception:
                # ignore all errors during connection reset
                pass

        # Clear the reference to the connection cache
        self.connection_cache = None

    def initialize_smb_connection(self):
        """ This function is used to initialize smb connection
        """
        smbclient.register_session(self.server_name, username=self.username, password=self.password, port=self.port, encrypt=self.encrypt,
                                   connection_cache=self.connection_cache)

    def prepare_server_name_share_name(self, server_name, share_name):
        """ This function is used to prepare server name and share name
        """
        if not server_name:
            server_name = self.server_name
        if not share_name:
            share_name = self.share_name
        return server_name, share_name

    def smb_copy_file_local_to_remote(self, local_file_path, remote_file_path, server_name=None, share_name=None):
        """ This function is used to copy local file to public folder

        Args:
            local_file_path(str): This is the local file path
            remote_file_path(str): This is the public file path that file will be saved under share name folder
            server_name(str):This is the  server name (url), e.g. szh0fs06.apac.bosch.com
            share_name(str): This is the  share_name of public folder, e.g. GS
        """
        server_name, share_name = self.prepare_server_name_share_name(server_name, share_name)

        try:
            with open(local_file_path, 'rb') as local_file:
                with smbclient.open_file(fr'{server_name}/{share_name}/{remote_file_path}', mode='wb', connection_cache=self.connection_cache) as remote_file:
                    remote_file.write(local_file.read())

            print("Copy successfully!")

        except Exception as e:
            print(f"Ops, error is: {e}")

    def smb_store_remote_file_by_obj(self, remote_file_path, file_obj, server_name=None, share_name=None):
        """ This function is used to store file to public folder

        Args:
            file_obj(io.BytesIO): This is the file object
            remote_file_path(str): This is the public file path that file will be saved under share name folder
            server_name(str):This is the  server name (url), e.g. szh0fs06.apac.bosch.com
            share_name(str): This is the  share_name of public folder, e.g. GS
        """
        server_name, share_name = self.prepare_server_name_share_name(server_name, share_name)

        try:
            with smbclient.open_file(fr'{server_name}/{share_name}/{remote_file_path}', mode='wb', connection_cache=self.connection_cache) as remote_file:
                file_obj.seek(0)
                remote_file.write(file_obj.read())

            print("File is saved successfully!")

        except Exception as e:
            print(f"Ops, error is: {e}")

    def smb_check_file_exist(self, remote_file_path, server_name=None, share_name=None):
        """ This function is used to check whether remote file is existed

        Args:
            server_name(str):This is the  server name (url), e.g. szh0fs06.apac.bosch.com
            share_name(str): This is the  share_name of public folder, e.g. GS_ACC_CN$
            remote_file_path(str): This is the public file path that file will be saved under share name folder
        """
        server_name, share_name = self.prepare_server_name_share_name(server_name, share_name)

        is_file_exist = False
        file_obj = io.BytesIO()
        full_remote_file_path = f'{server_name}/{share_name}/{remote_file_path}'

        try:
            smbclient.stat(full_remote_file_path, connection_cache=self.connection_cache)
            is_file_exist = True

            with smbclient.open_file(full_remote_file_path, 'rb', connection_cache=self.connection_cache) as remote_file:
                file_obj.write(remote_file.read())
                file_obj.seek(0)
            print(f"File {remote_file_path} exist.")

        except Exception as e:
            print(f'Ops, error is {e}')
            print('File with current path does not exist!')

        return is_file_exist, file_obj

    def smb_check_folder_exist(self, remote_folder_path, server_name=None, share_name=None):
        """ This function is used to check whether remote folder is existed

        Args:
            remote_folder_path(str): This is the public folder path that folder will be saved under share name folder
            server_name(str):This is the  server name (url), e.g. szh0fs06.apac.bosch.com
            share_name(str): This is the  share_name of public folder, e.g. GS
        """
        server_name, share_name = self.prepare_server_name_share_name(server_name, share_name)

        is_folder_exist = False
        full_remote_folder_path = f'{server_name}/{share_name}/{remote_folder_path}'

        try:
            # Check if the directory exists
            dir_info = smbclient.stat(full_remote_folder_path, connection_cache=self.connection_cache)
            if dir_info.st_file_attributes & 0x10:
                is_folder_exist = True
                print("Directory exists.")
            else:
                print("The path exists, but it is not a directory.")

        except Exception as e:
            print(e)
            print('Folder with current path does not exist!')

        return is_folder_exist

    def smb_traverse_remote_folder(self, remote_folder_path, server_name=None, share_name=None):
        """ This function is list all files or folders within remote folder

        Args:
            remote_folder_path(str): This is the public folder path that folder will be saved under share name folder
            server_name(str):This is the  server name (url), e.g. szh0fs06.apac.bosch.com
            share_name(str): This is the  share_name of public folder, e.g. GS
        """
        server_name, share_name = self.prepare_server_name_share_name(server_name, share_name)

        traverse_result_list = []
        client_guid = uuid.uuid4()
        connection = Connection(guid=client_guid, server_name=server_name, port=self.port)
        connection.connect()

        session = Session(connection, self.username, self.password)
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

    def smb_copy_file_remote_to_local(self, local_file_path, remote_file_path, server_name=None, share_name=None):
        """ This function is used to copy local file to public folder

        Args:
            local_file_path(str): This is the local file path
            remote_file_path(str): This is the public file path that file will be saved under share name folder
            server_name(str):This is the  server name (url), e.g. szh0fs06.apac.bosch.com
            share_name(str): This is the  share_name of public folder, e.g. GS
        """
        server_name, share_name = self.prepare_server_name_share_name(server_name, share_name)

        try:
            with smbclient.open_file(fr'{server_name}/{share_name}/{remote_file_path}', 'rb', connection_cache=self.connection_cache) as remote_file:
                with open(local_file_path, mode='wb') as local_file:
                    local_file.write(remote_file.read())

            print("Copy successfully!")

        except Exception as e:
            print(f"Ops, error is: {e}")

    def smb_load_file_obj(self, remote_file_path, server_name=None, share_name=None):
        """ This function is used to get file object from public folder

        Args:
            remote_file_path(str): This is the public file path that file will be saved under share name folder
            server_name(str):This is the  server name (url), e.g. szh0fs06.apac.bosch.com
            share_name(str): This is the  share_name of public folder, e.g. GS
        """
        server_name, share_name = self.prepare_server_name_share_name(server_name, share_name)

        file_obj = io.BytesIO()
        try:
            with smbclient.open_file(fr'{server_name}/{share_name}/{remote_file_path}', mode='rb', connection_cache=self.connection_cache) as remote_file:
                file_obj.write(remote_file.read())
                file_obj.seek(0)
            print("Load successfully!")
        except Exception as e:
            print(f"Ops, error is: {e}")

        return file_obj

    def smb_delete_file(self, remote_file_path, server_name=None, share_name=None):
        """ This function is used to copy local file to public folder

        Args:
            remote_file_path(str): This is the public file path that file will be saved under share name folder
            server_name(str):This is the  server name (url), e.g. szh0fs06.apac.bosch.com
            share_name(str): This is the  share_name of public folder, e.g. GS
        """
        server_name, share_name = self.prepare_server_name_share_name(server_name, share_name)

        try:
            # Delete the specified remote file
            smbclient.remove(fr'//{server_name}/{share_name}/{remote_file_path}', connection_cache=self.connection_cache)
            print("File deleted successfully!")

        except Exception as e:
            print(f"An error occurred: {e}")

    def smb_traverse_delete_file(self, report_save_path, exception_str='', server_name=None, share_name=None):
        """ This function is used to copy local file to public folder

        Args:
            report_save_path(str): This is the folder path of save folder
            exception_str(str): This is the string to exclude when file name or folder name contains current string
            server_name(str):This is the  server name (url), e.g. szh0fs06.apac.bosch.com
            share_name(str): This is the  share_name of public folder, e.g. GS
        """
        server_name, share_name = self.prepare_server_name_share_name(server_name, share_name)

        try:
            except_str_list = [item.upper().strip() for item in exception_str.replace('，', ',').split(',') if item.strip()]
            traverse_result_list = self.smb_traverse_remote_folder(report_save_path, server_name, share_name)
            for traverse_item_dict in traverse_result_list:
                item_name = traverse_item_dict['name']
                item_name_upper = item_name.upper()
                if traverse_item_dict['is_folder']:
                    if not any(keyword in item_name_upper for keyword in except_str_list):
                        folder_path = f"{report_save_path}/{item_name}"
                        self.smb_traverse_delete_file(folder_path, exception_str, server_name, share_name)
                else:
                    if not any(keyword in item_name_upper for keyword in except_str_list):
                        remote_file_path = f"{report_save_path}/{item_name}"
                        try:
                            # Delete the specified remote file
                            smbclient.remove(fr'//{server_name}/{share_name}/{remote_file_path}', connection_cache=self.connection_cache)
                            print("File deleted successfully!")

                        except Exception as e:
                            print(f"An error occurred: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")

    def smb_traverse_delete_file_by_keyword(self, report_save_path, deletion_keyword='', server_name=None, share_name=None):
        """ This function is used to copy local file to public folder

        Args:
            report_save_path(str): This is the folder path of save folder
            deletion_keyword(str): This is the string to keyword to match file or folder
            server_name(str):This is the  server name (url), e.g. szh0fs06.apac.bosch.com
            share_name(str): This is the  share_name of public folder, e.g. GS
        """
        server_name, share_name = self.prepare_server_name_share_name(server_name, share_name)

        try:
            keyword_str_list = [item.upper().strip() for item in deletion_keyword.replace('，', ',').split(',') if item.strip()]
            traverse_result_list = self.smb_traverse_remote_folder(report_save_path, server_name, share_name)
            for traverse_item_dict in traverse_result_list:
                item_name = traverse_item_dict['name']
                item_name_upper = item_name.upper()
                if traverse_item_dict['is_folder']:
                    if any(keyword in item_name_upper for keyword in keyword_str_list):
                        folder_path = f"{report_save_path}/{item_name}"
                        self.smb_traverse_delete_file_by_keyword(folder_path, deletion_keyword, server_name, share_name)
                else:
                    if any(keyword in item_name_upper for keyword in keyword_str_list):
                        remote_file_path = f"{report_save_path}/{item_name}"
                        try:
                            # Delete the specified remote file
                            smbclient.remove(fr'//{server_name}/{share_name}/{remote_file_path}', connection_cache=self.connection_cache)
                            print("File deleted successfully!")

                        except Exception as e:
                            print(f"An error occurred: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")

    def smb_create_folder(self, remote_folder_path, server_name=None, share_name=None):
        """ This function is used to copy local file to public folder

        Args:
            remote_folder_path(str): This is the public folder path that folder will be created under share name folder
            server_name(str):This is the  server name (url), e.g. szh0fs06.apac.bosch.com
            share_name(str): This is the  share_name of public folder, e.g. GS
        """
        server_name, share_name = self.prepare_server_name_share_name(server_name, share_name)

        try:
            # Create the specified remote directory
            smbclient.makedirs(fr'//{server_name}/{share_name}/{remote_folder_path}', connection_cache=self.connection_cache, exist_ok=True)
            print("Directory created successfully!")

        except Exception as e:
            print(f"An error occurred: {e}")

    def smb_delete_folder(self, remote_folder_path, server_name=None, share_name=None):
        """ This function is used to delete remote folder

        Args:
            remote_folder_path(str): This is the public folder path that folder will be created under share name folder
            server_name(str):This is the  server name (url), e.g. szh0fs06.apac.bosch.com
            share_name(str): This is the  share_name of public folder, e.g. GS
        """
        server_name, share_name = self.prepare_server_name_share_name(server_name, share_name)

        try:
            # Iterate over the folder contents
            remote_folder_path = f'{server_name}/{share_name}/{remote_folder_path}'
            for entry in smbclient.scandir(remote_folder_path, connection_cache=self.connection_cache):
                entry_path = f"{remote_folder_path}/{entry.name}"
                if entry.is_dir():
                    # Recursively delete subfolders
                    self.smb_delete_folder(entry_path, server_name, share_name)
                else:
                    # Delete files
                    smbclient.remove(entry_path, connection_cache=self.connection_cache)

            # Remove the now-empty folder
            smbclient.rmdir(remote_folder_path, connection_cache=self.connection_cache)
            print(f"Folder {remote_folder_path} and its contents have been successfully deleted.")
        except FileNotFoundError:
            print(f"Folder {remote_folder_path} does not exist.")
        except OSError as e:
            print(f"Failed to delete folder {remote_folder_path}: {e}")

    def smb_move_remote_file(self, from_remote_file_path, to_remote_file_path, from_server_name=None, from_share_name=None, to_server_name=None, to_share_name=None):
        """ This function is used to move remote file to another folder

        Args:
            from_server_name(str):This is the source server name (url), e.g. szh0fs06.apac.bosch.com
            from_share_name(str): This is the source share_name of public folder, e.g. GS_ACC_CN$
            from_remote_file_path(str): This is the source public file path that file will be saved under share name folder
            to_server_name(str):This is the destination server name (url), e.g. szh0fs06.apac.bosch.com
            to_share_name(str): This is the  destination share_name of public folder, e.g. GS_ACC_CN$
            to_remote_file_path(str): This is the destination new public file path that file will be saved under share name folder
        """
        from_server_name, from_share_name = self.prepare_server_name_share_name(from_server_name, from_share_name)
        to_server_name, to_share_name = self.prepare_server_name_share_name(to_server_name, to_share_name)

        is_from_file_exist, file_obj = self.smb_check_file_exist(from_remote_file_path, from_server_name, from_share_name)
        if is_from_file_exist:
            self.smb_store_remote_file_by_obj(to_remote_file_path, file_obj, to_server_name, to_share_name)
            self.smb_delete_file(from_remote_file_path, from_server_name, from_share_name)
            print("Move successfully!")
        else:
            print("Source file does not exist!")

    def smb_move_remote_folder(self, from_remote_folder_path, to_remote_folder_path, from_server_name=None, from_share_name=None, to_server_name=None, to_share_name=None):
        """ This function is used to move remote folder to another folder

        Args:
            from_server_name(str):This is the source server name (url), e.g. szh0fs06.apac.bosch.com
            from_share_name(str): This is the source share_name of public folder, e.g. GS_ACC_CN$
            from_remote_folder_path(str): This is the source public folder path that folder will be saved under share name folder
            to_server_name(str):This is the destination server name (url), e.g. szh0fs06.apac.bosch.com
            to_share_name(str): This is the  destination share_name of public folder, e.g. GS_ACC_CN$
            to_remote_folder_path(str): This is the destination new public folder path that folder will be saved under share name folder
        """
        from_server_name, from_share_name = self.prepare_server_name_share_name(from_server_name, from_share_name)
        to_server_name, to_share_name = self.prepare_server_name_share_name(to_server_name, to_share_name)

        is_from_folder_exist = self.smb_check_folder_exist(from_remote_folder_path, from_server_name, from_share_name)
        if is_from_folder_exist:
            self.smb_create_folder(to_remote_folder_path, to_server_name, to_share_name)
            for item in self.smb_traverse_remote_folder(from_remote_folder_path, from_server_name, from_share_name):
                if item['is_folder']:
                    self.smb_move_remote_folder(f"{from_remote_folder_path}/{item['name']}", f"{to_remote_folder_path}/{item['name']}",
                                                from_server_name, from_share_name, to_server_name, to_share_name)
                else:
                    self.smb_move_remote_file(f"{from_remote_folder_path}/{item['name']}", f"{to_remote_folder_path}/{item['name']}",
                                              from_server_name, from_share_name, to_server_name, to_share_name)
            self.smb_delete_folder(from_remote_folder_path, from_server_name, from_share_name)
            print("Move successfully!")
        else:
            print("Source folder does not exist!")

    def smb_copy_remote_file(self, from_remote_file_path, to_remote_file_path, from_server_name=None, from_share_name=None, to_server_name=None, to_share_name=None):
        """ This function is used to copy remote file to another folder

        Args:
            from_server_name(str):This is the source server name (url), e.g. szh0fs06.apac.bosch.com
            from_share_name(str): This is the source share_name of public folder, e.g. GS_ACC_CN$
            from_remote_file_path(str): This is the source public file path that file will be saved under share name folder
            to_server_name(str):This is the destination server name (url), e.g. szh0fs06.apac.bosch.com
            to_share_name(str): This is the  destination share_name of public folder, e.g. GS_ACC_CN$
            to_remote_file_path(str): This is the destination new public file path that file will be saved under share name folder
        """
        from_server_name, from_share_name = self.prepare_server_name_share_name(from_server_name, from_share_name)
        to_server_name, to_share_name = self.prepare_server_name_share_name(to_server_name, to_share_name)

        is_from_file_exist, file_obj = self.smb_check_file_exist(from_remote_file_path, from_server_name, from_share_name)
        if is_from_file_exist:
            self.smb_store_remote_file_by_obj(to_remote_file_path, file_obj, to_server_name, to_share_name)
            print("Copy successfully!")
        else:
            print("Source file does not exist!")

    def smb_copy_remote_folder(self, from_remote_folder_path, to_remote_folder_path, from_server_name=None, from_share_name=None, to_server_name=None, to_share_name=None):
        """ This function is used to copy remote folder to another folder

        Args:
            from_server_name(str):This is the source server name (url), e.g. szh0fs06.apac.bosch.com
            from_share_name(str): This is the source share_name of public folder, e.g. GS_ACC_CN$
            from_remote_folder_path(str): This is the source public folder path that folder will be saved under share name folder
            to_server_name(str):This is the destination server name (url), e.g. szh0fs06.apac.bosch.com
            to_share_name(str): This is the  destination share_name of public folder, e.g. GS_ACC_CN$
            to_remote_folder_path(str): This is the destination new public folder path that folder will be saved under share name folder
        """
        from_server_name, from_share_name = self.prepare_server_name_share_name(from_server_name, from_share_name)
        to_server_name, to_share_name = self.prepare_server_name_share_name(to_server_name, to_share_name)

        is_from_folder_exist = self.smb_check_folder_exist(from_remote_folder_path, from_server_name, from_share_name)
        if is_from_folder_exist:
            self.smb_create_folder(to_remote_folder_path, to_server_name, to_share_name)
            for item in self.smb_traverse_remote_folder(from_remote_folder_path, from_server_name, from_share_name):
                if item['is_folder']:
                    self.smb_copy_remote_folder(f"{from_remote_folder_path}/{item['name']}", f"{to_remote_folder_path}/{item['name']}",
                                                from_server_name, from_share_name, to_server_name, to_share_name)
                else:
                    self.smb_copy_remote_file(f"{from_remote_folder_path}/{item['name']}", f"{to_remote_folder_path}/{item['name']}",
                                              from_server_name, from_share_name, to_server_name, to_share_name)
            print("Copy successfully!")
        else:
            print("Source folder does not exist!")

    def smb_rename_remote_file(self, remote_file_path, new_remote_file_path, server_name=None, share_name=None):
        """ This function is used to rename remote file

        Args:
            server_name(str):This is the server name (url), e.g. szh0fs06.apac.bosch.com
            share_name(str): This is the share_name of public folder, e.g. GS_ACC_CN$
            remote_file_path(str): This is the public file path that file will be saved under share name folder
            new_remote_file_path(str): This is the new public file path that file will be saved under share name folder

        """
        server_name, share_name = self.prepare_server_name_share_name(server_name, share_name)

        try:
            # Rename the specified remote file
            smbclient.rename(fr'//{server_name}/{share_name}/{remote_file_path}', fr'//{server_name}/{share_name}/{new_remote_file_path}',
                             connection_cache=self.connection_cache)
            print("File renamed successfully!")

        except Exception as e:
            print(f"An error occurred: {e}")

    def smb_rename_remote_folder(self, remote_folder_path, new_remote_folder_path, server_name=None, share_name=None):
        """ This function is used to rename remote folder

        Args:
            server_name(str):This is the server name (url), e.g. szh0fs06.apac.bosch.com
            share_name(str): This is the share_name of public folder, e.g. GS_ACC_CN$
            remote_folder_path(str): This is the public folder path that folder will be saved under share name folder
            new_remote_folder_path(str): This is the new public folder path that folder will be saved under share name folder
        """
        server_name, share_name = self.prepare_server_name_share_name(server_name, share_name)

        try:
            # Rename the specified remote directory
            smbclient.rename(fr'//{server_name}/{share_name}/{remote_folder_path}', fr'//{server_name}/{share_name}/{new_remote_folder_path}',
                             connection_cache=self.connection_cache)
            print("Folder renamed successfully!")

        except Exception as e:
            print(f"An error occurred: {e}")
