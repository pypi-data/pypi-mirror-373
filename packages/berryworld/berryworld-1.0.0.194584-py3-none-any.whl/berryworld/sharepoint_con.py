import os
import msal
import urllib
import requests
import traceback
import pandas as pd
from dotenv import load_dotenv
from urllib.parse import unquote

load_dotenv(os.path.join(os.getcwd(), '.env'))


class SharepointConnection:
    """Class to connect to sharepoint
    """

    def __init__(self, env_name=None, api_version=None):
        """ Initialize the class
        :param env_name: Environment Variable name
        :param api_version: SharePoint API version to use
        """
        try:
            if env_name is None:
                raise ValueError('Please provide a valid env_name')

            if api_version is None:
                self.api_version = 'v1.0'
            else:
                self.api_version = api_version

            self.env_name = env_name
            self.client_id = os.environ.get(f"SHAREPOINT-CLIENT-ID")
            self.organisation_id = os.environ.get(f"SHAREPOINT-ORG-ID")
            self.username = os.environ.get(f"SHAREPOINT-USER")
            self.password = os.environ.get(f"SHAREPOINT-PASSWORD")
            self.scopes = ['Sites.ReadWrite.All', 'Files.ReadWrite.All']

        except ValueError as e:
            raise ValueError(f"Variable {str(e)} not found")

        self.graph_url = f'https://graph.microsoft.com/{self.api_version}'
        self.headers = self.get_headers()
        self.children = 'children?select=id,name,webUrl,file'

        self.site_id = self.list_sites(site_name=env_name)['id'].values[0]
        self.drive_id = self.set_drive_id()

    def get_headers(self):
        """ Query the Headers to be sent on the queries to SharePoint """
        try:
            base_url = f'https://login.microsoftonline.com/{self.organisation_id}'
            pca = msal.PublicClientApplication(self.client_id, authority=base_url)
            token = pca.acquire_token_by_username_password(self.username, self.password, self.scopes)
            header = {"Authorization": f"Bearer {token['access_token']}"}
            return header
        except Exception as e:
            Exception(f"Error when authenticating in SharePoint: {str(e)}")

    def set_drive_id(self):
        drive_url = f'{self.graph_url}/sites/{self.site_id}/drives'
        try:
            result = requests.get(drive_url, headers=self.headers)
            drive_id = pd.DataFrame(result.json()['value'])[['id', 'name']]
        except ValueError:
            raise ValueError(f"Could not retrieve the root folders: {traceback.format_exc()}")
        return drive_id

    def list_sites(self, site_name=None):
        """ List Sites in SharePoint
        :param site_name: Name of the site to retrieve the information
        """
        site_url = f'{self.graph_url}/sites?search=*'
        try:
            result = requests.get(site_url, headers=self.headers)
            site_values = result.json()['value']
            sites_df = pd.DataFrame(site_values)[['id', 'name', 'webUrl']]

            if site_name is not None:
                sites_df = sites_df.loc[
                    sites_df['name'].str.lower().str.replace(' ', '') == site_name.lower().replace(' ', '')]
                if sites_df.shape[0] == 0:
                    raise ValueError(f"The site {site_name} was not found")

            return sites_df

        except ValueError as e:
            raise ValueError(f"Could not retrieve the sites: {str(e)}")

    def list_items(self, path, file_type='All'):
        """ List Folders in SharePoint
        :param path: Full path to the directory to list the items. Use "/" to separate the directories (if path is not
            provided, it will show the root drives)
        :param file_type: Indicate which kind of items to retrieve:
            - "All" will retrieve all the items in the directory
            - "Folder" will retrieve all the folders in the directory
            - "File" will retrieve all the files in the directory
        """
        try:
            folders = self.resolve_path(path)
            try:
                drive_id = self.drive_id.loc[self.drive_id['name'].str.lower().str.replace(' ', '') ==
                                             folders[0].lower().replace(' ', ''), 'id'].values[0]
            except Exception as e:
                print(e)
                raise Exception(f"There are no items in: {path}. Please check self.drive_id to provide a valid folder")

            if len(folders) == 1:
                request_url = f'{self.graph_url}/drives/{drive_id}/root/children?select=id,name,webUrl,file'
                result = requests.get(request_url, headers=self.headers)
                if str(result.status_code).startswith("2"):
                    items_df = pd.DataFrame(result.json()['value'])
                    if 'file' in items_df.columns:
                        items_df = items_df[['id', 'name', 'webUrl', 'file']]
                        items_df['file'] = items_df['file'].fillna('folder')
                        if file_type.lower() == 'folder':
                            return items_df.loc[items_df['file'] == 'folder']
                        elif file_type.lower() == 'file':
                            return items_df.loc[items_df['file'] != 'folder']
                        return items_df
                    else:
                        items_df = items_df[['id', 'name', 'webUrl']]
                        items_df = items_df.assign(**{'file': 'file'})
                        return items_df
                else:
                    raise Exception(f"Status Code - {str(result.status_code)}. "
                                    f"There are no items in the root folder: {path}")

            url_path = urllib.parse.quote("/".join(folders[1:]))
            query_url = f'{self.graph_url}/drives/{drive_id}/root:/{url_path}'
            result = requests.get(query_url, headers=self.headers)
            if str(result.status_code).startswith("2"):
                folder_id = result.json()['id']
                drive_id = result.json()['parentReference']['driveId']

                request_url = f'{self.graph_url}/drives/{drive_id}/items/{folder_id}/children' \
                              f'?select=id,name,webUrl,file'
                result = requests.get(request_url, headers=self.headers)
                if str(result.status_code).startswith("2"):
                    items_df = pd.DataFrame(result.json()['value'])
                    if items_df.shape[0] > 0:
                        if 'file' in items_df.columns:
                            items_df = items_df[['id', 'name', 'webUrl', 'file']]
                            items_df['file'] = items_df['file'].fillna('folder')
                            if file_type.lower() == 'folder':
                                return items_df.loc[items_df['file'] == 'folder']
                            elif file_type.lower() == 'file':
                                return items_df.loc[items_df['file'] != 'folder']
                            return items_df
                        else:
                            items_df = items_df[['id', 'name', 'webUrl']]
                            items_df = items_df.assign(**{'file': 'file'})
                            return items_df
                    else:
                        return items_df
                else:
                    raise Exception(f"Status Code - {str(result.status_code)}. "
                                    f"There are no items in: {path}")
            else:
                raise Exception(f"Status Code - {str(result.status_code)}. "
                                f"There are no folders in: {path}")
        except Exception as e:
            raise Exception(str(e))

    def get_file_content(self, file_path):
        """ Get the file content from a file in SharePoint
        :param file_path: Full path to the directory where the file is. Use "/" to separate the directories
        """
        try:
            folders = self.resolve_path(file_path)
            if len(folders) < 2:
                raise Exception("Please provide a valid full path to the file")

            drive_id = self.drive_id.loc[self.drive_id['name'].str.lower().str.replace(' ', '') ==
                                         folders[0].lower().replace(' ', ''), 'id'].values[0]

            url_path = urllib.parse.quote("/".join(folders[1:]))
            query_url = f'{self.graph_url}/drives/{drive_id}/root:/{url_path}'
            result = requests.get(query_url, headers=self.headers)
            if str(result.status_code).startswith("2"):
                folder_id = result.json()['id']
                drive_id = result.json()['parentReference']['driveId']

                result = requests.get(f'{self.graph_url}/drives/{drive_id}/items/{folder_id}/content',
                                      headers=self.headers)
                file_content = result.content
                return file_content
            else:
                raise Exception(f"Status Code - {str(result.status_code)}. "
                                f"There are no files called: {folders[-1]}")
        except Exception as e:
            raise Exception(str(e))

    def download_file(self, file_path, download_name=None, download_path=None):
        """ Get the file content from a file in SharePoint
        :param file_path: Full path to the directory where the file is. Use "/" to separate the directories
        :param download_name: Name for the downloaded file content
        :param download_path: Location of where to download the file content
        """
        try:
            folders = self.resolve_path(file_path)
            if len(folders) < 2:
                raise Exception("Please provide a valid full path to the file")

            drive_id = self.drive_id.loc[self.drive_id['name'].str.lower().str.replace(' ', '') ==
                                         folders[0].lower().replace(' ', ''), 'id'].values[0]

            url_path = urllib.parse.quote("/".join(folders[1:]))
            query_url = f'{self.graph_url}/drives/{drive_id}/root:/{url_path}'
            result = requests.get(query_url, headers=self.headers)
            if str(result.status_code).startswith("2"):
                folder_id = result.json()['id']
                drive_id = result.json()['parentReference']['driveId']

                result = requests.get(f'{self.graph_url}/drives/{drive_id}/items/{folder_id}/content',
                                      headers=self.headers)

                if download_name is None:
                    download_name = folders[-1]

                if download_path is None:
                    open(download_name, 'wb').write(result.content)
                else:
                    download_path = download_path + download_name
                    with open(download_path, 'wb') as f:
                        f.write(result.content)
            else:
                raise Exception(f"Status Code - {str(result.status_code)}. "
                                f"There are no files called: {folders[-1]}")
        except Exception as e:
            raise Exception(str(e))

    def create_folder(self, folder_path):
        """ Create a folder in SharePoint
        :param folder_path: Full path to the directory to be created. Use "/" to separate the directories
        """
        try:
            folders = self.resolve_path(folder_path)
            if len(folders) < 2:
                raise Exception("Please provide a valid full path to the file")

            drive_id = self.drive_id.loc[self.drive_id['name'].str.lower().str.replace(' ', '') ==
                                         folders[0].lower().replace(' ', ''), 'id'].values[0]

            url_path = urllib.parse.quote("/".join(folders[1:]))
            query_url = f'{self.graph_url}/drives/{drive_id}/root:/{url_path}'
            result = requests.get(query_url, headers=self.headers)
            if not str(result.status_code).startswith("2"):
                url_path = urllib.parse.quote("/".join(folders[1:-1]))
                query_url = f'{self.graph_url}/drives/{drive_id}/root:/{url_path}'
                result = requests.get(query_url, headers=self.headers)
                if str(result.status_code).startswith("2"):
                    folder_id = result.json()['id']
                    drive_id = result.json()['parentReference']['driveId']

                    query_url = f'{self.graph_url}/drives/{drive_id}/items/{folder_id}/children'
                    result = requests.post(query_url, headers=self.headers,
                                           json={
                                               "name": urllib.parse.quote(folders[-1]),
                                               "folder": {},
                                               "@microsoft.graph.conflictBehavior": "rename"
                                           })
                    print(f"Folder Created: {result.status_code}")

                else:
                    raise Exception(f"Status Code - {str(result.status_code)}. "
                                    f"Please provide a valid full path. The folders indicated do not exist")
            else:
                raise Exception(f"Status Code - {str(result.status_code)}. "
                                f"The folder already exists in path: {folders}")
        except Exception as e:
            raise Exception(str(e))

    def create_file(self, local_file, file_path, overwrite=True):
        """ Create a file in SharePoint folder
        :param local_file: Local file path to be uploaded to SharePoint
        :param file_path: Full path to the directory where the file is to be created. Use "/" to separate
            the directories. ONLY SUPPORTS uploading csv
        :param overwrite: Whether the file should be overwritten or not if already exists in the path
        """
        local_file = local_file.rstrip("/")
        file_path = file_path.rstrip("/")
        try:
            # Check files extension
            remote_extension = file_path.split('.')[-1]
            local_extension = local_file.split('.')[-1]
            if (remote_extension == '') | ('/' in remote_extension):
                file_path += '.' + local_extension
            else:
                if remote_extension != local_extension:
                    print('## Fixing remote extension file to match local extension file ##')
                    file_path = file_path.replace(remote_extension, local_extension)

            # Read local file data
            with open(local_file, 'rb') as f:
                contents = f.read()
                f.close()
            if len(contents) == 0:
                raise Exception(f'The local file is empty')
        except Exception as e:
            raise Exception(f'The local file path was not valid: {str(e)}')

        try:
            folders = self.resolve_path(file_path)
            if len(folders) < 2:
                raise Exception("Please provide a valid full path to the file")

            drive_id = self.drive_id.loc[self.drive_id['name'].str.lower().str.replace(' ', '') ==
                                         folders[0].lower().replace(' ', ''), 'id'].values[0]

            if len(folders) == 2:
                query_url = f'{self.graph_url}/drives/{drive_id}/root/children?select=parentReference'
                result = requests.get(query_url, headers=self.headers)
                folder_id = result.json()['value'][0]['parentReference']['id']
                file_name = urllib.parse.quote(folders[-1])

                query_url = f"{self.graph_url}/drives/{drive_id}/items/{folder_id}/children" \
                            f"?$filter=name eq '{file_name}'"
                result = requests.get(query_url, headers=self.headers)
                if len(result.json()['value']) > 0:
                    file_id = result.json()['value'][0]['id']
                    if overwrite:
                        query_url = f'{self.graph_url}/drives/{drive_id}/items/{file_id}/content'
                        result = requests.put(
                            query_url,
                            headers=self.headers,
                            data=contents
                        )
                        print(f"File Overwritten: {result.status_code}")
                    else:
                        raise Exception("The file is already created and won't be overwritten")
                else:
                    query_url = f'{self.graph_url}/drives/{drive_id}/items/{folder_id}:/{file_name}:/content'
                    result = requests.put(
                        query_url,
                        headers=self.headers,
                        data=contents
                    )
                    print(f"File Created: {result.status_code}")

            else:
                url_path = urllib.parse.quote("/".join(folders[1:-1]))
                query_url = f'{self.graph_url}/drives/{drive_id}/root:/{url_path}'
                result = requests.get(query_url, headers=self.headers)
                if str(result.status_code).startswith("2"):
                    folder_id = result.json()['id']
                    drive_id = result.json()['parentReference']['driveId']
                    file_name = urllib.parse.quote(folders[-1])

                    query_url = f"{self.graph_url}/drives/{drive_id}/items/{folder_id}/children" \
                                f"?$filter=name eq '{file_name}'"
                    result = requests.get(query_url, headers=self.headers)
                    if len(result.json()['value']) > 0:
                        file_id = result.json()['value'][0]['id']
                        if overwrite:
                            query_url = f'{self.graph_url}/drives/{drive_id}/items/{file_id}/content'
                            result = requests.put(
                                query_url,
                                headers=self.headers,
                                data=contents
                            )
                            print(f"File Overwritten: {result.status_code}")
                        else:
                            raise Exception("The file is already created and won't be overwritten")
                    else:
                        query_url = f'{self.graph_url}/drives/{drive_id}/items/{folder_id}:/{file_name}:/content'
                        result = requests.put(
                            query_url,
                            headers=self.headers,
                            data=contents
                        )
                        print(f"File Created: {result.status_code}")
                else:
                    raise Exception(f"Status Code - {str(result.status_code)}. "
                                    f"The path where the file is to be created does not exist: {file_path}")

        except Exception as e:
            raise Exception(str(e))

    def delete_file(self, file_path):
        """ Delete a file in SharePoint
        :param file_path: Full path to the file to be removed. Use "/" to separate the directories
        """
        try:
            folders = self.resolve_path(file_path)
            if len(folders) < 2:
                raise Exception("Please provide a valid full path to the file")

            drive_id = self.drive_id.loc[self.drive_id['name'].str.lower().str.replace(' ', '') ==
                                         folders[0].lower().replace(' ', ''), 'id'].values[0]

            url_path = urllib.parse.quote("/".join(folders[1:]))
            query_url = f'{self.graph_url}/drives/{drive_id}/root:/{url_path}'
            result = requests.get(query_url, headers=self.headers)
            if str(result.status_code).startswith("2"):
                drive_id = result.json()['parentReference']['driveId']

                url_path = urllib.parse.quote("/".join(folders[1:]))
                query_url = f'{self.graph_url}/drives/{drive_id}/root:/{url_path}'
                result = requests.delete(query_url, headers=self.headers)

                print(f"File Deleted: {result.status_code}")

            else:
                raise Exception(f"Status Code - {str(result.status_code)}. "
                                f"The path indicated does not exist {file_path}")
        except Exception as e:
            raise Exception(str(e))

    def delete_folder(self, folder_path):
        """ Delete a folder in SharePoint
        :param folder_path: Full path to the folder to be removed. Use "/" to separate the directories
        """
        try:
            folders = self.resolve_path(folder_path)
            if len(folders) < 2:
                raise Exception("Please provide a valid full path to the file")

            drive_id = self.drive_id.loc[self.drive_id['name'].str.lower().str.replace(' ', '') ==
                                         folders[0].lower().replace(' ', ''), 'id'].values[0]

            url_path = urllib.parse.quote("/".join(folders[1:]))
            query_url = f'{self.graph_url}/drives/{drive_id}/root:/{url_path}'
            result = requests.get(query_url, headers=self.headers)
            if str(result.status_code).startswith("2"):
                drive_id = result.json()['parentReference']['driveId']

                url_path = urllib.parse.quote("/".join(folders[1:]))
                query_url = f'{self.graph_url}/drives/{drive_id}/root:/{url_path}'
                result = requests.delete(query_url, headers=self.headers)

                print(f"Folder Deleted: {result.status_code}")

            else:
                raise Exception(f"Status Code - {str(result.status_code)}. "
                                f"The path indicated does not exist {folder_path}")
        except Exception as e:
            raise Exception(str(e))

    @staticmethod
    def resolve_path(path):
        """ Resolve the path to a list of folders / files
        :param path: Full path to the directory to be created. Use "/" to separate the directories
        """
        final_path = []

        path = path.rstrip("/").lstrip("/")
        while os.path.split(path)[-1] != '':
            final_path.insert(0, os.path.split(path)[-1])
            path = os.path.split(path)[0]

        return final_path


