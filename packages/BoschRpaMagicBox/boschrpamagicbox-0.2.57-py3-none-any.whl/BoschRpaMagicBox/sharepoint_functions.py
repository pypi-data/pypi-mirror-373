from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.user_credential import UserCredential


class SharePointClient:
    def __init__(self, site_url: str, username: str, password: str):
        """
        Initialize a SharePointClient object.
        """
        username = f'{username}@bosch.com'
        self.ctx = ClientContext(site_url).with_credentials(UserCredential(username, password))

    def list_folder(self, folder_url: str):
        """
        List all items (files and folders) in a SharePoint folder.

        Args:
            folder_url (str): The server-relative URL of the folder.

        Returns:
            list[dict]: A list of dictionaries, each containing:
                - name (str): The item name
                - type (str): "file" or "folder"
        """
        folder = self.ctx.web.get_folder_by_server_relative_url(folder_url)

        # Load files
        files = folder.files
        self.ctx.load(files)

        # Load subfolders
        subfolders = folder.folders
        self.ctx.load(subfolders)

        self.ctx.execute_query()

        items = []

        # Add files
        for f in files:
            items.append({
                "name": f.properties["Name"],
                "type": "file"
            })

        # Add folders
        for sub in subfolders:
            items.append({
                "name": sub.properties["Name"],
                "type": "folder"
            })

        return items

    def upload_file(self, folder_url: str, file_name: str, local_path: str = None, file_obj=None, overwrite: bool = True):
        """
        Upload a file to a SharePoint folder.

        Args:
            folder_url (str): The server-relative URL of the SharePoint folder.
            file_name (str): The name to save the file as in SharePoint.
            local_path (str, optional): Local path of the file to upload. Ignored if file_obj is provided.
            file_obj (bytes, bytearray, or BytesIO, optional): File content. If provided, local_path is ignored.
            overwrite (bool, optional): Whether to overwrite the file if it already exists. Default is True.

        Returns:
            str: The server-relative URL of the uploaded file.
        """
        folder = self.ctx.web.get_folder_by_server_relative_url(folder_url)

        # Prefer file_obj if provided
        if file_obj is not None:
            if hasattr(file_obj, "read"):  # Handle BytesIO
                file_obj = file_obj.read()
            elif not isinstance(file_obj, (bytes, bytearray)):
                raise TypeError("file_obj must be bytes, bytearray, or BytesIO")
        elif local_path:
            with open(local_path, "rb") as f:
                file_obj = f.read()
        else:
            raise ValueError("Either local_path or file_obj must be provided")

        # Upload file with overwrite option
        uploaded_file = folder.upload_file(file_name, file_obj, overwrite).execute_query()
        return uploaded_file.serverRelativeUrl

    def download_file(self, folder_url: str, filename: str, local_path: str = None):
        """ Download a file from a SharePoint folder.

        Args:
            folder_url(str): The server-relative URL of the SharePoint folder.
            filename(str): The name of the file to download.
            local_path(str, optional): Local path to save the downloaded file. Defaults to filename if not provided.
        """
        folder = self.ctx.web.get_folder_by_server_relative_url(folder_url)
        file = folder.files.get_by_url(filename)
        self.ctx.load(file)
        self.ctx.execute_query()

        if local_path is None:
            local_path = filename

        with open(local_path, "wb") as f:
            file.download(f).execute_query()
        return local_path

    def delete_file(self, folder_url: str, filename: str):
        """ Delete a file from a SharePoint folder.

        Args:
            folder_url(str): The server-relative URL of the SharePoint folder.
            filename(str): The name of the file to delete.
        """
        folder = self.ctx.web.get_folder_by_server_relative_url(folder_url)
        file = folder.files.get_by_url(filename)
        file.delete_object()
        self.ctx.execute_query()
        return f'File is deleted: {filename}'

    def create_folder(self, parent_folder_url: str, folder_name: str):
        """Create a new folder in a SharePoint folder.

        Args:
            parent_folder_url(str): The server-relative URL of the parent folder.
            folder_name(str): The name of the new folder to create.
        """
        parent_folder = self.ctx.web.get_folder_by_server_relative_url(parent_folder_url)
        new_folder = parent_folder.folders.add(folder_name)
        self.ctx.execute_query()
        return f"Folder is created: {folder_name}"

    def delete_folder(self, folder_url: str):
        """ Delete a folder from SharePoint.
         Args:
             folder_url(str): The server-relative URL of the folder to delete.

        """
        folder = self.ctx.web.get_folder_by_server_relative_url(folder_url)
        folder.delete_object()
        self.ctx.execute_query()
        return f"Folder is deleted: {folder_url}"
