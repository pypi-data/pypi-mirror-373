import logging
from opencensus.ext.azure.log_exporter import AzureLogHandler


class AppLogs:
    """ Upload Logs to ApplicationInsights """

    def __init__(self, instrumentation_key, project_name=None, pipeline=None, section=None, server_type=None,
                 ip_address=None, request_url=None):
        """ Initialize the class
        :param instrumentation_key: Key to access Application Insights from Azure portal
        :param project_name: Name of the project being run. it must be already declared in PythonEmailProjectSeverity
        :param pipeline: Pipeline name being run. It must identify the process being executed uniquely
        :param server_type: Script section where the script failed
        :param server_type: Type of server to connect to
        :param ip_address: IP Address
        :param request_url: URL requested by the client
        """
        self.server_type = server_type
        self.project_name = project_name
        self.pipeline = pipeline
        self.section = section
        self.ip_address = ip_address
        self.request_url = request_url
        self.properties = None

        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(AzureLogHandler(
            connection_string=f"InstrumentationKey={instrumentation_key};"
                              f"IngestionEndpoint=https://westeurope-5.in.applicationinsights.azure.com/;"
                              f"LiveEndpoint=https://westeurope.livediagnostics.monitor.azure.com/")
        )

    def allocate_properties(self):
        self.properties = {"custom_dimensions": {
            "ServerType": self.server_type if self.server_type is not None else "",
            "ProjectName": self.project_name if self.project_name is not None else "",
            "Pipeline": self.pipeline if self.pipeline is not None else "",
            "Section": self.section if self.section is not None else "",
            "IpAddress": str(self.ip_address) if self.ip_address is not None else "",
            "RequestUrl": str(self.request_url) if self.request_url is not None else ""}
        }

    def send_log(self, error_message, error_type='exception'):
        """ Send a Log message
        :param error_message: Error message
        :param error_type: Type of error to raise.
            - exception
            - critical
            - info
            - warning
            - error
        """
        self.allocate_properties()
        if self.properties is not None:
            if error_type == 'exception':
                self.logger.exception(error_message, extra=self.properties)
            elif error_type == 'critical':
                self.logger.critical(error_message, extra=self.properties)
            elif error_type == 'info':
                self.logger.info(error_message, extra=self.properties)
            elif error_type == 'warning':
                self.logger.warning(error_message, extra=self.properties)
            elif error_type == 'error':
                self.logger.error(error_message, extra=self.properties)
            else:
                raise Exception("error_type not understood")
        else:
            if error_type == 'exception':
                self.logger.exception(error_message)
            elif error_type == 'critical':
                self.logger.critical(error_message)
            elif error_type == 'info':
                self.logger.info(error_message)
            elif error_type == 'warning':
                self.logger.warning(error_message)
            elif error_type == 'error':
                self.logger.error(error_message)
            else:
                raise Exception("error_type not understood")

    def exception(self, message='Exception.'):
        """ Send an Exception
        :param message: Message to be added to the exception
        try:
            result = 1 / 0  # generate a ZeroDivisionError
        except Exception:
            logger.exception()
        """
        self.allocate_properties()
        if self.properties is not None:
            self.logger.exception(message, extra=self.properties)
        else:
            self.logger.exception(message)