class SharepointConn:
    """Class to connect to sharepoint
    """

    def __init__(self, env_name=None, api_version=None):
        """ Initialize the class
        :param env_name: Environment Variable name
        :param api_version: SharePoint API version to use
        """
        if os.environ.get(f"SHAREPOINT-{env_name.upper()}") is None:
            raise ValueError(f'Sharepoint environment {env_name} not found in the environment variables')

        if api_version is None:
            self.api_version = 'v1.0'
        else:
            self.api_version = api_version

        try:
            self.client_id = os.environ.get(f"SHAREPOINT-AUTH").split(' ')[0]
            self.organisation_id = os.environ.get(f"SHAREPOINT-AUTH").split(' ')[1]
        except Exception as e:
            print(e)
            raise ValueError(f"Sharepoint Auth not found in the environment variables")

        self.env_name = os.environ.get(f"SHAREPOINT-{env_name.upper()}").split(' ')[0]
        self.username = os.environ.get(f"SHAREPOINT-{env_name.upper()}").split(' ')[1]
        self.password = os.environ.get(f"SHAREPOINT-{env_name.upper()}").split(' ')[2]
        self.scopes = ['Sites.ReadWrite.All', 'Files.ReadWrite.All']

        self.graph_url = f'https://graph.microsoft.com/{self.api_version}'
        self.headers = self.get_headers()
        self.children = 'children?select=id,name,webUrl,file'

        self.site_id = self.list_sites(site_name=self.env_name)['id'].values[0]
        self.drive_id = self.set_drive_id()

    def get_headers(self):
        """ Query the Headers to be sent on the queries to SharePoint """
        try:
            base_url = f'https://login.microsoftonline.com/{self.organisation_id}'
            pca = msal.PublicClientApplication(self.client_id, authority=base_url)
            token = pca.acquire_token_by_username_password(self.username, self.password, self.scopes)
            header = {"Authorization": f"Bearer {token['access_token']}"}
            return header
        except Exception as e:
            Exception(f"Error when authenticating in SharePoint: {str(e)}")

    def set_drive_id(self):
        drive_url = f'{self.graph_url}/sites/{self.site_id}/drives'
        try:
            result = requests.get(drive_url, headers=self.headers)
            drive_id = pd.DataFrame(result.json()['value'])[['id', 'name']]
        except ValueError:
            raise ValueError(f"Could not retrieve the root folders: {traceback.format_exc()}")
        return drive_id

    def list_sites(self, site_name=None):
        """ List Sites in SharePoint
        :param site_name: Name of the site to retrieve the information
        """
        site_url = f'{self.graph_url}/sites?search=*'
        try:
            result = requests.get(site_url, headers=self.headers)
            site_values = result.json()['value']
            sites_df = pd.DataFrame(site_values)[['id', 'name', 'webUrl']]

            if site_name is not None:
                sites_df = sites_df.loc[
                    sites_df['name'].str.lower().str.replace(' ', '') == site_name.lower().replace(' ', '')]
                if sites_df.shape[0] == 0:
                    raise ValueError(f"The site {site_name} was not found")

            return sites_df

        except ValueError as e:
            raise ValueError(f"Could not retrieve the sites: {str(e)}")

    def list_items(self, path, file_type='All'):
        """ List Folders in SharePoint
        :param path: Full path to the directory to list the items. Use "/" to separate the directories (if path is not
            provided, it will show the root drives)
        :param file_type: Indicate which kind of items to retrieve:
            - "All" will retrieve all the items in the directory
            - "Folder" will retrieve all the folders in the directory
            - "File" will retrieve all the files in the directory
        """
        try:
            folders = self.resolve_path(path)
            try:
                drive_id = self.drive_id.loc[self.drive_id['name'].str.lower().str.replace(' ', '') ==
                                             folders[0].lower().replace(' ', ''), 'id'].values[0]
            except Exception as e:
                print(e)
                raise Exception(f"There are no items in: {path}. Please check self.drive_id to provide a valid folder")

            if len(folders) == 1:
                request_url = f'{self.graph_url}/drives/{drive_id}/root/children?select=id,name,webUrl,file'
                result = requests.get(request_url, headers=self.headers)
                if str(result.status_code).startswith("2"):
                    items_df = pd.DataFrame(result.json()['value'])
                    if 'file' in items_df.columns:
                        items_df = items_df[['id', 'name', 'webUrl', 'file']]
                        items_df['file'] = items_df['file'].fillna('folder')
                        if file_type.lower() == 'folder':
                            return items_df.loc[items_df['file'] == 'folder']
                        elif file_type.lower() == 'file':
                            return items_df.loc[items_df['file'] != 'folder']
                        return items_df
                    else:
                        items_df = items_df[['id', 'name', 'webUrl']]
                        items_df = items_df.assign(**{'file': 'file'})
                        return items_df
                else:
                    raise Exception(f"Status Code - {str(result.status_code)}. "
                                    f"There are no items in the root folder: {path}")

            url_path = urllib.parse.quote("/".join(folders[1:]))
            query_url = f'{self.graph_url}/drives/{drive_id}/root:/{url_path}'
            result = requests.get(query_url, headers=self.headers)
            if str(result.status_code).startswith("2"):
                folder_id = result.json()['id']
                drive_id = result.json()['parentReference']['driveId']

                request_url = f'{self.graph_url}/drives/{drive_id}/items/{folder_id}/children' \
                              f'?select=id,name,webUrl,file'
                result = requests.get(request_url, headers=self.headers)
                if str(result.status_code).startswith("2"):
                    items_df = pd.DataFrame(result.json()['value'])
                    if items_df.shape[0] > 0:
                        if 'file' in items_df.columns:
                            items_df = items_df[['id', 'name', 'webUrl', 'file']]
                            items_df['file'] = items_df['file'].fillna('folder')
                            if file_type.lower() == 'folder':
                                return items_df.loc[items_df['file'] == 'folder']
                            elif file_type.lower() == 'file':
                                return items_df.loc[items_df['file'] != 'folder']
                            return items_df
                        else:
                            items_df = items_df[['id', 'name', 'webUrl']]
                            items_df = items_df.assign(**{'file': 'file'})
                            return items_df
                    else:
                        return items_df
                else:
                    raise Exception(f"Status Code - {str(result.status_code)}. "
                                    f"There are no items in: {path}")
            else:
                raise Exception(f"Status Code - {str(result.status_code)}. "
                                f"There are no folders in: {path}")
        except Exception as e:
            raise Exception(str(e))

    def get_file_content(self, file_path):
        """ Get the file content from a file in SharePoint
        :param file_path: Full path to the directory where the file is. Use "/" to separate the directories
        """
        try:
            folders = self.resolve_path(file_path)
            if len(folders) < 2:
                raise Exception("Please provide a valid full path to the file")

            drive_id = self.drive_id.loc[self.drive_id['name'].str.lower().str.replace(' ', '') ==
                                         folders[0].lower().replace(' ', ''), 'id'].values[0]

            url_path = urllib.parse.quote("/".join(folders[1:]))
            query_url = f'{self.graph_url}/drives/{drive_id}/root:/{url_path}'
            result = requests.get(query_url, headers=self.headers)
            if str(result.status_code).startswith("2"):
                folder_id = result.json()['id']
                drive_id = result.json()['parentReference']['driveId']

                result = requests.get(f'{self.graph_url}/drives/{drive_id}/items/{folder_id}/content',
                                      headers=self.headers)
                file_content = result.content
                return file_content
            else:
                raise Exception(f"Status Code - {str(result.status_code)}. "
                                f"There are no files called: {folders[-1]}")
        except Exception as e:
            raise Exception(str(e))

    def download_file(self, file_path, download_name=None, download_path=None):
        """ Get the file content from a file in SharePoint
        :param file_path: Full path to the directory where the file is. Use "/" to separate the directories
        :param download_name: Name for the downloaded file content
        :param download_path: Location of where to download the file content
        """
        try:
            folders = self.resolve_path(file_path)
            if len(folders) < 2:
                raise Exception("Please provide a valid full path to the file")

            drive_id = self.drive_id.loc[self.drive_id['name'].str.lower().str.replace(' ', '') ==
                                         folders[0].lower().replace(' ', ''), 'id'].values[0]

            url_path = urllib.parse.quote("/".join(folders[1:]))
            query_url = f'{self.graph_url}/drives/{drive_id}/root:/{url_path}'
            result = requests.get(query_url, headers=self.headers)
            if str(result.status_code).startswith("2"):
                folder_id = result.json()['id']
                drive_id = result.json()['parentReference']['driveId']

                result = requests.get(f'{self.graph_url}/drives/{drive_id}/items/{folder_id}/content',
                                      headers=self.headers)

                if download_name is None:
                    download_name = folders[-1]

                if download_path is None:
                    open(download_name, 'wb').write(result.content)
                else:
                    download_path = download_path + download_name
                    with open(download_path, 'wb') as f:
                        f.write(result.content)
            else:
                raise Exception(f"Status Code - {str(result.status_code)}. "
                                f"There are no files called: {folders[-1]}")
        except Exception as e:
            raise Exception(str(e))

    def create_folder(self, folder_path):
        """ Create a folder in SharePoint
        :param folder_path: Full path to the directory to be created. Use "/" to separate the directories
        """
        try:
            folders = self.resolve_path(folder_path)
            if len(folders) < 2:
                raise Exception("Please provide a valid full path to the file")

            drive_id = self.drive_id.loc[self.drive_id['name'].str.lower().str.replace(' ', '') ==
                                         folders[0].lower().replace(' ', ''), 'id'].values[0]

            url_path = urllib.parse.quote("/".join(folders[1:]))
            query_url = f'{self.graph_url}/drives/{drive_id}/root:/{url_path}'
            result = requests.get(query_url, headers=self.headers)
            if not str(result.status_code).startswith("2"):
                url_path = urllib.parse.quote("/".join(folders[1:-1]))
                query_url = f'{self.graph_url}/drives/{drive_id}/root:/{url_path}'
                result = requests.get(query_url, headers=self.headers)
                if str(result.status_code).startswith("2"):
                    folder_id = result.json()['id']
                    drive_id = result.json()['parentReference']['driveId']

                    query_url = f'{self.graph_url}/drives/{drive_id}/items/{folder_id}/children'
                    result = requests.post(query_url, headers=self.headers,
                                           json={
                                               "name": urllib.parse.quote(folders[-1]),
                                               "folder": {},
                                               "@microsoft.graph.conflictBehavior": "rename"
                                           })
                    print(f"Folder Created: {result.status_code}")

                else:
                    raise Exception(f"Status Code - {str(result.status_code)}. "
                                    f"Please provide a valid full path. The folders indicated do not exist")
            else:
                raise Exception(f"Status Code - {str(result.status_code)}. "
                                f"The folder already exists in path: {folders}")
        except Exception as e:
            raise Exception(str(e))

    def create_file(self, local_file, file_path, overwrite=True):
        """ Create a file in SharePoint folder
        :param local_file: Local file path to be uploaded to SharePoint
        :param file_path: Full path to the directory where the file is to be created. Use "/" to separate
            the directories. ONLY SUPPORTS uploading csv
        :param overwrite: Whether the file should be overwritten or not if already exists in the path
        """
        local_file = local_file.rstrip("/")
        file_path = file_path.rstrip("/")
        try:
            # Check files extension
            remote_extension = file_path.split('.')[-1]
            local_extension = local_file.split('.')[-1]
            if (remote_extension == '') | ('/' in remote_extension):
                file_path += '.' + local_extension
            else:
                if remote_extension != local_extension:
                    print('## Fixing remote extension file to match local extension file ##')
                    file_path = file_path.replace(remote_extension, local_extension)

            # Read local file data
            with open(local_file, 'rb') as f:
                contents = f.read()
                f.close()
            if len(contents) == 0:
                raise Exception(f'The local file is empty')
        except Exception as e:
            raise Exception(f'The local file path was not valid: {str(e)}')

        try:
            folders = self.resolve_path(file_path)
            if len(folders) < 2:
                raise Exception("Please provide a valid full path to the file")

            drive_id = self.drive_id.loc[self.drive_id['name'].str.lower().str.replace(' ', '') ==
                                         folders[0].lower().replace(' ', ''), 'id'].values[0]

            if len(folders) == 2:
                query_url = f'{self.graph_url}/drives/{drive_id}/root/children?select=parentReference'
                result = requests.get(query_url, headers=self.headers)
                folder_id = result.json()['value'][0]['parentReference']['id']
                file_name = urllib.parse.quote(folders[-1])

                query_url = f"{self.graph_url}/drives/{drive_id}/items/{folder_id}/children" \
                            f"?$filter=name eq '{file_name}'"
                result = requests.get(query_url, headers=self.headers)
                if len(result.json()['value']) > 0:
                    file_id = result.json()['value'][0]['id']
                    if overwrite:
                        query_url = f'{self.graph_url}/drives/{drive_id}/items/{file_id}/content'
                        result = requests.put(
                            query_url,
                            headers=self.headers,
                            data=contents
                        )
                        print(f"File Overwritten: {result.status_code}")
                    else:
                        raise Exception("The file is already created and won't be overwritten")
                else:
                    query_url = f'{self.graph_url}/drives/{drive_id}/items/{folder_id}:/{file_name}:/content'
                    result = requests.put(
                        query_url,
                        headers=self.headers,
                        data=contents
                    )
                    print(f"File Created: {result.status_code}")

            else:
                url_path = urllib.parse.quote("/".join(folders[1:-1]))
                query_url = f'{self.graph_url}/drives/{drive_id}/root:/{url_path}'
                result = requests.get(query_url, headers=self.headers)
                if str(result.status_code).startswith("2"):
                    folder_id = result.json()['id']
                    drive_id = result.json()['parentReference']['driveId']
                    file_name = urllib.parse.quote(folders[-1])

                    query_url = f"{self.graph_url}/drives/{drive_id}/items/{folder_id}/children" \
                                f"?$filter=name eq '{file_name}'"
                    result = requests.get(query_url, headers=self.headers)
                    if len(result.json()['value']) > 0:
                        file_id = result.json()['value'][0]['id']
                        if overwrite:
                            query_url = f'{self.graph_url}/drives/{drive_id}/items/{file_id}/content'
                            result = requests.put(
                                query_url,
                                headers=self.headers,
                                data=contents
                            )
                            print(f"File Overwritten: {result.status_code}")
                        else:
                            raise Exception("The file is already created and won't be overwritten")
                    else:
                        query_url = f'{self.graph_url}/drives/{drive_id}/items/{folder_id}:/{file_name}:/content'
                        result = requests.put(
                            query_url,
                            headers=self.headers,
                            data=contents
                        )
                        print(f"File Created: {result.status_code}")
                else:
                    raise Exception(f"Status Code - {str(result.status_code)}. "
                                    f"The path where the file is to be created does not exist: {file_path}")

        except Exception as e:
            raise Exception(str(e))

    def delete_file(self, file_path):
        """ Delete a file in SharePoint
        :param file_path: Full path to the file to be removed. Use "/" to separate the directories
        """
        try:
            folders = self.resolve_path(file_path)
            if len(folders) < 2:
                raise Exception("Please provide a valid full path to the file")

            drive_id = self.drive_id.loc[self.drive_id['name'].str.lower().str.replace(' ', '') ==
                                         folders[0].lower().replace(' ', ''), 'id'].values[0]

            url_path = urllib.parse.quote("/".join(folders[1:]))
            query_url = f'{self.graph_url}/drives/{drive_id}/root:/{url_path}'
            result = requests.get(query_url, headers=self.headers)
            if str(result.status_code).startswith("2"):
                drive_id = result.json()['parentReference']['driveId']

                url_path = urllib.parse.quote("/".join(folders[1:]))
                query_url = f'{self.graph_url}/drives/{drive_id}/root:/{url_path}'
                result = requests.delete(query_url, headers=self.headers)

                print(f"File Deleted: {result.status_code}")

            else:
                raise Exception(f"Status Code - {str(result.status_code)}. "
                                f"The path indicated does not exist {file_path}")
        except Exception as e:
            raise Exception(str(e))

    def delete_folder(self, folder_path):
        """ Delete a folder in SharePoint
        :param folder_path: Full path to the folder to be removed. Use "/" to separate the directories
        """
        try:
            folders = self.resolve_path(folder_path)
            if len(folders) < 2:
                raise Exception("Please provide a valid full path to the file")

            drive_id = self.drive_id.loc[self.drive_id['name'].str.lower().str.replace(' ', '') ==
                                         folders[0].lower().replace(' ', ''), 'id'].values[0]

            url_path = urllib.parse.quote("/".join(folders[1:]))
            query_url = f'{self.graph_url}/drives/{drive_id}/root:/{url_path}'
            result = requests.get(query_url, headers=self.headers)
            if str(result.status_code).startswith("2"):
                drive_id = result.json()['parentReference']['driveId']

                url_path = urllib.parse.quote("/".join(folders[1:]))
                query_url = f'{self.graph_url}/drives/{drive_id}/root:/{url_path}'
                result = requests.delete(query_url, headers=self.headers)

                print(f"Folder Deleted: {result.status_code}")

            else:
                raise Exception(f"Status Code - {str(result.status_code)}. "
                                f"The path indicated does not exist {folder_path}")
        except Exception as e:
            raise Exception(str(e))

    @staticmethod
    def resolve_path(path):
        """ Resolve the path to a list of folders / files
        :param path: Full path to the directory to be created. Use "/" to separate the directories
        """
        final_path = []

        path = path.rstrip("/").lstrip("/")
        while os.path.split(path)[-1] != '':
            final_path.insert(0, os.path.split(path)[-1])
            path = os.path.split(path)[0]

        return final_path
