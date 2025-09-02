import pandas as pd
import datetime
from bs4 import BeautifulSoup


class VivantioLogging:
    """ Manage Error Logs in Vivantio """

    def __init__(self, vivantio_connection):
        if vivantio_connection is None:
            raise Exception('A connection to the Vivantio class is required to connect to Vivantio Logging')
        else:
            self.vivantio_con = vivantio_connection

    def check_for_existing_message(self, message, record_type_id=11, client_id=60, status_id=122, category_id=1769,
                                   error_id=None):
        list_messages = self.vivantio_con.get_tickets(record_type_id=record_type_id, client_id=client_id,
                                                      status_id=status_id, category_id=category_id)

        if error_id:
            error_message_rows = list_messages[list_messages['Title'].str.contains(error_id)]
        else:
            error_message_rows = list_messages[list_messages['DescriptionHtml'].str.contains(message)]

        if error_message_rows.shape[0] > 0:
            error_message_rows = error_message_rows.sort_values(by='LastModifiedDate',
                                                                ascending=False).reset_index(drop=True)
            vivantio_message = error_message_rows.loc[0]
            return True, vivantio_message
        else:
            return False, pd.Series()

    def update_existing_ticket(self, existing_message, severity):
        ticket_id = existing_message['Id']
        if severity == 'High Priority':
            importance = 'High Priority'
        else:
            importance = 'Standard Priority'

        ticket_notes = self.vivantio_con.get_ticket_notes(ticket_id)
        if ticket_notes.shape[0] > 0:
            error_counts = ticket_notes[ticket_notes['Notes'].str.contains('Count')]

            if error_counts.shape[0] > 0:
                error_count = int(error_counts['Notes'].values[0].split(': ')[1])

                ticket_response = self.vivantio_con.add_note_ticket(ticket_id, f'Error Count: {error_count + 1}')

                if error_count >= 3:
                    importance = 'High Priority'

                priority_ids = self.vivantio_con.get_priorities(record_type_id=11)
                priority_df = priority_ids[priority_ids['Name'] == importance]
                if priority_df.shape[0] > 0:
                    priority_id = priority_df['Id'].values[0]
                    ticket_response = self.vivantio_con.update_ticket_priority(ticket_id=ticket_id,
                                                                               priority_id=priority_id)

            else:
                ticket_response = self.vivantio_con.add_note_ticket(ticket_id, 'Error Count: 1')
        else:
            ticket_response = self.vivantio_con.add_note_ticket(ticket_id, 'Error Count: 1')

        return ticket_response

    def create_ticket(self, title, category_name=None, severity='Standard Priority', **data):
        """ Create a ticket to System Errors
        :param title: Title of the Vivantio ticket that will be created
        :param category_name: Sub category of System Errors to create the ticket under
        :param severity: Severity of the message to be posted to the channel (normal, high)
        :param data: Dictionary of data to be posted to the channel
            {'message': 'message to be posted to the channel', 'RunTime': '%Y-%m-%d %H:%M:%S',
            'Project': 'Project Name', 'Section': 'Section Name', 'Pipeline': 'Pipeline Name'}
        """
        if 'message' not in data:
            raise Exception('Data input dictionary must be provided, including message as a key')

        if title is None:
            raise Exception('title is required')

        if category_name is None:
            category_name = 'System Errors'
        elif 'System Errors' not in category_name:
            category_name = f'System Errors: {category_name}'

        vivantio_categories = self.vivantio_con.get_categories(record_type_id=11)
        category_df = vivantio_categories[vivantio_categories['Name'] == category_name]

        if category_df.shape[0] > 0:
            category_id = category_df['Id'].values[0]
        else:
            raise Exception(f'Category {category_name} not found in Vivantio')

        message = data['message']
        is_message_html = bool(BeautifulSoup(message, "html.parser").find())

        error_id = data.get('ErrorId', None)

        if is_message_html:
            html_message = message
        else:
            if 'RunTime' not in data.keys():
                data['RunTime'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            html_message = pd.DataFrame.from_dict(data, orient='index').T.to_html(index=False)

        exists, existing_message = self.check_for_existing_message(message=message, category_id=category_id,
                                                                   error_id=error_id)

        if exists:
            ticket_response = self.update_existing_ticket(existing_message, severity)

            return ticket_response
        else:
            vivantio_priorities = self.vivantio_con.get_priorities(record_type_id=11)
            priority_df = vivantio_priorities[vivantio_priorities['Name'] == severity]

            if priority_df.shape[0] > 0:
                priority_id = priority_df['Id'].values[0]
            else:
                raise Exception(f'Priority {severity} not found in Vivantio')

            ticket_response = self.vivantio_con.create_ticket(title=title, message=html_message,
                                                              category_id=category_id, priority_id=priority_id)

            return ticket_response
