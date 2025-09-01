"""
log_file.py encapsulates the functionality common to all log files.
This includes validating the existence of the file at the specified path.
"""
import json
import logging
from pathlib import Path
import pandas as pd
from wbclient.wb_server import get_fmserver_connection
import fmrest
from fmrest.exceptions import BadJSON, BadGatewayError, FileMakerError, RequestException
from os import environ as env, path


def validate_file_path(file_path: str) -> bool:
    """
    Validate the existence of the file at the specified path.

    :param file_path: Path to the file
    :return: True if file exists, else False
    """
    my_file = Path(file_path)
    return my_file.is_file()


def get_log_files() -> list:
    """
    Connects to FileMaker Server, reads configuration layout, then creates and returns the matching log_files
    :return: list of LogFile objects
    """
    fms = get_fmserver_connection("configure")
    logfiles = []
    # PWA: the 'with' statement is taking care of object destruction but…
    with fms as my_server:
        # PWA: as I think there is a problem with the destructor of he fms instance,
        # let's handle the exception back in the calling code and not return on error
        # this avoids the unhandled error in the class destructor
        try:
            my_server.login()
        except (RequestException, BadGatewayError, BadJSON, FileMakerError) as e:
            if isinstance(e, RequestException):
                logging.error(f'Unable to connect to the server, check that the server url is correct: {str(e)}')
            elif isinstance(e, BadGatewayError):
                logging.error(f'Unable to connect to the server, make sure the Data API connector is enabled: {str(e)}')
            elif isinstance(e, BadJSON):
                logging.error(f'Unable to connect to the server, make sure the Data API connector is enabled: {str(e)}')
            elif isinstance(e, FileMakerError):
                logging.error(f'Unable to login to the server with the credentials provided: {str(e)}')

            return logfiles

        # PWA: we are counting on access privileges on record level
        find_query = [{'id_server': "*"}]
        try:
            records = my_server.find(query=find_query)
        except (RequestException, FileMakerError) as e:
            logging.error(f"Unable to get configuration records: {str(e)}")
            return logfiles

        for record in records:
            logging.info(record.Path_to_log_file)
            file_path = record.Path_to_log_file if record.Path_to_log_file else None
            timestamp_column = record.name_of_timestamp if record.name_of_timestamp else "Timestamp"
            timestamp_last = record.timestamp_payload_last

            # PWA: loading 'columns' filemaker field directly into config_dict
            # (no more base64 encode needed)
            config_dict = json.loads(record.columns)
            # Extract 'fields' from the dictionary and assign it to variables columns.
            columns = config_dict['fields']

            try:
                log = LogFile(id_configuration=record.id_configuration,
                          log_type=record.Name,
                          columns=columns,
                          timestamp_column=timestamp_column,
                          timestamp_last=timestamp_last,
                          file_path=file_path)
                logfiles.append(log)
            except ValueError as e:
                logging.error(f"Unable to create log object: {str(e)}")
    return logfiles


