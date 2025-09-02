import base64
import json
import copy
import traceback
import pandas as pd
import requests
from typing import Dict
from datetime import datetime, timedelta
from msal import ClientApplication


class EmailConnection:
    """ Tooling to connect to Outlook and manage emails. Use the Graphql Outlook API """

    def __init__(self, client_id, authority, client_secret, email_user, email_password, days_back=10):
        self.client_id = client_id
        self.authority = authority
        self.client_secret = client_secret
        self.email_user = email_user
        self.email_password = email_password
        self.base_url = "https://graph.microsoft.com/v1.0"
        self.headers = self.get_headers()
        self.days_back = days_back

    def get_headers(self):
        """ Initialise MS ClientApplication object with your client_id and authority URL and return the header
            to be attached to authenticate the requests
        """
        app = ClientApplication(client_id=self.client_id, authority=self.authority,
                                client_credential=self.client_secret)
        token = app.acquire_token_by_username_password(username=self.email_user, password=self.email_password,
                                                       scopes=['.default'])
        headers = {"Authorization": f"Bearer {token['access_token']}"}
        return headers

    def get_folder_id(self, folder_name):
        """ Get the Folder Id to the indicated Folder Name
        :param folder_name: Name of the folder in the Email account
        """
        try:
            header = copy.copy(self.headers)
            params = {
                'top': 100,
                'select': 'id,displayName'
            }

            folders = folder_name.split("/")
            folder_id, folder_url = '', ''
            folder_url = f'{self.base_url}/me/mailFolders'
            for folder in folders:
                if folders.index(folder) > 0:
                    folder_url += f'/{folder_id}/childFolders'

                response = requests.get(url=folder_url, headers=header, params=params)
                if not str(response.status_code).startswith('2'):
                    raise Exception(f"Folder Not found: {folder_name}. Error Code {response.json()}")
                folders_list = pd.DataFrame(response.json()['value'])
                folder_id = folders_list.loc[folders_list['displayName'].str.lower() == folder.lower(), 'id'].values[0]

            return folder_id

        except Exception as e:
            print(e)
            raise Exception("Folder not found in email box")

    def mark_as_read(self, folder_id, message_id, read=True):
        """ Mark email messages as read/unread
        :param folder_id: Folder id where the message is contained
        :param message_id: Message id in the account
        :param read: Whether to mark the message as read or unread
        """
        header = copy.copy(self.headers)
        if read:
            read = "true"
            result = "read"
        else:
            read = "false"
            result = "unread"
        data = json.dumps({"isRead": read})

        header.update({"Content-Type": "application/json"})
        response = requests.patch(
            url=f'{self.base_url}/me/mailFolders/{folder_id}/messages/{message_id}',
            headers=header, data=data)
        if str(response.status_code).startswith("2"):
            print(f"Message marked as {result}")
        else:
            print("Message not found")

    def query_messages(self, folder_name, unread=True, mark_as_read=True, download_attachments=True,
                       extension_files=None, emails_to_query=10):
        """ Query some information about the email messages and return it in a DataFrame. It also downloads
        the attachments if indicated
        :param folder_name: Name of the folder in the Email account
        :param unread: Whether the emails to retrieve are just the unread emails (True) or any emails (False)
        :param mark_as_read: Mark read emails as read after retrieving them
        :param download_attachments: Whether to download the attachments or not
        :param extension_files: Indicate the file extensions to download and skip others
        :param emails_to_query: Number of emails to be queried when the method is called
        """
        header = copy.copy(self.headers)
        folder_id = self.get_folder_id(folder_name)

        date_to_query = (datetime.now() - timedelta(days=self.days_back)).strftime('%Y-%m-%d')
        filter_graph = f'createdDateTime ge {date_to_query}T00:00:00Z'
        if download_attachments:
            filter_graph += ' and hasAttachments eq true'
        if unread:
            filter_graph += ' and isRead eq false'
        params = {
            'top': emails_to_query,
            'select': 'id,subject,hasAttachments,createdDateTime,isRead,from,body',
            'filter': filter_graph,
            'orderby': 'createdDateTime desc'
        }
        response = requests.get(url=f'{self.base_url}/me/mailFolders/{folder_id}/messages',
                                headers=header, params=params)
        if not str(response.status_code).startswith('2'):
            raise Exception(f"No messages found in folder: {folder_name}. Error Code {response.json()}")

        emails_df = pd.DataFrame(response.json()['value'])
        if emails_df.shape[0] == 0:
            return emails_df
        emails_df['from'] = emails_df['from'].apply(lambda x: x['emailAddress']['address'])

        if mark_as_read:
            for message_id in emails_df['id'].drop_duplicates():
                self.mark_as_read(folder_id, message_id, read=True)

        if download_attachments:
            if extension_files is None:
                extension_files = ['.xls', '.xlsx', '.csv']
            elif isinstance(extension_files, list) is False:
                extension_files = [extension_files]

            # Download all attachments
            all_attachments = pd.DataFrame()
            for _, msg in emails_df.iterrows():
                response = requests.get(
                    url=f'{self.base_url}/me/mailFolders/{folder_id}/messages/{msg["id"]}/attachments',
                    headers=header)
                if not str(response.status_code).startswith('2'):
                    print(f"There are no attachments for email: {msg['subject']}. Error Code {response.json()}")
                attachments_df = pd.DataFrame(response.json()['value'])[['id', 'name', 'contentBytes']]
                attachments_df = attachments_df.assign(**{'MessageId': msg["id"]})
                attachments_df = attachments_df.loc[attachments_df['name'].str.contains('|'.join(extension_files))]
                all_attachments = pd.concat([all_attachments, attachments_df])
                for _, attachment in attachments_df.iterrows():
                    f = open(attachment['name'], 'w+b')
                    f.write(base64.b64decode(attachment['contentBytes']))
                    f.close()

            emails_df = emails_df.merge(all_attachments, left_on='id', right_on='MessageId')

            emails_df = emails_df[['createdDateTime', 'subject',
                                   'body', 'from', 'name']].rename(columns={'createdDateTime': 'ReceivedDateTime',
                                                                            'subject': 'Subject',
                                                                            'body': 'Body',
                                                                            'from': 'Sender',
                                                                            'name': 'AttachmentName'})
        else:
            # Do not download attachments
            emails_df = emails_df[['createdDateTime', 'subject',
                                   'body', 'from']].rename(columns={'createdDateTime': 'ReceivedDateTime',
                                                                    'subject': 'Subject',
                                                                    'body': 'Body',
                                                                    'from': 'Sender'})

        emails_df['ReceivedDateTime'] = pd.to_datetime(emails_df['ReceivedDateTime'])
        emails_df['ReceivedDateTime'] = emails_df['ReceivedDateTime'].dt.strftime("%Y-%m-%d %H:%M:%S")

        return emails_df

    def send_email(self, subject, body, recipient, hidden_recipient=None, attachment=None, is_html=True,
                   save_to_send_folder=False):
        """ Send an email with attachment if indicated
        :param subject: Email subject
        :param body: Email body or message
        :param recipient: Email address to whom the email will be sent
        :param hidden_recipient: Email address for the hidden recipients
        :param attachment: List of files to attach if indicated
        :param is_html: Indicate if the email body is HTML or not
        :param save_to_send_folder: Whether the sent email will be stored in the "Send" folder or not
        :return:
        """
        try:
            header = copy.copy(self.headers)
            header.update({"Content-Type": "application/json"})

            content_type = 'HTML' if is_html else 'Text'
            save = "true" if save_to_send_folder else "false"

            if isinstance(recipient, list) is False:
                recipient = [recipient]
            recipient_list = [{"emailAddress": {"address": email}} for email in recipient]

            message_body = {
                "message": {
                    "subject": f"{subject}",
                    "body": {
                        "contentType": f"{content_type}",
                        "content": f"{body}"
                    },
                    "toRecipients": recipient_list
                },
                "saveToSentItems": f"{save}"
            }

            if hidden_recipient is not None:
                if isinstance(hidden_recipient, list) is False:
                    hidden_recipient = [hidden_recipient]
                hidden_list = [{"emailAddress": {"address": email}} for email in hidden_recipient]
                bbc_dicts = {"bccRecipients": hidden_list}
                message_body['message'].update(bbc_dicts)

            if attachment is not None:
                if isinstance(attachment, list) is False:
                    attachment = [attachment]

                attachment_list = []
                for file in attachment:
                    mimetype, extension = self.get_mimetype(file)
                    if mimetype is None:
                        raise Exception("File format not allowed")

                    f = open(file, 'rb')
                    content = f.read()
                    f.close()

                    attachment_list.append(
                        {
                            "@odata.type": "#microsoft.graph.fileAttachment",
                            "name": f"{str(file).split('/')[-1]}",
                            "contentType": f"{mimetype}",
                            "contentBytes": base64.b64encode(content).decode()
                        }
                    )

                attachment_dictionary: Dict = {"attachments": attachment_list}
                message_body['message'].update(attachment_dictionary)

            response = requests.post(url=f'{self.base_url}/me/sendMail',
                                     headers=header, data=json.dumps(message_body))
            print(response.status_code)

        except Exception:
            print(traceback.format_exc())
            raise Exception("An unknown error have happened")

    def check_emails(self, folder_name, last_date=None):
        """ Check if there are outstanding emails to be queried in the folder indicated
        :param folder_name: Name of the folder in the Email account
        :param last_date: Date from which to check if there are outstanding emails
        :return:
        """
        try:
            header = copy.copy(self.headers)
            folder_id = self.get_folder_id(folder_name)

            base_url = f"https://graph.microsoft.com/v1.0/me/mailFolders/{folder_id}/messages/delta" \
                       f"?changeType=created&select=receivedDateTime,isRead"

            if last_date is not None:
                last_date = pd.to_datetime(last_date).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
                base_url += f"&filter=receivedDateTime+ge+{last_date}"

            response = requests.get(url=base_url, headers=header)
            json_resp = response.json()

            if 'value' not in json_resp.keys():
                return False
            emails_df = pd.DataFrame(json_resp['value'])
            if emails_df.shape[0] > 0:
                emails_df = emails_df.loc[emails_df['isRead'] == False]
            return emails_df.shape[0] != 0

        except Exception as e:
            print(e)

    @staticmethod
    def get_mimetype(file_path):
        """ Get the mimetype of the file to be attached to the email
        :param file_path: Path of the file to be attached
        """
        # Get mimetype
        if ('.jpg' in file_path) | ('.jpeg' in file_path):
            mimetype = "image/jpeg"
            extension = '.jpeg'
        elif '.png' in file_path:
            mimetype = "image/png"
            extension = '.png'
        elif '.doc' in file_path:
            mimetype = "application/msword"
            extension = '.doc'
        elif '.docx' in file_path:
            mimetype = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            extension = '.docx'
        elif '.pdf' in file_path:
            mimetype = "application/pdf"
            extension = '.pdf'
        elif '.txt' in file_path:
            mimetype = "text/plain"
            extension = '.txt'
        elif '.csv' in file_path:
            mimetype = "text/csv"
            extension = '.csv'
        elif '.xls' in file_path:
            mimetype = "application/vnd.ms-excel"
            extension = '.xls'
        elif '.xlsx' in file_path:
            mimetype = "application/vnd.ms-excel"
            extension = '.xlsx'
        elif '.html' in file_path:
            mimetype = "application/vnd.ms-excel"
            extension = 'text/html'
        else:
            raise Exception('File mime type not found')

        return mimetype, extension
