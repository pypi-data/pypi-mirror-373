import pandas as pd
import requests as req
import json
import re
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def response_validation(response, key=None):
    if response.status_code == 204:
        return pd.DataFrame(), str(response.status_code)
    elif str(response.status_code).startswith('2'):
        response_json = response.json()
        if key in response_json.keys():
            response_df = pd.json_normalize(response.json()[key])
        else:
            response_df = pd.json_normalize(response_json)

    else:
        raise Exception(f'Status: {response.status_code} - {response.text}')

    return response_df, str(response.status_code)


def read_webhook(webhook_json):
    incoming_id = webhook_json['id']
    message_id = webhook_json['conversation']['id'].split(';')[1].split('=')[1]
    if message_id == incoming_id:
        print('The message is a new conversation')
    else:
        print('The message is a reply to a conversation')


class MicrosoftTeams:
    """ Class to connect to Microsoft Teams """

    def __init__(self, credentials=None):
        if credentials is None:
            raise Exception('Credentials are required to connect to Teams Logging')

        if all(k in credentials for k in ("client_id", "client_secret")):
            self.client_id = credentials['client_id']
            self.client_secret = credentials['client_secret']
        else:
            raise Exception('Credentials require a client_id and client_secret to connect to Teams Logging')

        if all(k in credentials for k in ("username", "password")):
            self.username = credentials['username']
            self.password = credentials['password']
        else:
            raise Exception('Delegated credentials require a username and password to connect to Teams Logging')

        if 'organisation_id' in credentials:
            self.organisation = credentials['organisation_id']
        else:
            raise Exception('Organisation ID is required to connect to Teams Logging')

        self.session = req.Session()
        retry = Retry(total=3, status_forcelist=[429, 500, 502, 504], backoff_factor=30)
        retry.BACKOFF_MAX = 190

        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)

        self.scope = 'https://graph.microsoft.com/.default'

        self.auth_url = f"https://login.microsoftonline.com/{self.organisation}/oauth2/v2.0/token"
        self.base_url = "https://graph.microsoft.com/v1.0"

        self.delegated_headers = self.get_access_token(grant_type='password')
        self.app_headers = self.get_access_token(grant_type='client_credentials')

    def get_access_token(self, grant_type=None, user=None, password=None):
        """ Initialise MS ClientApplication object with your client_id and authority URL and return the header
            to be attached to authenticate the requests
        """
        if grant_type is None:
            grant_type = 'client_credentials'

        token_payload = f'grant_type={grant_type}&scope={self.scope}&client_id={self.client_id}' \
                        f'&client_secret={self.client_secret}'

        if grant_type == 'password':
            if user is None:
                user = self.username

            if password is None:
                password = self.password

            token_payload = token_payload + f'&username={user}&password={password}'

        token_headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        token_response = self.session.request("POST", self.auth_url, headers=token_headers, data=token_payload)
        auth_status_code = token_response.status_code

        if str(auth_status_code).startswith('2'):
            auth_access_token = 'Bearer ' + json.loads(token_response.text)['access_token']
            headers = {"Authorization": f"{auth_access_token}", "Content-Type": "application/json"}
        else:
            raise Exception(f'Error: {auth_status_code} - {token_response.text}')

        return headers

    def next_link_pagination(self, messages_response, response_df, headers):
        while "@odata.nextLink" in messages_response:
            message_response_nextLink = messages_response['@odata.nextLink']
            nextLink_response = self.session.request("GET", message_response_nextLink, headers=headers)

            if str(nextLink_response.status_code).startswith('2'):
                messages_response = nextLink_response.json()
                nextLink_df = pd.json_normalize(messages_response['value'])

                if len(nextLink_df) > 0:
                    response_df = pd.concat([response_df, nextLink_df])
                else:
                    break

        return response_df

    def session_request(self, method, url, headers, key='value', body=None):
        if method.upper() in ['POST', 'PATCH']:
            response = self.session.request(method, url, headers=self.delegated_headers, data=body)
            response_df, status_code = response_validation(response)

        else:
            response = self.session.request(method, url, headers=headers)
            response_df, status_code = response_validation(response, key=key)

            response_df = self.next_link_pagination(response.json(), response_df, headers)

        return response_df, status_code

    def get_teams(self, team_name=None):
        """ Get the teams for the organisation """
        url = f"{self.base_url}/teams"

        if team_name is not None:
            url = url + f"?$filter=displayName eq '{team_name}'"
        else:
            url = url + f"?$top=500"

        response_df, status_code = self.session_request("GET", url, self.app_headers)

        return response_df, status_code

    def get_channels(self, team_id, channel_name=None):
        """ Get the channel id for the team id passed in """
        url = f"{self.base_url}/teams/{team_id}/channels"

        if channel_name is not None:
            url = url + f"?$filter=displayName eq '{channel_name}'"

        response_df, status_code = self.session_request("GET", url, self.app_headers)

        return response_df, status_code

    def get_channel_info(self, team_id, channel_name):
        """ Get the channel info for the channel name passed in """
        url = f"{self.base_url}/teams/{team_id}/channels"
        response_df, status_code = self.session_request("GET", url, self.app_headers)
        if response_df.shape[0] > 0:
            for i, res in response_df.iterrows():
                if res['displayName'] == channel_name:
                    return pd.DataFrame(res).T, status_code
        else:
            return response_df, status_code

    def get_channel_messages(self, team_id, channel_id, message_id=None):
        """ Get the channel messages for the channel id passed in """
        url = f"{self.base_url}/teams/{team_id}/channels/{channel_id}/messages"
        if message_id is not None:
            url = url + f"/{message_id}"
        else:
            url = url + "?$top=50"

        response_df, status_code = self.session_request("GET", url, self.app_headers)

        return response_df, status_code

    def get_channel_delta_messages(self, team_id, channel_id, date_filter=None, expand=None):
        """ Get the channel messages for the channel id passed in """
        url = f"{self.base_url}/teams/{team_id}/channels/{channel_id}/messages"
        query_params = ''
        if date_filter is not None:
            query_params = query_params + f"$filter=createdDateTime ge {date_filter}"

        if expand is not None:
            if len(query_params) > 0:
                query_params = query_params + f"&$expand={expand}"
            else:
                query_params = query_params + f"$expand={expand}"

        if len(query_params) > 0:
            url = url + '?' + query_params

        response_df, status_code = self.session_request("GET", url, self.app_headers)

        return response_df, status_code

    def get_message_replies(self, team_id, channel_id, message_id):
        """ Get the message replies for the message id passed in """
        url = f"{self.base_url}/teams/{team_id}/channels/{channel_id}/messages/{message_id}/replies"
        response_df, status_code = self.session_request("GET", url, self.app_headers)

        return response_df, status_code

    def build_post_message_body(self, message, mentions=None, subject=None, importance='normal', status='Open',
                                count=1, vivantio_ticket=None):
        if vivantio_ticket is None:
            vivantio_ticket = pd.DataFrame()

        mentions_body_content = ''
        mentions_payload = []
        if mentions is not None:
            if any(ext in '@' for ext in mentions):
                filter_field = 'mail'
            else:
                filter_field = 'displayName'

            users_url = f"{self.base_url}/users"
            if len(mentions) > 0:
                users_url = users_url + '?$filter=' + ' or '.join(
                    [f'{filter_field} eq \'{user_id}\'' for user_id in mentions])

            users_response_df, status_code = self.session_request("GET", users_url, self.app_headers)

            users_response_df['request_id'] = range(0, 0 + len(users_response_df))

            mentions_payload = users_response_df.apply(
                lambda x: {
                    "id": x['request_id'],
                    "mentionText": x['displayName'],
                    "mentioned": {
                        "user": {
                            "id": x['id'],
                            "displayName": x['displayName'],
                            "userIdentityType": "aadUser"
                        }
                    }
                }, axis=1
            ).tolist()

            mentions_body_content = users_response_df.apply(
                lambda x: f"<at id=\"{x['request_id']}\">{x['displayName']}</at> ", axis=1).str.cat(sep='')

        html_message = mentions_body_content + '<br>'
        if subject is not None:
            html_message = html_message + f"<br><b>Subject:</b> {subject}<br>"

        if vivantio_ticket.shape[0] > 0:
            vivantio_ticket_id = vivantio_ticket['Id'].values[0]
            display_id = vivantio_ticket['DisplayId'].values[0]
            vivantio_ticket_url = f'https://poupart.flex.vivantio.com/item/Ticket/{vivantio_ticket_id}'
            html_message = html_message + f'<br><b>Vivantio Ticket Id:</b> {display_id}' \
                                          f'<br><b>Vivantio Ticket URL:</b> {vivantio_ticket_url}<br>'

        html_message = html_message + '<br><b>Error Status:</b> ' + status + f'<br><b>Error Count:</b> {count}' \
                                                                             f'<br><b>Error Content:</b> <br>' + message

        payload = {}
        if importance:
            payload.update({"importance": importance})

        payload.update({
            "body": {
                "contentType": "html",
                "content": html_message
            },
            "mentions": mentions_payload
        })

        return payload

    def check_for_existing_message(self, message, team_id, channel_id, message_type=None):
        list_messages, status_code = self.get_channel_messages(team_id=team_id, channel_id=channel_id)

        if list_messages.shape[0] > 0:
            if message_type == 'html':
                message = message.replace('class="dataframe"', '')
                message = re.sub('[^a-zA-Z \n\.]', '', message).replace(' ', '').lower()
                error_message_rows = list_messages[list_messages['body.content'].apply(
                    lambda x: re.sub('[^a-zA-Z \n\.]', '', x.replace(' ', '')).lower()).str.contains(message)]
            else:
                error_message_rows = list_messages[list_messages['body.content'].str.contains(message)]

            if error_message_rows.shape[0] > 0:
                error_message_rows = error_message_rows.sort_values(by='lastModifiedDateTime',
                                                                    ascending=False).reset_index(drop=True)
                teams_message = error_message_rows.loc[0]
                return True, teams_message
            else:
                return False, pd.Series()
        else:
            return False, pd.Series()

    def post_message(self, team_id, channel_id, message, subject=None, mentions=None, vivantio_ticket=None,
                     importance='normal'):
        """ Post a message to the channel id passed in """
        payload = self.build_post_message_body(message=message, subject=subject, mentions=mentions,
                                               importance=importance, vivantio_ticket=vivantio_ticket)

        url = f"{self.base_url}/teams/{team_id}/channels/{channel_id}/messages"

        response, status_code = self.session_request("POST", url, self.delegated_headers, body=json.dumps(payload))

        return response, status_code

    def update_message(self, team_id, channel_id, message_id, message=None, importance='normal', mentions=None):
        """ Update a message to the message id passed in """
        url = f"{self.base_url}/teams/{team_id}/channels/{channel_id}/messages/{message_id}"
        payload = {}
        if importance is not None:
            payload.update({"importance": importance})

        if message is not None:
            payload.update({"body": {"contentType": "html", "content": message}})

        if mentions is not None:
            payload.update({"mentions": mentions})

        if len(payload) > 0:
            response, status_code = self.session_request("PATCH", url, self.delegated_headers, body=json.dumps(payload))

            return response, status_code
        else:
            return None, None

    def post_message_reply(self, team_id, channel_id, message_id, message):
        url = f"{self.base_url}/teams/{team_id}/channels/{channel_id}/messages/{message_id}/replies"
        payload = {
            "body": {
                "contentType": "html",
                "content": message
            }
        }

        response, status_code = self.session_request("POST", url, self.delegated_headers, body=json.dumps(payload))

        return response, status_code

    def update_message_reply(self, team_id, channel_id, message_id, reply_id, message=None, importance=None):
        url = f"{self.base_url}/teams/{team_id}/channels/{channel_id}/messages/{message_id}/replies/{reply_id}"
        payload = {}
        if importance is not None:
            payload.update({"importance": importance})

        if message is not None:
            payload.update({"body": {"contentType": "html", "content": message}})

        if len(payload) > 0:
            response, status_code = self.session_request("PATCH", url, self.delegated_headers, body=json.dumps(payload))

            return response, status_code
        else:
            return None, None

    def delete_message(self, team_id, channel_id, message_id):
        url = f"{self.base_url}/teams/{team_id}/channels/{channel_id}/messages/{message_id}/softDelete"
        response, status_code = self.session_request("POST", url, self.delegated_headers)

        return response, status_code

    def undo_delete_message(self, team_id, channel_id, message_id):
        url = f"{self.base_url}/teams/{team_id}/channels/{channel_id}/messages/{message_id}/undoDelete"
        response, status_code = self.session_request("POST", url, self.delegated_headers)

        return response, status_code

    def delete_message_reply(self, team_id, channel_id, message_id, reply_id):
        url = f"{self.base_url}/teams/{team_id}/channels/{channel_id}/messages/{message_id}/replies/{reply_id}" \
              f"/softDelete"
        response, status_code = self.session_request("POST", url, self.delegated_headers)

        return response, status_code