class LogFile:
    def __init__(self, id_configuration: str, log_type: str, columns: str,
                 timestamp_column: str,
                 timestamp_last: str,
                 file_path: str = None):
        """
        Initialize LogFile object.

        :param id_configuration: Configuration ID
        :param log_type: Type of the log
        :param columns: Columns of the log file
        :param timestamp_column: Column name for timestamps
        :param timestamp_last: Last timestamp in the log
        :param file_path: Path to the log file
        """
        self.log_type = log_type
        self.id_configuration = id_configuration
        if validate_file_path(file_path):
            self.file_path = file_path
        else:
            logging.error(f"There is no file at the path:{file_path}")
            raise ValueError(f'There is no file at the specified path:{file_path}')
        if not columns:
            logging.error(f"No columns specified for the log file:{file_path}")
            raise ValueError("No columns specified for the log file.")
        self.columns = columns
        self.chunk_size = 20
        self.retry_post = False
        self.timestamp_ref = None
        self.timestamp_column = timestamp_column
        logging.debug(f"Timestamp column = {self.timestamp_column}")
        self.timestamp_start = timestamp_last
        logging.debug(f"Timestamp start = {self.timestamp_start}")
        self.timestamp_start_last = timestamp_last
        logging.debug(f"Logging the file at: {file_path}")
        self.server = get_fmserver_connection("post")
        self.server.login()

    def read_log(self):
        if self.retry_post:
            self.timestamp_start = self.timestamp_start_last
            self.retry_post = False
        logging.debug(f"{self.log_type} ...")
        try:
            df = pd.read_csv(self.file_path, sep="\t", engine='python')
        except pd.errors.ParserError as e:
            logging.error(f"failed to read log file {str(self.file_path)}: {str(e)}.")
            raise ValueError("Cannot continue.")

        # Check if self.columns is set
        if not self.columns:
            logging.error("No columns specified for the log file.")
            raise ValueError("No columns specified for the log file.")

        df.columns = self.columns
        ts_column = self.timestamp_column

        # query df for all rows after the timestamp_start
        temp_df = df[df[ts_column] > self.timestamp_start]
        logging.debug(f"Temp df: {temp_df.shape[0]}")
        row_count = temp_df.shape[0]
        if row_count == 0:
            end_of_file = True
            return None, None, end_of_file, row_count
        elif row_count > self.chunk_size:
            # truncate the dataframe to max chunk size
            new_data = temp_df.iloc[0:self.chunk_size, :]
            # row_count == self.chunk_size
            end_of_file = False
        else:
            end_of_file = True
            new_data = temp_df

        last_timestamp_read = new_data.iloc[-1, 0]
        logging.debug(last_timestamp_read)
        self.set_last_read_timestamp(last_timestamp_read)
        if new_data.size > 0:
            logging.debug("new data - ")
        else:
            logging.debug("no new data - ")

        # PWA: add id_configuration column
        new_data.insert(0, 'id_configuration', self.id_configuration)

        # PWA: convert this to a dictionary
        dict_data = new_data.to_dict(orient='records')

        # PWA: wrap a FileMaker DAPI 'create' structure around it
        # PWA: unfortunately FileMaker is not supporting this in the current build
        # as soon as they catch up this should become a(n) oneliner on the FMS end
        dict_payload = {'action': 'create', 'fieldData': dict_data, 'layouts': path.basename(self.file_path)}

        # PWA: convert to a string for posting
        json_str = json.dumps(dict_payload)
        logging.debug(json_str)

        # PWA: return json, last_timestamp_read, end_of_file, row_count
        return json_str, last_timestamp_read, end_of_file, row_count

    def post_logfile_data(self, the_data, record_id, id_configuration, last_timestamp, end_of_file):
        logging.debug("Sending log file data to Whistleblower server")
        # IJE: nasty workaround for FileMaker Data API not being keen on Boolean
        eof = 1 if end_of_file else 0
        try:
            my_data = {
                "payload": the_data,
                "id_server": self.server.user,
                "id_configuration": id_configuration,
                "timestamp_stop": last_timestamp,
                "is_end_of_file": eof
            }
            self.server.edit_record(record_id, my_data, scripts={
                'after': [env['post_script'], 'logfile']
            })
            logging.debug(self.server.last_script_result)
            logging.debug("OK -")

            return True
        except fmrest.exceptions.FileMakerError as e:
            logging.error(f"Failed to send log file data: {str(e)}")
            logging.exception(e)
            return False

    def set_last_read_timestamp(self, timestamp_ref):
        """
        Set the last read timestamp to allow for post retries.

        :param timestamp_ref: The new timestamp reference
        """
        logging.debug(f"Setting last read timestamp to {timestamp_ref}")
        self.timestamp_start_last = self.timestamp_start
        self.timestamp_start = timestamp_ref
