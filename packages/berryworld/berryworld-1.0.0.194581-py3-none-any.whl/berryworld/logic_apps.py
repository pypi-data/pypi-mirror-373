import requests as req
import json
import pandas as pd
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def format_create_payload(payload):
    """ Format the payload to create a workflow in Azure Portal
    :param payload: Properties and Definition of the workflow
    """
    # Reshape the payload to fit the required format
    json_dict = json.loads(payload)

    # Check if definition key is in json payload
    if not ('definition' in json_dict['properties'].keys()):
        json_dict = {
            "properties": {
                "definition": json_dict['properties']
            }
        }

    # Check if location key is in json payload
    location_flag = False
    location_dict = {}
    if 'location' in json_dict['properties']['definition'].keys():
        location_dict = json_dict['properties']['definition']['location']
        json_dict = {
            "properties": {
                "definition": {key: val for key, val in json_dict['properties']['definition'].items() if
                               key != 'location'}
            }
        }
        location_flag = True

    # Check if tags key is in json payload
    tags_flag = False
    tags_dict = {}
    if 'tags' in json_dict['properties']['definition'].keys():
        tags_dict = json_dict['properties']['definition']['tags']
        json_dict = {
            "properties": {
                "definition": {key: val for key, val in json_dict['properties']['definition'].items() if
                               key != 'tags'}
            }
        }
        tags_flag = True
        json_dict = {**json_dict, **{'tags': tags_dict}}

    if tags_flag:
        json_dict = {**json_dict, **{'tags': tags_dict}}
    if location_flag:
        json_dict = {**json_dict, **{'location': location_dict}}

    return json.dumps(json_dict)


