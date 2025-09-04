


class PythonLogs:
    """ Register the Python Logs """
    def __init__(self, conn, batch_process):
        self.conn = conn
        self.batch_process = batch_process
        self.batch_log_id = None

    def start(self, log_type):
        """ Start the Python Log
        :param log_type: Type of the log
        """
        batch_log = self.conn.run_statement(
            f"EXEC d365bc.spPythonBatchLogInsert @DataType = {self.batch_process}, @LogType = '{log_type}'",
            commit_as_transaction=False)
        self.batch_log_id = batch_log['OUTPUT'][0]

    def end(self, batch_log_id=None):
        """ End the Python Log
        :param batch_log_id: Batch Log Id
        """
        if batch_log_id is None:
            batch_log_id = self.batch_log_id
        if batch_log_id is None:
            raise Exception('Batch Log Id is not set')

        self.conn.run_statement(
            f"EXEC d365bc.spPythonBatchLogUpdate @BatchLogId = {batch_log_id}",
            commit_as_transaction=False)
