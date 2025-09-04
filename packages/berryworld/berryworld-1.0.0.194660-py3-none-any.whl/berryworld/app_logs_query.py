import requests
import json
import pandas as pd


class AppLogsQuery:
    """ Query Logs to ApplicationInsights """

    def __init__(self, app_id, app_key, days=1):
        """ Initialize the class
        :param app_id: ApplicationId as it comes in Application Insights -> API Access
        :param app_key: ApplicationKey as it comes in Application Insights -> API Access
        :param days: Days to query back the logs (Applicable only if using the default Kusto query)
        """
        self.headers = {'X-Api-Key': app_key}
        self.url = f'https://api.applicationinsights.io/v1/apps/{app_id}/query'
        self.days = days

        default_kusto_query = f"""
          exceptions
          | where timestamp > ago({days}d) 
          | order by timestamp desc
        """
        self.params = {"query": default_kusto_query}

    def query_logs(self, query=None):
        """ Query Application Insights logs
        :param query: Kusto custom query to retrieve the logs
        """
        if query is not None:
            self.params = {"query": query}

        # Query logs
        app_ins_resp = requests.get(self.url, headers=self.headers, params=self.params)
        logs = json.loads(app_ins_resp.text)

        # Load logs into a DataFrame
        logs_df = pd.DataFrame()
        for row in logs['tables'][0]['rows']:
            logs_df = pd.concat([logs_df, pd.DataFrame(row).T])
        columns_list = pd.DataFrame(logs['tables'][0]['columns'])['name'].values
        logs_df.columns = columns_list

        return logs_df.drop_duplicates().reset_index(drop=True)

    def query_exceptions(self, query=None, days=None):
        """ Query Application Insights logs
        :param query: Kusto custom query to retrieve the logs
        :param days: Days to query back the logs (Applicable only if using the default Kusto query)
        """
        if days is None:
            days = self.days

        if query is None:
            default_kusto_query = f"""
              exceptions
              | where timestamp > ago({days}d) 
              | order by timestamp desc
              | project timestamp, type, severityLevel, details[0].message, customDimensions.ServerType, 
                        customDimensions.ProjectName, customDimensions.Pipeline, customDimensions.IpAddress, 
                        customDimensions.RequestUrl, customDimensions.Section
            """
        else:
            default_kusto_query = query
        self.params.update({"query": default_kusto_query})

        # Query logs
        app_ins_resp = requests.get(self.url, headers=self.headers, params=self.params)
        logs = json.loads(app_ins_resp.text)

        # Convert Logs into a DataFrame
        logs_df = pd.DataFrame()
        for row in logs['tables'][0]['rows']:
            logs_df = pd.concat([logs_df, pd.DataFrame(row).T])

        if logs_df.shape[0] > 0:
            # Allocate column names
            columns_list = pd.DataFrame(logs['tables'][0]['columns'])['name'].values
            logs_df.columns = columns_list

            # Standardise timestamp
            if 'timestamp' in logs_df.columns:
                logs_df['timestamp'] = pd.to_datetime(logs_df['timestamp'])
                logs_df['timestamp'] = logs_df['timestamp'].dt.strftime("%Y-%m-%d %H:%M:%S")

            if query is None:
                logs_df = logs_df.rename(
                    columns={'timestamp': 'Datetime', 'type': 'ErrorType', 'severityLevel': 'ErrorSeverity',
                             'details_0_message': 'ErrorMessage', 'customDimensions_ServerType': 'ServerType',
                             'customDimensions_ProjectName': 'ProjectName', 'customDimensions_Pipeline': 'Pipeline',
                             'customDimensions_IpAddress': 'IpAddress', 'customDimensions_RequestUrl': 'RequestUrl',
                             'customDimensions_Section': 'Section'}
                    ).drop_duplicates()

            # Unpack customDimensions
            if 'customDimensions' in logs_df.columns:
                logs_df = logs_df.assign(**pd.json_normalize(logs_df['customDimensions'].apply(lambda x: json.loads(x))))

            # Unpack details
            if 'details' in logs_df.columns:
                logs_df = logs_df.assign(**pd.json_normalize(logs_df['details'].apply(lambda x: json.loads(x)[0])))

        return logs_df
