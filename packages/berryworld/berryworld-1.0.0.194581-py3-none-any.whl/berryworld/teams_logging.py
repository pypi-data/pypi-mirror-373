import pandas as pd
import datetime
import re
from bs4 import BeautifulSoup


def build_existing_update_message(existing_message, html_message):
    message_id = existing_message['id']
    year_month_day = datetime.datetime.now().strftime('%Y-%m-%d')
    last_run_time = re.search(f'<td>{year_month_day}(.*)</td>', html_message)
    if last_run_time:
        last_run_time = year_month_day + last_run_time.group(1)
    else:
        last_run_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    html_message = existing_message['body.content']
    mentions = existing_message['mentions']
    importance = 'normal'
    if 'Error Count' in existing_message['body.content']:
        find_count = re.search('Error Count:</b>(.*)<br>', existing_message['body.content'])
        if find_count:
            count_number = find_count.group(1)
            new_count = int(count_number) + 1
            find_last_run_time = re.search('Latest RunTime:</b>(.*)<br>', existing_message['body.content'])
            if find_last_run_time:
                html_message = html_message.replace(f'Latest RunTime:</b>{find_last_run_time.group(1)}<br>',
                                                    f'Latest RunTime:</b> {last_run_time}<br>')

                html_message = html_message.replace(f'Error Count:</b>{count_number}<br>',
                                                    f'Error Count:</b> {new_count}<br>')
            else:
                html_message = html_message.replace(f'Error Count:</b>{count_number}<br>',
                                                    f'Latest RunTime:</b> {last_run_time}<br>'
                                                    f'<b>Error Count:</b> {new_count}<br>')

            if int(count_number) >= 3:
                importance = 'high'

    return message_id, html_message, mentions, importance


class TeamsLogging:
    """ Manage Error Logs in Microsoft Teams """

    def __init__(self, teams_connection, vivantio_connection=None):
        if teams_connection is None:
            raise Exception('A connection to the Microsoft Teams class is required to connect to Teams Logging')
        else:
            self.ms_teams_con = teams_connection

        self.vivantio = False
        if vivantio_connection:
            self.vivantio = True
            self.vivantio_con = vivantio_connection

    def upload_message(self, team_name, channel_name, subject, mentions=None, severity='normal', **data):
        """ Post a message to the channel id passed in
        :param team_name: Name of the Team to post the message to
        :param channel_name: Name of the team's channel to post the message to
        :param subject: Subject to be included in the teams message and as the Vivantio ticket title if connected
        :param mentions: List of user display names or email addresses to be mentioned in the message
        :param severity: Severity of the message to be posted to the channel (normal, high)
        :param data: Dictionary of data to be posted to the channel
            {'message': 'message to be posted to the channel', 'RunTime': '%Y-%m-%d %H:%M:%S',
            'Project': 'Project Name', 'Section': 'Section Name', 'Pipeline': 'Pipeline Name'}
        """
        if 'message' not in data:
            raise Exception('Data input dictionary must be provided, including message as a key')

        if subject is None:
            raise Exception('subject is required')

        if severity not in ['normal', 'high']:
            severity = 'normal'

        message = data['message']
        is_message_html = bool(BeautifulSoup(message, "html.parser").find())

        if is_message_html:
            html_message = message
        else:
            if 'RunTime' not in data.keys():
                data['RunTime'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            html_message = pd.DataFrame.from_dict(data, orient='index').T.to_html(index=False)

        team_response_df, status_code = self.ms_teams_con.get_teams(team_name=team_name)
        team_id = team_response_df['id'].values[0]

        channel_response_df, status_code = self.ms_teams_con.get_channel_info(team_id=team_id,
                                                                              channel_name=channel_name)
        channel_id = channel_response_df['id'].values[0]

        if not is_message_html:
            exists, existing_message = self.ms_teams_con.check_for_existing_message(message=message, team_id=team_id,
                                                                                    channel_id=channel_id)
        else:
            exists, existing_message = self.ms_teams_con.check_for_existing_message(message=html_message,
                                                                                    team_id=team_id,
                                                                                    channel_id=channel_id,
                                                                                    message_type='html')

        if exists:
            message_id, html_message, mentions, importance = build_existing_update_message(existing_message,
                                                                                           html_message)

            if importance == 'high':
                severity = 'high'

            update_message, update_message_status = self.ms_teams_con.update_message(team_id=team_id,
                                                                                     channel_id=channel_id,
                                                                                     message_id=message_id,
                                                                                     message=html_message,
                                                                                     importance=severity,
                                                                                     mentions=mentions)

            return update_message, update_message_status
        else:
            vivantio_ticket_info = None
            if self.vivantio:
                vivantio_ticket_df = self.vivantio_con.create_ticket(title=subject, message=html_message)
                vivantio_ticket_id = vivantio_ticket_df['InsertedItemId'].values[0]
                vivantio_ticket_info = self.vivantio_con.get_ticket(vivantio_ticket_id)

            new_message, new_message_status = self.ms_teams_con.post_message(team_id=team_id, channel_id=channel_id,
                                                                             message=html_message, subject=subject,
                                                                             mentions=mentions,
                                                                             vivantio_ticket=vivantio_ticket_info,
                                                                             importance=severity)

            return new_message, new_message_status
