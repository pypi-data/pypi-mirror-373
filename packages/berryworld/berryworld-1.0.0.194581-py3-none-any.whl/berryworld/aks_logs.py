import logging


class Logs:
    """ Class to send Logs to the Kubernetes Pod in a structured manner """

    @staticmethod
    def send_log(label='LOG', project='', method='', section='', error_msg='', ip_address='',
                 request_url='', instructions=''):
        """ Submit a log to the Kubernetes Pod
         :param label: Label to mark the Log Type
         :param project: Name of the project
         :param method: Name of the method
         :param error_msg: Error message
         :param section: Section of the pipeline
         :param ip_address: IP Address of the request
         :param request_url: URL of the request
         :param instructions: Instructions to sort the error

         Call examples:

         PodLogs().send_log(label='LOG', project='ProjectName', method='MethodName', section='Title',
                            error_msg='Message', ip_address='IPAddress', request_url='RequestURL',
                            instructions='Instructions')
        PodLogs.send_log(label='LOG', project='ProjectName', method='MethodName', section='Title',
                         error_msg='Message', ip_address='IPAddress', request_url='RequestURL',
                         instructions='Instructions')
        """

        # Configure logger format string
        log_format = '%(Label)s:%(asctime)s¦%(name)s¦%(Method)s¦' \
                     '%(IPAddress)s¦%(RequestUrl)s¦%(Section)s|%(message)s|%(Instructions)s'

        # Create log extra parameters dictionary
        params_ = {'Label': label, 'Method': method, 'IPAddress': ip_address,
                   'RequestUrl': request_url, 'Section': section, 'Instructions': instructions}

        # Set logger and remove handlers if any (To avoid logs duplication)
        logger = logging.getLogger(project)
        if logger.hasHandlers():
            logger.handlers.clear()

        # Create Log Handler and set format
        syslog = logging.StreamHandler()
        formatter = logging.Formatter(log_format, "%Y-%m-%d %H:%M:%S")
        syslog.setFormatter(formatter)

        # Set logger level and add handler
        logger.setLevel(logging.INFO)
        logger.addHandler(syslog)

        # Send log
        logger = logging.LoggerAdapter(logger, params_)
        logger.info(error_msg)
