import os
import re
from dotenv import load_dotenv

load_dotenv(os.path.join(os.getcwd(), '.env'))


class SQLCredentials:
    def __init__(self, db_name, server_type=None, azure=None):
        if db_name is None:
            raise ValueError("Please provide a value for db_name")
        self.db_name = db_name
        self.server_type = server_type
        self.azure = azure

    def simple_creds(self):
        if self.server_type is None:
            raise ValueError("Please provide a value for server_type")

        try:
            if self.azure is not None:
                if self.azure:
                    server_name = os.environ.get(f"SQL_AZURE_{self.server_type.upper()}")
                else:
                    server_name = os.environ.get(f"SQL_ONPREM_{self.server_type.upper()}")
            else:
                server_name = os.environ.get("SQL_" + self.db_name.upper() + '_' + self.server_type.upper())

            if os.environ.get("SQL_" + self.db_name.upper() + '_DB_NAME_' + self.server_type.upper()) is not None:
                db_name = os.environ.get("SQL_" + self.db_name.upper() + '_DB_NAME_' + self.server_type.upper())
            else:
                db_name = os.environ.get("SQL_" + self.db_name.upper() + '_DB_NAME')

            user_name = os.environ.get("SQL_" + self.db_name.upper() + '_USER_NAME')
            password = os.environ.get("SQL_" + self.db_name.upper() + '_PASSWORD')

            return {'server_name': re.sub(r'(\\)\1*', r'\1', server_name),
                    'db_name': db_name,
                    'user_name': user_name,
                    'password': password}
        except ValueError as e:
            raise ValueError("Variable %s not found" % str(e))

    def all_creds(self):
        try:
            prod_ = os.environ.get("SQL_" + self.db_name.upper() + '_PROD')
            test_ = os.environ.get("SQL_" + self.db_name.upper() + '_TEST')
            try:
                dev_ = os.environ.get("SQL_" + self.db_name.upper() + '_DEV')
            except Exception as e:
                print(e)
                dev_ = None
            if os.environ.get("SQL_" + self.db_name.upper() + '_DB_NAME_' + self.server_type.upper()) is not None:
                db_name = os.environ.get("SQL_" + self.db_name.upper() + '_DB_NAME_' + self.server_type.upper())
            else:
                db_name = os.environ.get("SQL_" + self.db_name.upper() + '_DB_NAME')
            user_name = os.environ.get("SQL_" + self.db_name.upper() + '_USER_NAME')
            password = os.environ.get("SQL_" + self.db_name.upper() + '_PASSWORD')

            creds = {'prod': prod_,
                     'test': re.sub(r'(\\)\1*', r'\1', test_),
                     'db_name': db_name,
                     'user_name': user_name,
                     'password': password}

            if dev_ is not None:
                creds.update({'dev': dev_})
            return creds

        except ValueError as e:
            raise ValueError("Variable %s not found" % str(e))


class BCCredentials:
    def __init__(self, db_name=None, auth=False):
        self.db_name = db_name
        self.auth = auth

    def simple_creds(self):
        try:
            if self.auth:
                scope = os.environ.get("BC-AUTH-SCOPE")
                client_id = os.environ.get("BC-AUTH-CLIENT-ID")
                client_secret = os.environ.get("BC-AUTH-CLIENT-SECRET")

                return {'scope': scope,
                        'client_id': client_id,
                        'client_secret': client_secret}
            elif self.db_name is not None:
                server_type = os.environ.get(f"BC-ENV-SERVER-{self.db_name.upper()}")

                return {'server_type': server_type}
            else:
                raise ValueError("Please provide a valid input")

        except ValueError as e:
            raise ValueError("Variable %s not found" % str(e))


class WebServiceCredentials:
    def __init__(self, service=None):
        self.service = service

    def simple_creds(self):
        try:
            if self.service is None:
                raise ValueError("Please provide a value for site")

            try:
                user_name = os.environ.get(f"WEBSERVICE_USER_{self.service.upper()}")
            except Exception as e:
                print(e)
                user_name = ''
            try:
                password = os.environ.get(f"WEBSERVICE_PASSWORD_{self.service.upper()}")
            except Exception as e:
                print(e)
                password = ''
            try:
                access_token = os.environ.get(f"WEBSERVICE_ACCESS_TOKEN_{self.service.upper()}")
            except Exception as e:
                print(e)
                access_token = ''

            return {'user_name': user_name,
                    'password': password,
                    'access_token': access_token}

        except ValueError as e:
            raise ValueError("Variable %s not found" % str(e))


class MicrosoftTeamsCredentials:
    def __init__(self, organisation_id=None):
        self.organisation_id = organisation_id

    def simple_creds(self):
        try:
            if self.organisation_id is None:
                self.organisation_id = os.environ.get("POUPART_ORGANISATION_ID")

            client_id = os.environ.get("MICROSOFT_TEAMS_APP_CLIENT_ID")
            client_secret = os.environ.get("MICROSOFT_TEAMS_APP_CLIENT_SECRET")
            username = os.environ.get("MICROSOFT_TEAMS_USERNAME")
            password = os.environ.get("MICROSOFT_TEAMS_PASSWORD")

            return {'organisation_id': self.organisation_id,
                    'client_id': client_id,
                    'client_secret': client_secret,
                    'username': username,
                    'password': password}

        except ValueError as e:
            raise ValueError("Variable %s not found" % str(e))


class SnowflakeCredentials:
    def __init__(self, db_name):
        if db_name is None:
            raise ValueError("Please provide a value for db_name")
        self.db_name = db_name

    def simple_creds(self):
        try:
            account = os.environ.get("SNOWFLAKE-" + self.db_name.upper() + '-ACCOUNT')
            user_name = os.environ.get("SNOWFLAKE-" + self.db_name.upper() + '-USERNAME')
            password = os.environ.get("SNOWFLAKE-" + self.db_name.upper() + '-PASSWORD')

            return {
                'account': account,
                'user_name': user_name,
                'password': password}
        except ValueError as e:
            raise ValueError("Variable %s not found" % str(e))
