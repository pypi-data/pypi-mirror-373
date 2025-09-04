from dotenv import load_dotenv
import requests
import os

class SharePointClient:
    """
    Not used anymore...

    Was used in the process of creating the initial 
    code for setting up a SharePoint connection.
    Can be removed. Did not manage to remove so far.
    """

    def __init__(self, tenant_id, client_id, client_secret, resource_url):
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.resource_url = resource_url
        self.base_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
        self.headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        self.access_token = self.get_access_token()
        self.token_headers = {'Authorization': f'Bearer {self.access_token}'}
        self.graph_url = "https://graph.microsoft.com/v1.0/sites"


    def get_access_token(self):
        # Body for the access token request
        body = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'scope': self.resource_url + '.default'
        }
        response = requests.post(self.base_url, headers=self.headers, data=body)
        return response.json().get('access_token')  # Extract access token from the response
    

    def get_site_id(self, site_url):
        # Build URL to request site ID
        full_url = f'{self.graph_url}/{site_url}'
        response = requests.get(full_url, headers=self.token_headers)
        return response.json().get('id')  # Return the site ID


    def get_drive_id(self, site_id):
        # Retrieve drive IDs and names associated with a site
        drives_url = f'{self.graph_url}/{site_id}/drives'
        response = requests.get(drives_url, headers=self.token_headers)
        drives = response.json().get('value', [])
        return [(drive['id'], drive['name']) for drive in drives]


    def get_folder_content(self, site_id, drive_id, folder_path='root'):
        # Get the contents of a folder
        folder_url = f'{self.graph_url}/{site_id}/drives/{drive_id}/root/children'
        response = requests.get(folder_url, headers=self.token_headers)
        items_data = response.json()
        rootdir = []
        if 'value' in items_data:
            for item in items_data['value']:
                rootdir.append((item['id'], item['name']))
        return rootdir
    

    # Recursive function to browse folders
    def list_folder_contents(self, site_id, drive_id, folder_id, level=0):
        # Get the contents of a specific folder
        folder_contents_url = f'{self.graph_url}/{site_id}/drives/{drive_id}/items/{folder_id}/children'
        contents_headers = self.token_headers
        contents_response = requests.get(folder_contents_url, headers=contents_headers)
        folder_contents = contents_response.json()

        items_list = []  # List to store information

        if 'value' in folder_contents:
            for item in folder_contents['value']:
                if 'folder' in item:
                    # Add folder to list
                    items_list.append({'name': item['name'], 'type': 'Folder', 'mimeType': None})
                    # Recursive call for subfolders
                    items_list.extend(self.list_folder_contents(site_id, drive_id, item['id'], level + 1))
                elif 'file' in item:
                    # Add file to the list with its mimeType
                    items_list.append({'name': item['name'], 'type': 'File', 'mimeType': item['file']['mimeType']})

        return items_list
    

    def download_file(self, download_url, local_path, file_name):
        headers = self.token_headers
        response = requests.get(download_url, headers=headers)
        if response.status_code == 200:
            full_path = os.path.join(local_path, file_name)
            with open(full_path, 'wb') as file:
                file.write(response.content)
            print(f"File downloaded: {full_path}")
        else:
            print(f"Failed to download {file_name}: {response.status_code} - {response.reason}")
    

    def download_folder_contents(self, site_id, drive_id, folder_id, local_folder_path, level=0):
        # Recursively download all contents from a folder
        folder_contents_url = f'{self.graph_url}/{site_id}/drives/{drive_id}/items/{folder_id}/children'
        contents_headers = self.token_headers
        contents_response = requests.get(folder_contents_url, headers=contents_headers)
        folder_contents = contents_response.json()

        if 'value' in folder_contents:
            for item in folder_contents['value']:
                if 'folder' in item:
                    new_path = os.path.join(local_folder_path, item['name'])
                    if not os.path.exists(new_path):
                        os.makedirs(new_path)
                    self.download_folder_contents(site_id, drive_id, item['id'], new_path, level + 1)  # Recursive call for subfolders
                elif 'file' in item:
                    file_name = item['name']
                    file_download_url = f"{self.resource_url}/v1.0/sites/{site_id}/drives/{drive_id}/items/{item['id']}/content"
                    self.download_file(file_download_url, local_folder_path, file_name)


def test_sharepoint_client():
    # Usage of the class
    load_dotenv()
    tenant_id = os.getenv('CLIENT_ID')
    client_id = os.getenv('TENANT_ID')
    client_secret = os.getenv('GRAPH_CLIENT_SECRET')
    resource = 'https://graph.microsoft.com/'

    client = SharePointClient(tenant_id, client_id, client_secret, resource)

    site_id = "otcfin1.sharepoint.com,e6dadbba-d556-4282-bbbd-2524af8466ca,ecc3a3bf-ec4b-4ab8-910d-6f656ddbdf72"
    drive_id = "b!utva5lbVgkK7vSUkr4Rmyr-jw-xL7LhKkQ1vZW3b33J3_ie0A3MDS4uuoNVIHXeL"
    folder_id = "017DZBVPFPS23VFCAHI5BJ32WSP2OXVFSD"

    r = client.download_folder_contents(site_id, drive_id, folder_id, "")
    print(r)