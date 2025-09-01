import fmrest
from fmrest.exceptions import BadGatewayError, BadJSON, FileMakerError, FMRestException, RequestException
import logging
from os import environ as env
import urllib3


def get_fmserver_connection(action: str):
    if action == "configure":
        layout = env['configuration_layout']
    elif action == "post":
        layout = env['post_layout']
    elif action == "control":
        layout = env['command_layout']
    else:
        layout = ""
        logging.error(f"making connection to server with unknown action '{action}'")
    use_ssl = env['use_ssl'] == 'True'
    if not use_ssl:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    fms = fmrest.Server(url=f"{env['host_name']}:{str(env['port'])}",
                        user=env['serverid'],
                        password=env['password'],
                        database=env['database_name'],
                        layout=layout,
                        api_version='vLatest',
                        verify_ssl=use_ssl,
                        auto_relogin=True
                        )
    return fms


def get_payload_global_id():
    logging.debug("Getting payload_global_id")
    fms = get_fmserver_connection("post")
    with fms as my_server:
        try:
            my_server.login()
            # get our FileMaker record
            records = my_server.get_records(limit=1)
            if records:
                record = records[0]
                record_id = record.record_id
                return record_id
            else:
                logging.error("Problem getting payload record ID.")
                return None
        except (RequestException, BadGatewayError, BadJSON, FileMakerError) as e:
            if isinstance(e, RequestException):
                logging.error(f'Unable to connect to the server, check that the server url is correct: {str(e)}')
            elif isinstance(e, BadGatewayError):
                logging.error(f'Unable to connect to the server, make sure the Data API connector is enabled: {str(e)}')
            elif isinstance(e, BadJSON):
                logging.error(f'Unable to connect to the server, make sure the Data API connector is enabled: {str(e)}')
            elif isinstance(e, FileMakerError):
                logging.error(f'Unable to login to the server with the credentials provided: {str(e)}')
        return None