class LogicApps:
    def __init__(self, **kwargs):
        """
        Manage Logic Apps Flows.
        :param kwargs: Dictionary containing the info to connect to the Power Automate API
            - client_id: ID of the client as defined in Azure (Application (client) ID)
            - client_secret: Secret of the client as created in Azure
            - tenant_id: ID of the environment as defined in Power Automate
        """
        if kwargs != {}:
            try:
                self.client_id = kwargs['client_id']
                self.client_secret = kwargs['client_secret']
                self.tenant_id = kwargs['tenant_id']
                self.resource = 'https://management.azure.com/'
            except KeyError as ke:
                raise KeyError("Missing parameter: %s" % str(ke))
        else:
            raise KeyError('Please provide a value for each of these variables: client_id, client_secret, tenant_id.')

        self.session = req.Session()
        retry = Retry(total=3, status_forcelist=[429, 500, 502, 504], backoff_factor=30)
        retry.BACKOFF_MAX = 190

        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)

        # Set API version
        self.api_version = 'api-version=2016-06-01'

        self.token_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/token"

        self.headers = self.generate_bearer_token()

    def generate_bearer_token(self):
        """ Generate a bearer token to be used in the headers of the requests
        """
        bearer_headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'resource': self.resource
        }
        token_response = req.post(self.token_url, headers=bearer_headers, data=data)
        auth_status_code = token_response.status_code

        if str(auth_status_code).startswith('2'):
            auth_access_token = 'Bearer ' + json.loads(token_response.text)['access_token']
            headers = {"Authorization": f"{auth_access_token}", "Content-Type": "application/json"}
        else:
            raise Exception(f'Error: {auth_status_code} - {token_response.text}')

        return headers

    def list_subscriptions(self):
        """ List the available subscriptions in Azure Portal
        """
        subscriptions_url = f"https://management.azure.com/subscriptions?" + self.api_version
        subscription_resp = req.get(subscriptions_url, headers=self.headers, data={})
        if subscription_resp.status_code != 200:
            raise Exception(f'Cannot retrieve Subscriptions. Error: {subscription_resp.text}')
        try:
            subscription_df = pd.DataFrame(subscription_resp.json()['value'])
        except KeyError:
            raise KeyError(f'No Value key for Subscriptions. Error: {subscription_resp.text}')

        return subscription_df

    def list_resource_groups(self, subscription):
        """ List the available resource groups in Azure Portal
        :param subscription: Subscription to get the resource groups from
        """
        resource_url = f"https://management.azure.com/subscriptions/{subscription}/resourcegroups?" \
                       f"api-version=2021-04-01"
        resource_resp = req.get(resource_url, headers=self.headers, data={})
        if resource_resp.status_code != 200:
            raise Exception(f'Cannot retrieve Resource Groups. Error: {resource_resp.text}')
        try:
            resource_df = pd.DataFrame(resource_resp.json()['value'])
        except KeyError:
            raise KeyError(f'No Value key for Resource Groups. Error: {resource_resp.text}')

        return resource_df

    def list_workflows(self, subscription, resource_group):
        """ List the available resource groups in Azure Portal
        :param subscription: Subscription to get the resource groups from
        :param resource_group: Resource group to get the workflows from
        """
        workflows_url = f"https://management.azure.com/subscriptions/{subscription}/resourceGroups/" \
                        f"{resource_group}/providers/Microsoft.Logic/workflows?" + self.api_version
        workflow_resp = req.get(workflows_url, headers=self.headers, data={})
        if workflow_resp.status_code != 200:
            raise Exception(f'Cannot retrieve Workflows. Error: {workflow_resp.text}')
        try:
            workflow_df = pd.DataFrame(workflow_resp.json()['value'])
        except KeyError:
            raise KeyError(f'No Value key for Workflows. Error: {workflow_resp.text}')

        logic_app_url = f"https://portal.azure.com/#@poupart.onmicrosoft.com/resource/subscriptions/{subscription}/" \
                        f"resourceGroups/{resource_group}/providers/Microsoft.Logic/workflows/%s/logicApp"
        workflow_df['WorkflowUrl'] = workflow_df['name'].apply(lambda x: logic_app_url % x)

        return workflow_df

    def list_workflow_run(self, subscription, resource_group, workflow_name):
        """ List the available resource groups in Azure Portal
        :param subscription: Subscription to get the resource groups from
        :param resource_group: Resource group to get the workflows from
        :param workflow_name: Name of the workflow to get the runs from
        """
        runs_url = f"https://management.azure.com/subscriptions/{subscription}/resourceGroups/{resource_group}" \
                   f"/providers/Microsoft.Logic/workflows/{workflow_name}/runs?" + self.api_version
        runs_resp = req.get(runs_url, headers=self.headers, data={})
        if runs_resp.status_code != 200:
            raise Exception(f'Cannot retrieve Workflow Runs. Error: {runs_resp.text}')
        try:
            runs_df = pd.DataFrame(runs_resp.json()['value'])
        except KeyError:
            raise KeyError(f'No Value key for Workflow Runs. Error: {runs_resp.text}')

        return runs_df

    def get_workflow_info(self, subscription, resource_group, workflow_name):
        """ Get workflow information from Azure Portal
        :param subscription: Subscription to get the resource groups from
        :param resource_group: Resource group to get the workflows from
        :param workflow_name: Name of the workflow to get the runs from
        """
        info_url = f"https://management.azure.com/subscriptions/{subscription}/resourceGroups/{resource_group}/" \
                   f"providers/Microsoft.Logic/workflows/{workflow_name}?" + self.api_version
        info_resp = req.get(info_url, headers=self.headers, data={})
        if info_resp.status_code != 200:
            raise Exception(f'Cannot retrieve Workflow Info. Error: {info_resp.text}')
        workflow_info_df = pd.json_normalize(info_resp.json())

        return workflow_info_df

    def disable_workflow(self, subscription, resource_group, workflow_name):
        """ Disable workflow in Azure Portal
        :param subscription: Subscription to get the resource groups from
        :param resource_group: Resource group to get the workflows from
        :param workflow_name: Name of the workflow to get the runs from
        """
        disable_url = f"https://management.azure.com/subscriptions/{subscription}/resourceGroups/{resource_group}/" \
                      f"providers/Microsoft.Logic/workflows/{workflow_name}/disable?" + self.api_version
        disable_resp = req.post(disable_url, headers=self.headers, data={})
        if disable_resp.status_code != 200:
            raise Exception(f'Cannot disable the workflow {workflow_name}. Error: {disable_resp.text}')

    def enable_workflow(self, subscription, resource_group, workflow_name):
        """ Enable workflow in Azure Portal
        :param subscription: Subscription to get the resource groups from
        :param resource_group: Resource group to get the workflows from
        :param workflow_name: Name of the workflow to get the runs from
        """
        enable_url = f"https://management.azure.com/subscriptions/{subscription}/resourceGroups/{resource_group}/" \
                     f"providers/Microsoft.Logic/workflows/{workflow_name}/enable?" + self.api_version
        enable_resp = req.post(enable_url, headers=self.headers, data={})
        if enable_resp.status_code != 200:
            raise Exception(f'Cannot enable the workflow {workflow_name}. Error: {enable_resp.text}')

    def delete_workflow(self, subscription, resource_group, workflow_name):
        """ Delete workflow in Azure Portal
        :param subscription: Subscription to get the resource groups from
        :param resource_group: Resource group to get the workflows from
        :param workflow_name: Name of the workflow to get the runs from
        """
        delete_url = f"https://management.azure.com/subscriptions/{subscription}/resourceGroups/{resource_group}/" \
                     f"providers/Microsoft.Logic/workflows/{workflow_name}?" + self.api_version
        delete_resp = req.delete(delete_url, headers=self.headers, data={})
        if delete_resp.status_code != 200:
            raise Exception(f'Cannot delete the workflow {workflow_name}. Error: {delete_resp.text}')

    def create_workflow(self, subscription, resource_group, workflow_name, payload):
        """ Create workflow in Azure Portal
        :param subscription: Subscription ID to get the resource groups from
        :param resource_group: Resource group Name to get the workflows from
        :param workflow_name: New name of the workflow
        :param payload: Payload to create the workflow. It usually comes under properties in the workflow response
        which we must add "location" and "tags" keys. It should be in the same format that the Logic Apps are stored in
        the Azure DevOps repository.
        Payload example:
        {
          "properties": {
            "definition": {
              "$schema": "https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#",
              "contentVersion": "1.0.0.0",
              "parameters": {
                "$connections": {
                  "defaultValue": {},
                  "type": "Object"
                }
              },
              "triggers": {
                "manual": {
                  "type": "Request",
                  "kind": "Http",
                  "inputs": {
                    "schema": {}
                  }
                }
              },
              "actions": {
                "Find_pet_by_ID": {
                  "runAfter": {},
                  "type": "ApiConnection",
                  "inputs": {
                    "host": {
                      "connection": {
                        "name": "@parameters('$connections')['test-custom-connector']['connectionId']"
                      }
                    },
                    "method": "get",
                    "path": "/pet/@{encodeURIComponent('1')}"
                  }
                }
              },
              "outputs": {}
            },
            "parameters": {
              "$connections": {
                "value": {
                  "test-custom-connector": {
                    "connectionId": "/subscriptions/34adfa4f-cedf-4dc0-ba29-b6d1a69ab345/resourceGroups/test-resource-group/providers/Microsoft.Web/connections/test-custom-connector",
                    "connectionName": "test-custom-connector",
                    "id": "/subscriptions/34adfa4f-cedf-4dc0-ba29-b6d1a69ab345/providers/Microsoft.Web/locations/brazilsouth/managedApis/test-custom-connector"
                  }
                }
              }
            }
          },
          "location": "brazilsouth",
          "tags": {}
        }
        """
        create_url = f"https://management.azure.com/subscriptions/{subscription}/resourceGroups/{resource_group}/" \
                     f"providers/Microsoft.Logic/workflows/{workflow_name}?" + self.api_version
        headers_ = self.headers
        headers_['Content-Type'] = 'application/json'

        create_resp = req.put(create_url, headers=self.headers, data=payload)
        if not str(create_resp.status_code).startswith('2'):
            print('Try to reform the payload to fit the required format in the Azure Portal')
            payload = format_create_payload(payload)
            create_resp = req.put(create_url, headers=self.headers, data=payload)
            if not str(create_resp.status_code).startswith('2'):
                raise Exception(f'Cannot create the workflow {workflow_name}. Error: {create_resp.text}')
