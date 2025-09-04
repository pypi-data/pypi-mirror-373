import requests as req
import json
import pandas as pd
import datetime


class Vivantio:
    def __init__(self, token=None):
        if token is None:
            raise Exception('Token is required to connect to DevOps')

        self.headers = {
            'Authorization': 'Basic ' + token,
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0'
        }

        self.base_url = 'https://webservices-na01.vivantio.com/api'

    def session_request(self, method, url, headers=None, data=None):
        if headers is None:
            headers = self.headers

        if data is None:
            response = req.request(method, url, headers=headers)
        else:
            response = req.request(method, url, headers=headers, json=data)

        if str(response.status_code).startswith('2'):
            return response
        else:
            raise Exception(f'Status: {response.status_code} - {response.text}')

    def get_clients(self, record_type_id=None):
        items = []
        if record_type_id is not None:
            items.append({"FieldName": "RecordTypeId", "Op": "Equals", "Value": record_type_id})

        client_query = json.dumps(
            {
                "Query": {
                    "Items": items,
                    "Mode": "MatchAll"
                }
            }
        )

        url = f'{self.base_url}/Client/Select'
        response = self.session_request('POST', url, data=json.loads(client_query))
        response = response.json()
        response_df = pd.json_normalize(response['Results'])

        return response_df

    def get_categories(self, record_type_id=None):
        if record_type_id is None:
            raise Exception('Record Type ID is required to get categories')

        url = f'{self.base_url}/Configuration/CategorySelectByRecordTypeId/{record_type_id}'
        response = self.session_request('POST', url)
        response = response.json()
        response_df = pd.json_normalize(response['Results'])

        return response_df

    def get_priorities(self, record_type_id=None):
        if record_type_id is None:
            raise Exception('Record Type ID is required to get priorities')

        url = f'{self.base_url}/Configuration/PrioritySelectByRecordTypeId/{record_type_id}'
        response = self.session_request('POST', url)
        response = response.json()
        response_df = pd.json_normalize(response['Results'])

        return response_df

    def get_statuses(self, record_type_id=None):
        if record_type_id is None:
            raise Exception('Record Type ID is required to get statuses')

        url = f'{self.base_url}/Configuration/StatusSelectByRecordTypeId/{record_type_id}'
        response = self.session_request('POST', url)
        response = response.json()
        response_df = pd.json_normalize(response['Results'])

        return response_df

    def get_tickets(self, record_type_id=None, client_id=None, open_date=None, close_date=None,
                    last_modified_date=None, status_id=None, category_id=None, priority_id=None):
        items = []
        if record_type_id is not None:
            items.append({"FieldName": "RecordTypeId", "Op": "Equals", "Value": int(record_type_id)})
        if client_id is not None:
            items.append({"FieldName": "ClientId", "Op": "Equals", "Value": int(client_id)})
        if open_date is not None:
            items.append({"FieldName": "OpenDate", "Op": "GreaterThanOrEqualTo", "Value": open_date})
        if close_date is not None:
            items.append({"FieldName": "CloseDate", "Op": "LessThanOrEqualTo", "Value": close_date})
        if last_modified_date is not None:
            items.append({"FieldName": "LastModifiedDate", "Op": "LessThanOrEqualTo", "Value": last_modified_date})
        if status_id is not None:
            items.append({"FieldName": "StatusId", "Op": "Equals", "Value": int(status_id)})
        if category_id is not None:
            items.append({"FieldName": "CategoryId", "Op": "Equals", "Value": int(category_id)})
        if priority_id is not None:
            items.append({"FieldName": "PriorityId", "Op": "Equals", "Value": int(priority_id)})

        ticket_query = json.dumps(
            {
                "Query": {
                    "Items": items,
                    "Mode": "MatchAll"
                }
            }
        )

        url = f'{self.base_url}/Ticket/Select'
        response = self.session_request('POST', url, data=json.loads(ticket_query))
        response = response.json()
        response_df = pd.json_normalize(response['Results'])

        return response_df

    def get_ticket(self, ticket_id):
        url = f'{self.base_url}/Ticket/SelectById/{ticket_id}'
        response = self.session_request('POST', url)

        response = response.json()
        response_df = pd.json_normalize(response['Item'])

        return response_df

    def get_ticket_notes(self, ticket_id):
        url = f'{self.base_url}/Ticket/ActionSelectByParentId/{ticket_id}?includePrivate=True&includeAttachments=False'

        response = self.session_request('POST', url)

        response = response.json()
        response_df = pd.json_normalize(response['Results'])
        notes_df = response_df.loc[~response_df['Notes'].isnull()]
        notes_df = notes_df.sort_values(by='ActionDate', ascending=False).reset_index(drop=True)

        return notes_df

    def get_config_info(self, record_type_id, extension='category'):
        url = f'{self.base_url}/Configuration/'
        if extension.lower() == 'priority':
            url += f'CategorySelectByRecordTypeId/{record_type_id}'
        else:
            url += f'PrioritySelectByRecordTypeId/{record_type_id}'

        response = self.session_request('POST', url)

        response = response.json()
        response_df = pd.json_normalize(response['Results'])

        return response_df

    def get_sla_info(self, extension='sla', ticket_id=None):
        if extension.lower() == 'priority':
            url = f'{self.base_url}/Configuration/SLAStageTargetSelectByPriority/{ticket_id}'
        else:
            url = f'{self.base_url}/Ticket/SLAStageInstanceSelectByTicket/{ticket_id}'

        response = self.session_request('POST', url)

        response = response.json()
        response_df = pd.json_normalize(response['Results'])

        return response_df

    def create_ticket(self, title, message, category_id=None, priority_id=None):
        if title is None:
            raise Exception('Ticket title is required')

        if message is None:
            raise Exception('Ticket message is required')

        if category_id is None:
            category_id = 1769  # System Errors

        if priority_id is None:
            priority_id = 81  # 81 Normal - 94 High Priority

        ticket_payload = {
            "RecordTypeId": 11,
            "ClientId": 60,  # Poupart IT
            "OpenDate": datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
            "Title": title,
            "CallerName": "Data Alert",
            "CallerEmail": "Data.Alert@poupart.onmicrosoft.com",
            "StatusId": 122,  # Open
            "PriorityId": priority_id,
            "CategoryId": category_id
        }

        if message is not None:
            if isinstance(message, pd.DataFrame):
                message = message.to_html()
            ticket_payload['DescriptionHtml'] = message

        ticket_payload = json.dumps(ticket_payload)

        url = f'{self.base_url}/Ticket/Insert'
        response = self.session_request('POST', url, data=json.loads(ticket_payload))

        response = response.json()
        response_df = pd.DataFrame.from_dict(response, orient='index').T

        return response_df

    def add_note_ticket(self, ticket_id, message=None):
        if message is None:
            raise Exception('An update message is required')

        url = f'{self.base_url}/Ticket/AddNote'
        ticket_payload = json.dumps(
            {
                "AffectedTickets": [int(ticket_id)],
                "Date": datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
                "Notes": message
            }
        )

        response = self.session_request('POST', url, data=json.loads(ticket_payload))
        response = response.json()
        response_df = pd.DataFrame([response])

        return response_df

    def update_ticket_priority(self, ticket_id, priority_id):
        url = f'{self.base_url}/Ticket/ChangePriority'
        ticket_payload = json.dumps(
            {
                "AffectedTickets": [int(ticket_id)],
                "PriorityId": int(priority_id)
            }
        )

        response = self.session_request('POST', url, data=json.loads(ticket_payload))
        response = response.json()
        response_df = pd.DataFrame([response])

        return response_df

    def close_ticket(self, ticket_id, message=None):
        if message is None:
            raise Exception('A close message is required')

        open_status_url = f'{self.base_url}/Ticket/ChangeStatus'
        status_payload = json.dumps(
            {
                "AffectedTickets": [int(ticket_id)],
                "Date": datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
                "StatusId": 122
            }
        )
        response = self.session_request('POST', open_status_url, data=json.loads(status_payload))
        if str(response.status_code).startswith('2'):
            url = f'{self.base_url}/Ticket/Close'
            ticket_payload = json.dumps(
                {"AffectedTickets": [int(ticket_id)],
                 "CloseStatusId": 124,
                 "CloseDate": datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
                 "Notes": message
                 }
            )

            response = self.session_request('POST', url, data=json.loads(ticket_payload))

        response = response.json()
        response_df = pd.DataFrame([response])

        return response_df

    def delete_ticket(self, ticket_id):
        url = f'{self.base_url}/Ticket/Delete'

        delete_payload = json.dumps(
            {
                "AffectedTickets": [
                    int(ticket_id)
                ],
                "Date": datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
            }, default=str
        )

        response = self.session_request('DELETE', url, data=json.loads(delete_payload))
        response = response.json()
        response_df = pd.DataFrame([response])

        return response_df
