import math
import requests as req
import json
import pandas as pd
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class PowerAutomate:
    def __init__(self, filter_limit=15, **kwargs):
        """
        Manage Power Automate Flows.
        :param filter_limit: Limit of items to be filtered in a request
        :param kwargs: Dictionary containing the info to connect to the Power Automate API
            - organisation_id: ID of the organisation as defined in Azure (Directory (tenant) ID)
            - client_id: ID of the client as defined in Azure (Application (client) ID)
            - client_secret: Secret of the client as created in Azure
            - username: Username of the user to be used to generate the bearer token
            - password: Password of the user to be used to generate the bearer token
            - environment_name: Name of the environment as defined in Power Automate
            - environment_id: ID of the environment as defined in Power Automate
            - business_unit: Business Unit of the environment as defined in Power Automate
        """
        if kwargs != {}:
            try:
                self.organisation_id = kwargs['organisation_id']
                self.environment_id = kwargs['environment_id']
                self.environment_name = kwargs['environment_name']

                self.client_id = kwargs['client_id']
                self.client_secret = kwargs['client_secret']

                self.grant_type = 'password'
                if all([key_ in kwargs.keys() for key_ in ['username', 'password']]):
                    self.username = kwargs['username']
                    self.password = kwargs['password']
                elif all([key_ in kwargs.keys() for key_ in ['business_unit']]):
                    self.grant_type = 'client_credentials'
                    self.business_unit = kwargs['business_unit']
            except KeyError as ke:
                raise KeyError("Missing parameter: %s" % str(ke))
        else:
            raise KeyError('Please provide a value for each of these variables: organisation_id, environment_id, '
                           'environment_name, client_id, client_secret.\n'
                           'If the grant_type is delegated then please also provide username, password.\n'
                           'If grant_type is set up to client credentials, then please provide business_unit')

        self.session = req.Session()
        retry = Retry(total=3, status_forcelist=[429, 500, 502, 504], backoff_factor=30)
        retry.BACKOFF_MAX = 190

        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)

        # Set API version
        self.api_version = 'api-version=2016-11-01'

        # Limit of elements to get each call
        self.filter_limit = filter_limit

        # URL to get a bearer token
        self.token_url = f'https://login.microsoftonline.com/{self.organisation_id}/oauth2/v2.0/token'

        # Base URL to get the flows
        self.base_flow_url = f'https://api.flow.microsoft.com/providers/Microsoft.ProcessSimple'

        # Base URL to edit the flows
        self.base_edit_url = 'https://make.powerautomate.com/'

        self.headers = self.generate_bearer_token(self.grant_type)

    def generate_bearer_token(self, grant_type, scope=None):
        """ Generate a bearer token to be used in the headers of the requests
        :param grant_type: Type of grant to be used to generate the token
        :param scope: Scope of the token to be generated
        """
        bearer_payload = f'grant_type={grant_type}&client_id={self.client_id}&client_secret={self.client_secret}'

        if grant_type == 'client_credentials':
            if scope is None:
                scope = 'https://management.azure.com/.default'
            bearer_payload = bearer_payload + f'&scope={scope}'
        else:
            if scope is None:
                scope = 'https://service.flow.microsoft.com/.default'
            bearer_payload = bearer_payload + f'&username={self.username}' \
                                              f'&password={self.password}&scope={scope}'

        bearer_headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        token_response = self.session.request("POST", self.token_url, headers=bearer_headers, data=bearer_payload)
        auth_status_code = token_response.status_code

        if str(auth_status_code).startswith('2'):
            auth_access_token = 'Bearer ' + json.loads(token_response.text)['access_token']
            headers = {"Authorization": f"{auth_access_token}", "Content-Type": "application/json"}
        else:
            raise Exception(f'Error: {auth_status_code} - {token_response.text}')

        return headers

    def paginate(self, response):
        """ Paginate the response of the API
        :param response: Response from the API call
        """
        paginated_df = pd.DataFrame()

        pagination_keys = ['@odata.nextLink', '@odata.deltaLink', 'nextLink']
        pagination_response = response.copy()
        while any([key in pagination_response for key in pagination_keys]):
            link_key = pagination_keys[([key in pagination_response for key in pagination_keys]).index(True)]
            pagination_response = self.session.request("GET", pagination_response[link_key], headers=self.headers)
            pagination_response = json.loads(pagination_response.text)['value']
            paginated_df = pd.concat([paginated_df, pd.DataFrame(pagination_response)])

        return paginated_df

    def session_request(self, method, url, headers=None, data=None):
        """ Make a request to the API
        :param method: Method of the request
        :param url: URL of the request
        :param headers: Headers of the request
        :param data: Data of the request
        """
        if headers is None:
            headers = self.headers

        if data is None:
            response = self.session.request(method, url, headers=headers)
        else:
            response = self.session.request(method, url, headers=headers, data=data)

        if response.status_code == 204:
            return pd.DataFrame()
        elif str(response.status_code).startswith('2'):
            response = (json.loads(response.text))
            if 'value' in response:
                response_df = pd.DataFrame(response['value'])
            elif isinstance(response, list):
                response_df = pd.DataFrame(response)
            else:
                response_df = pd.DataFrame([response])

            paginated_response_df = self.paginate(response)
            if len(paginated_response_df) > 0:
                response_df = pd.concat([response_df, paginated_response_df]).reset_index(drop=True)
        else:
            raise Exception(f'Status: {response.status_code} - {response.text}')

        return response_df

    def list_flow_owners(self, flow_id):
        """ List the owners of a flow
        :param flow_id: ID of the flow to get the owners from
        """
        flow_url = f'{self.base_flow_url}/scopes/admin/environments/{self.environment_id}/flows/{flow_id}/' \
                   f'owners?{self.api_version}'

        flow_owners_response = self.session_request("GET", flow_url).to_dict(orient='records')
        flow_user_ids = []
        flow_group_ids = []

        for owner in flow_owners_response:
            if 'principal' in owner['properties']:
                principal_type = owner['properties']['principal'].get('type', None)
                if principal_type == 'User':
                    flow_user_ids.append(owner['name'])
                elif principal_type == 'Group':
                    flow_group_ids.append(owner['name'])

        return flow_user_ids, flow_group_ids

    def list_graph_accounts(self, account_type, account_ids=None):
        """ List the accounts of a type
        :param account_type: Type of account to get the information from
        :param account_ids: IDs of the accounts to get the information from
        """
        accounts_df = pd.DataFrame()

        if account_ids is not None:
            headers = self.generate_bearer_token(grant_type='client_credentials',
                                                 scope='https://graph.microsoft.com/.default')

            remaining_ids = [user_id for user_id in account_ids if user_id]

            while remaining_ids:
                graph_url = f'https://graph.microsoft.com/v1.0/{account_type.lower()}?$top=999'
                graph_url += '&$filter=' + ' or '.join([f"id eq '{user_id}'" for user_id in remaining_ids])

                try:
                    result = self.session_request("GET", graph_url, headers=headers)
                    if isinstance(result, pd.DataFrame):
                        accounts_df = pd.concat([accounts_df, result], ignore_index=True)
                    else:
                        accounts_df = pd.concat([accounts_df, pd.DataFrame(result)], ignore_index=True)
                    break
                except Exception as e:
                    error_message = str(e)
                    if '404' in error_message and 'Request_ResourceNotFound' in error_message and len(remaining_ids) > 1:
                        for user_id in remaining_ids.copy():
                            try:
                                single_url = f"https://graph.microsoft.com/v1.0/{account_type.lower()}?$filter=id eq '{user_id}'"
                                self.session_request("GET", single_url, headers=headers)
                            except Exception as error_message1:
                                if '404' in str(error_message1) and 'Request_ResourceNotFound' in error_message1:
                                    remaining_ids.remove(user_id)
                                    break

        return accounts_df

    def enrich_owners(self, flows_df):
        """ Enrich the owners of the flows
        :param flows_df: DataFrame containing the flows information
        """
        accounts_df = pd.DataFrame()
        user_ids = []
        group_ids = []

        # Get Flow Owners
        flows_df['Owners'] = None
        for i, flow in flows_df.iterrows():
            flow_user_ids, flow_group_ids = self.list_flow_owners(flow['FlowId'])
            flows_df.at[i, 'Owners'] = (flow_user_ids + flow_group_ids)

            user_ids = set(list(user_ids) + flow_user_ids)
            group_ids = set(list(group_ids) + flow_group_ids)

        # Get User Account information
        if len(user_ids) > 0:
            user_ids = list(dict.fromkeys(user_ids))
            batch_steps = math.ceil(len(user_ids) / self.filter_limit)
            for batch in range(batch_steps):
                batch_user_ids = user_ids[batch * self.filter_limit:(batch + 1) * self.filter_limit]
                accounts_df = pd.concat([accounts_df, self.list_graph_accounts('users', batch_user_ids)])

        # Get Group Account information
        if len(group_ids) > 0:
            group_ids = list(dict.fromkeys(group_ids))
            batch_steps = math.ceil(len(group_ids) / 15)
            for batch in range(batch_steps):
                batch_group_ids = group_ids[batch * 15:(batch + 1) * 15]
                accounts_df = pd.concat([accounts_df, self.list_graph_accounts('groups', batch_group_ids)])

        # Get Creator
        flows_df['CreatedById'] = flows_df['FlowProperties'].apply(
            lambda x: x['creator']['userId'] if 'creator' in x else None)
        flows_df = flows_df.merge(
            accounts_df[['displayName', 'id']].rename(columns={'id': 'CreatedById'}).drop_duplicates(),
            how='left', on='CreatedById')
        flows_df.rename(columns={'displayName': 'CreatedBy'}, inplace=True)

        if accounts_df.shape[0] > 0:
            flows_df = flows_df.explode('Owners')
            flows_df = flows_df.merge(accounts_df[['displayName', 'id']], how='left',
                                      left_on='Owners', right_on='id', suffixes=('', '_account'))

            # Remove null owners
            null_account_mask = flows_df['displayName'].isnull()
            flow_name_mask = flows_df.groupby('FlowId')['FlowId'].transform('count') > 1
            flows_df = flows_df[~(null_account_mask & flow_name_mask)]

            flows_df = flows_df[flows_df['displayName'].notna()]
            flows_df = flows_df.groupby(['FlowId', 'id', 'type', 'CreatedBy']).agg({
                'displayName': list, 'FlowProperties': list}).reset_index()
            flows_df.rename(columns={'displayName': 'Owners'}, inplace=True)

        return flows_df

    @staticmethod
    def enrich_info(flows_df):
        """ Enrich the flows with the information
        :param flows_df: DataFrame containing the flows information
        """
        if 'FlowProperties' in flows_df.columns:
            flows_info_df = pd.DataFrame()
            flows_list = []
            for _, prop in flows_df[['FlowId', 'FlowProperties']].iterrows():
                flow_info_response = prop['FlowProperties']
                if isinstance(flow_info_response, list) & (len(flow_info_response) > 0):
                    flow_info_response = flow_info_response[0]
                flow_info = {'FlowId': prop['FlowId']}
                for key in flow_info_response.keys():
                    if isinstance(flow_info_response[key], (dict, list, bool)):
                        flow_info[key] = [flow_info_response[key]]
                    else:
                        if len(flow_info_response[key]) > 0:
                            flow_info[key] = flow_info_response[key]

                flows_list.append(flow_info)
                flows_info_df = pd.DataFrame(flows_list)

            flows_df = pd.merge(flows_df, flows_info_df, on='FlowId', how='left')

        return flows_df

    def enrich_run_history(self, flows_df):
        """ Enrich the flows with the run history
        :param flows_df: DataFrame containing the flows information
        """
        flows_runs_df = pd.DataFrame()
        for _, flow in flows_df.iterrows():
            flow_url = f'{self.base_flow_url}/scopes/admin/environments/{self.environment_id}/flows/{flow["FlowId"]}/' \
                       f'runs?{self.api_version}'

            run_info_df = self.session_request("GET", flow_url)
            if run_info_df.shape[0] > 0:
                run_info_df.rename(columns={'properties': 'RunProperties'}, inplace=True)
                run_info_df['ErrorCount'] = run_info_df['RunProperties'].apply(
                    lambda x: x['status'] != 'Succeeded').sum()
                run_info_df['RunCount'] = run_info_df['RunProperties'].count()
                run_info_df['LastRun'] = run_info_df['RunProperties'].apply(lambda x: x['startTime']).max()
                run_info_df['LastRunStatus'] = run_info_df['RunProperties'].apply(lambda x: x['status']).max()
                run_info_df['ErrorMessage'] = run_info_df['RunProperties'].apply(
                    lambda x: x['error']['message'] if 'error' in x else None)

                run_info_df['FlowId'] = flow['FlowId']
                run_info_df = run_info_df.groupby(['FlowId', 'ErrorCount', 'RunCount', 'LastRun', 'LastRunStatus']).agg(
                    {'RunProperties': list, 'ErrorMessage': list}).reset_index()

                run_info_df['ErrorMessage'] = run_info_df['ErrorMessage'].apply(
                    lambda x: [e for e in x if not pd.isna(e)])

                flows_runs_df = pd.concat([flows_runs_df, run_info_df])

        if flows_runs_df.shape[0] > 0:
            flows_df = pd.merge(flows_df, flows_runs_df, how='left', on='FlowId')
            flows_df[['ErrorCount', 'RunCount']] = flows_df[['ErrorCount', 'RunCount']].fillna(0).astype(int)

        return flows_df

    def enrich_connections(self, flows_df):
        """ Enrich the flows with the connections
        :param flows_df: DataFrame containing the flows information
        """
        flows_connections_df = pd.DataFrame()
        for i, flow in flows_df.iterrows():
            flow_url = f'{self.base_flow_url}/scopes/admin/environments/{self.environment_id}/flows/{flow["FlowId"]}/' \
                       f'connections?{self.api_version}'

            connections_df = self.session_request("GET", flow_url)
            if connections_df.shape[0] > 0:
                connections_df.rename(columns={'name': 'ConnectionName'}, inplace=True)
                connections_df['FlowId'] = flow['FlowId']

                if 'properties' in connections_df.columns:
                    connections_df_properties = pd.concat(connections_df.apply(
                        lambda row: pd.json_normalize(row['properties']).assign(name=row['FlowId']), axis=1).tolist(),
                                                          ignore_index=True)

                    expanded_statuses_df = pd.concat(connections_df_properties.apply(
                        lambda row: pd.json_normalize(row['statuses']).assign(original_index=row.name),
                        axis=1).tolist(), ignore_index=True)
                    connections_df_properties = connections_df_properties.drop(columns=['statuses'])

                    connections_df_properties = connections_df_properties.merge(expanded_statuses_df, left_index=True,
                                                                                right_on='original_index')

                    connections_df_properties['ConnectionType'] = connections_df_properties['apiId'].apply(
                        lambda x: x.split('apis/')[1])

                    connections_df_properties.rename(columns={'displayName': 'ConnectionAccountName',
                                                              'status': 'ConnectionStatus',
                                                              'lastModifiedTime': 'ConnectionLastModifiedTime'},
                                                     inplace=True)

                    property_columns = ['name', 'ConnectionType', 'ConnectionAccountName', 'ConnectionStatus',
                                        'ConnectionLastModifiedTime', 'isDelegatedAuthConnection']
                    if 'error.code' in connections_df_properties.columns:
                        connections_df_properties.rename(columns={'error.code': 'ConnectionErrorCode',
                                                                  'error.message': 'ConnectionErrorMessage'},
                                                         inplace=True)
                        property_columns.extend(['ConnectionErrorCode', 'ConnectionErrorMessage'])

                    if 'authenticatedUser.name' in connections_df_properties.columns:
                        connections_df_properties.rename(columns={'authenticatedUser.name': 'AuthenticatedUserName'},
                                                         inplace=True)
                        property_columns.extend(['AuthenticatedUserName'])

                        null_account_mask = connections_df_properties['AuthenticatedUserName'].isnull()
                        flow_name_mask = connections_df_properties.groupby('name')['name'].transform('count') > 1
                        connections_df_properties = connections_df_properties[~(null_account_mask & flow_name_mask)]

                    connections_df_properties = connections_df_properties[property_columns]

                    grouped_property_columns = {column: list for column in property_columns[1:]}
                    connections_df_properties_group = connections_df_properties.groupby(['name']).agg(
                        grouped_property_columns).reset_index()

                    connections_df_properties_group['ConnectionsCount'] = connections_df_properties_group[
                        'ConnectionType'].apply(lambda x: len(x))

                    flows_connections_df = pd.concat([flows_connections_df, connections_df_properties_group])

        if flows_connections_df.shape[0] > 0:
            flows_connections_df.rename(columns={'name': 'FlowId'}, inplace=True)
            flows_df = pd.merge(flows_df, flows_connections_df, how='left', on='FlowId')
            flows_df['ConnectionsCount'] = flows_df['ConnectionsCount'].fillna(0).astype(int)

            if 'ConnectionErrorCode' in flows_df.columns:
                flows_df['ConnectionErrorCount'] = flows_df['ConnectionErrorCode'].apply(
                    lambda x: len(x) if isinstance(x, list) else 0)
            else:
                flows_df['ConnectionErrorCount'] = 0

        return flows_df

    def enrich_flow_url(self, flows_df):
        """ Enrich the flows with the flow URL
        :param flows_df: DataFrame containing the flows information
        """
        replacement_str = '/providers/Microsoft.ProcessSimple/'
        flows_df.loc[:, 'FlowUrl'] = flows_df['id'].apply(lambda x: self.base_edit_url + x.replace(replacement_str, ''))

        return flows_df

    def list_flows(self, relevant_columns=True, **kwargs):
        """ List the flows of an environment
        :param relevant_columns: Whether to return all the columns or only the relevant ones
        """
        enrich = False
        enrich_info = False
        enrich_owners = False
        enrich_run_history = False
        enrich_connections = False
        enrich_flow_url = False
        if kwargs != {}:
            try:
                if 'enrich' in kwargs.keys():
                    enrich = True

                if ('enrich_info' in kwargs.keys()) | (enrich is True):
                    enrich_info = True
                if ('enrich_owners' in kwargs.keys()) | (enrich is True):
                    enrich_owners = True
                if ('enrich_run_history' in kwargs.keys()) | (enrich is True):
                    enrich_run_history = True
                if ('enrich_connections' in kwargs.keys()) | (enrich is True):
                    enrich_connections = True
                if ('enrich_flow_url' in kwargs.keys()) | (enrich is True):
                    enrich_flow_url = True

            except KeyError:
                raise KeyError('Please provide a value to enrich the response with')

        flow_url = f'{self.base_flow_url}/scopes/admin/environments/{self.environment_id}/v2/flows?{self.api_version}'
        flows_df = self.session_request("GET", flow_url)

        # After first call, we use the IDs to get the flows properties from a separate call
        flows_data = pd.DataFrame()
        failed_flows_df = pd.DataFrame()
        flows_final_df = pd.DataFrame()
        if flows_df.shape[0] > 0 and 'name' in flows_df.columns:
            for flow_id in flows_df['name']:
                flow_url = f'{self.base_flow_url}/environments/{self.environment_id}/flows/{flow_id}?api-version=2016-11-01'
                try:
                    flow_data = self.session_request("GET", flow_url)
                    flows_data = pd.concat([flows_data, flow_data], ignore_index=True)
                except Exception as e:
                    failed_flow = flows_df[flows_df['name'] == flow_id].copy()
                    failed_flow['ErrorMessage'] = str(e)

                    failed_flows_df = pd.concat([failed_flows_df, failed_flow], ignore_index=True)

            flows_data.rename(columns={'name': 'FlowId', 'properties': 'FlowProperties'}, inplace=True)
            flows_df = flows_data.copy()

            if enrich_owners:
                flows_df = self.enrich_owners(flows_df)
                flows_df.drop_duplicates(subset=['FlowId'], inplace=True)

            if enrich_info:
                flows_df = self.enrich_info(flows_df)

            if enrich_run_history:
                flows_df = self.enrich_run_history(flows_df)

            if enrich_connections:
                flows_df = self.enrich_connections(flows_df)

            if enrich_flow_url:
                flows_df = self.enrich_flow_url(flows_df)

            flows_df.rename(
                columns={
                    'displayName': 'FlowName', 'definition': 'JsonDefinition', 'state': 'State',
                    'createdTime': 'CreatedDate', 'lastModifiedTime': 'LastModifiedDate',
                    'flowSuspensionReason': 'FlowSuspensionReason', 'flowSuspensionTime': 'FlowSuspensionTime',
                    'flowSuspensionReasonDetails': 'FlowSuspensionReasonDetails',
                    'AuthenticatedUserName': 'ConnectionAuthenticatedUserName'
                }, inplace=True
            )

            if relevant_columns & enrich:
                required_columns = ['FlowId', 'FlowName', 'id', 'FlowUrl', 'JsonDefinition', 'State', 'CreatedBy',
                                    'Owners', 'CreatedDate', 'LastModifiedDate', 'FlowSuspensionReason',
                                    'ErrorCount', 'ErrorMessage', 'RunCount', 'RunProperties', 'LastRun',
                                    'LastRunStatus', 'ConnectionAccountName', 'ConnectionStatus',
                                    'ConnectionLastModifiedTime', 'ConnectionsCount', 'ConnectionAuthenticatedUserName']

                existing_columns = [col for col in required_columns if col in flows_df.columns]
                flows_final_df = flows_df[existing_columns]

                if 'FlowSuspensionReasonDetails' in flows_df.columns:
                    flows_final_df = flows_final_df.assign(
                        **{'FlowSuspensionReasonDetails': flows_df['FlowSuspensionReasonDetails']})
                if 'FlowSuspensionTime' in flows_df.columns:
                    flows_final_df = flows_final_df.assign(**{'FlowSuspensionTime': flows_df['FlowSuspensionTime']})
                if 'ConnectionErrorCode' in flows_df.columns:
                    flows_final_df = flows_final_df.assign(**{'ConnectionErrorCode': flows_df['ConnectionErrorCode']})
                if 'ConnectionErrorMessage' in flows_df.columns:
                    flows_final_df = flows_final_df.assign(**{'ConnectionErrorMessage': flows_df['ConnectionErrorMessage']})
            else:
                flows_final_df = flows_df

            if 'FlowName' in flows_final_df.columns:
                flows_final_df = flows_final_df.sort_values(by=['FlowName'])

        return flows_final_df.reset_index(drop=True), failed_flows_df

    def update_flow(self, flow_id, payload):
        """ Update a flow
        :param flow_id: ID of the flow to be updated
        :param payload: Payload to be sent to the API
        """
        flow_url = f'{self.base_flow_url}/environments/{self.environment_id}/flows/{flow_id}?{self.api_version}'

        # currently no support to patch flow owners, can only be done via flow UI or admin center (09/2023)
        if isinstance(payload, dict):
            if 'properties' not in payload.keys():
                payload = {'properties': payload}
        elif isinstance(payload, pd.DataFrame):
            payload = {'properties': payload.to_dict(orient='records')[-1]}

        flow_patch_response = self.session_request("PATCH", flow_url, data=payload)

        return flow_patch_response

    def delete_flow(self, flow_id):
        """ Delete a flow
        :param flow_id: ID of the flow to be deleted
        """
        flow_url = f'{self.base_flow_url}/environments/{self.environment_id}/flows/{flow_id}?{self.api_version}'

        flow_delete_response = self.session.request("DELETE", flow_url, headers=self.headers)

        return flow_delete_response

    def create_flow(self, payload):
        """ Create a flow
        :param payload: Payload to be sent to the API
        """
        flow_url = f'{self.base_flow_url}/environments/{self.environment_id}/flows?{self.api_version}'

        flow_post_response = self.session_request("POST", flow_url, data=payload)

        return flow_post_response
