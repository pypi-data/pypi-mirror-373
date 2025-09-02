import requests as req
import json
import pandas as pd
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import base64
import datetime


class DevOps:
    def __init__(self, token=None, api_version=None):
        """ Connect to Azure DevOps and backup the flows data
        :param token: Azure DevOps PAT token
        :param api_version: Azure DevOps API version
        """

        if token is None:
            raise Exception('Token is required to connect to DevOps')

        self.headers = {"Content-Type": "application/json",
                        "Authorization": f"Basic {base64.b64encode(str(f':{token}').encode('utf-8')).decode('utf-8')}"}

        self.session = req.Session()
        retry = Retry(total=3, status_forcelist=[429, 500, 502, 504], backoff_factor=30)
        retry.BACKOFF_MAX = 190

        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)

        self.base_url = 'https://dev.azure.com/BerryworldGroup'

        if api_version is None:
            self.api_version = 'api-version=7.0'
        else:
            self.api_version = f'api-version={api_version}'

    def session_request(self, method, url, headers=None, data=None, content=False):
        """ Make a request to Azure DevOps
        :param method: Request method
        :param url: Request URL
        :param headers: Request headers
        :param data: Request data
        :param content: Content request
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
            if content:
                return response

            response = (json.loads(response.text))
            if 'value' in response:
                response_df = pd.DataFrame(response['value'])
            else:
                response_df = pd.DataFrame([response])

        else:
            raise Exception(f'Status: {response.status_code} - {response.text}')

        return response_df

    def list_projects(self):
        """ List all projects in the DevOps organisation
        """
        projects_url = f'{self.base_url}/_apis/projects'
        projects_df = self.session_request('GET', projects_url)

        return projects_df

    def list_repositories(self, project_name):
        """ List all repositories in a project
        :param project_name: DevOps project name
        """
        repo_url = f"{self.base_url}/{project_name}/_apis/git/repositories"
        repo_df = self.session_request('GET', repo_url)

        return repo_df

    def list_repository_items(self, project_name, repo_id, path=None, branch=None):
        """ List all items in a repository
        :param project_name: DevOps project name
        :param repo_id: DevOps repository ID
        :param path: Path to the repository
        :param branch: Branch to list
        """
        repo_items_url = f"{self.base_url}/{project_name}/_apis/git/repositories/{repo_id}/itemsbatch?" \
                         f"{self.api_version}"

        if path is None:
            path = "/"

        if branch is None:
            branch = "master"

        body = json.dumps({
            "itemDescriptors": [
                {
                    "path": path,
                    "version": branch,
                    "versionType": "branch",
                    "versionOptions": "none",
                    "recursionLevel": "full"
                }
            ],
            "includeContentMetadata": "true"
        })

        repo_items_df = self.session_request('POST', repo_items_url, data=body)

        return repo_items_df

    def list_pipeline_releases(self, project_name):
        """ List all pipeline releases in a project
        :param project_name: DevOps project name
        """
        release_definitions_url = f"https://vsrm.dev.azure.com/BerryworldGroup/{project_name}/_apis/release/definitions"
        release_definitions_df = self.session_request('GET', release_definitions_url)

        return release_definitions_df

    def list_release_revision(self, project_name, release_id, revision_name=None):
        """ List all pipeline release revisions
        :param project_name: DevOps project name
        :param release_id: DevOps release ID
        :param revision_name: DevOps release revision name
        """
        release_revision_url = f"https://vsrm.dev.azure.com/BerryworldGroup/{project_name}/_apis/release/" \
                               f"definitions/{release_id}/revisions"

        if revision_name is not None:
            release_revision_url = f"{release_revision_url}/{revision_name}"

        release_revision_df = self.session_request('GET', release_revision_url)

        return release_revision_df

    def list_pipeline_builds(self, project_name):
        """ List all pipeline builds in a project
        :param project_name: DevOps project name
        """
        build_definitions_url = f"{self.base_url}/{project_name}/_apis/build/definitions"
        build_definitions_df = self.session_request('GET', build_definitions_url)

        return build_definitions_df

    def list_build_revision(self, project_name, build_id):
        """ List all pipeline build revisions
        :param project_name: DevOps project name
        :param build_id: DevOps build ID
        """
        build_revision_url = f"{self.base_url}/{project_name}/_apis/build/definitions/{build_id}/revisions"
        build_revision_df = self.session_request('GET', build_revision_url)

        return build_revision_df

    def list_artifact_feeds(self):
        """ List all artifact feeds
        """
        artifact_feeds_url = f"https://feeds.dev.azure.com/BerryworldGroup/_apis/packaging/feeds"
        artifact_feeds_df = self.session_request('GET', artifact_feeds_url)

        return artifact_feeds_df

    def list_feed_packages(self, feed_id):
        """ List all packages in a feed
        :param feed_id: DevOps feed ID
        """
        feed_packages_url = f"https://feeds.dev.azure.com/BerryworldGroup/_apis/packaging/feeds/{feed_id}/packages"
        feed_packages_df = self.session_request('GET', feed_packages_url)

        return feed_packages_df

    def list_package_versions(self, feed_id, package_name):
        """ List all versions of a package
        :param feed_id: DevOps feed ID
        :param package_name: DevOps package name
        """
        package_versions_url = f"https://feeds.dev.azure.com/BerryworldGroup/_apis/packaging/feeds/{feed_id}/" \
                               f"packages/{package_name}/versions"
        package_versions_df = self.session_request('GET', package_versions_url)

        return package_versions_df

    def get_package_version_content(self, feed_id, package_id, version_id):
        """ Get the content of a package version
        :param feed_id: DevOps feed ID
        :param package_id: DevOps package ID
        :param version_id: DevOps package version ID
        """
        package_content_url = f"https://feeds.dev.azure.com/BerryworldGroup/_apis/packaging/feeds/{feed_id}/" \
                              f"packages/{package_id}/versions/{version_id}"
        package_content_df = self.session_request('GET', package_content_url)

        return package_content_df

    def create_repo_files(self, project_name, repo_id, environment_name, payload, branch=None):
        """ Create files in a repository
        :param project_name: DevOps project name
        :param repo_id: DevOps repository ID
        :param environment_name: Environment name
        :param payload: Payload to create the files
        :param branch: Branch to create the files
        """
        commits_url = f"{self.base_url}/{project_name}/_apis/git/repositories/{repo_id}/" \
                      f"commits?{self.api_version}"
        commits_df = self.session_request("GET", commits_url)
        if commits_df.shape[0] > 0:
            last_commit_id = commits_df['commitId'][0]
        else:
            last_commit_id = '0000000000000000000000000000000000000000'

        if branch is None:
            branch = "refs/heads/master"

        run_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        repo_payload = json.dumps({
            "refUpdates": [
                {
                    "name": branch,
                    "oldObjectId": last_commit_id
                }
            ],
            "commits": [{
                "comment": f"Adding {environment_name} PowerAutomate properties via API - {run_time}. "
                           f"skip-secret-scanning:true",
                "changes": payload
            }]
        })

        repo_pushes_url = f"{self.base_url}/{project_name}/_apis/git/repositories/{repo_id}/pushes?{self.api_version}"

        create_repo_files = self.session_request("POST", repo_pushes_url, data=repo_payload)

        return create_repo_files

    def get_file_content(self, project_name, repo_id, file_path):
        """ Get the content of a file in a repository
        :param project_name: DevOps project name
        :param repo_id: DevOps repository ID
        :param file_path: Path to the file
        """
        file_content_url = f"{self.base_url}/{project_name}/_apis/git/repositories/{repo_id}/items?" \
                           f"scopePath={file_path}&includeContent=True"

        file_content = self.session_request("GET", file_content_url, content=True)

        return file_content
