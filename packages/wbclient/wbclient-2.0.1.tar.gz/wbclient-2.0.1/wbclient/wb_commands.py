import logging
import fmrest
from fmrest.exceptions import BadGatewayError, FileMakerError, FMRestException, RequestException
from os import environ as env
import subprocess
import json
import os
from wbclient.wb_server import get_fmserver_connection


class CommandScanner:
    def __init__(self):
        self.server = get_fmserver_connection("control")
        try:
            self.server.login()
        except RequestException as e:
            logging.error(f'Unable to connect to the server, check that the server url is correct: {str(e)}')
        except BadGatewayError as e:
            logging.error(f'Unable to connect to the server, make sure the Data API connector is enabled: {str(e)}')
        except fmrest.exceptions.FileMakerError as e:
            logging.error(f"An error happened reading the Command Scanner:{str(e)}")
        except FMRestException as e:
            logging.error(f"An error happened logging into FileMaker: {str(e)}")

    def __del__(self):
        logging.debug("scanner self destruction")
        try:
            self.server.logout()
        except FMRestException as e:
            logging.debug(f"Tried logging out with no server connectio: {str(e)}")

    def scan_for_commands(self):
        logging.debug("scanning for commands")
        find_query = [{'done': 0}]
        try:
            foundset = self.server.find(find_query)
            logging.info(f"Found {foundset.info['foundCount']} commands to execute")
        except fmrest.exceptions.FileMakerError as e:
            foundset = []
            logging.debug(f"No commands found to process: {e}")
        for record in foundset:
            args = []
            user = env['command_user']
            # shell = False
            command_string = record.command_string
            whitelist_string = env["command_whitelist"].replace("'", "\"")
            whitelist_array = json.loads(whitelist_string)
            for item in whitelist_array:
                if item["command"] == command_string:
                    user = "root"
                    # shell = False
            workdir = record.work_dir
            argument_string = record.argument_string
            if '' != argument_string:
                args.append(argument_string)
            err = False
            print(user)
            try:
                result = subprocess.check_output(
                    executable=command_string,
                    args=args,
                    text=True,
                    user=user,
                    #shell=shell,
                    cwd=workdir
                )
            except subprocess.CalledProcessError as e:
                logging.error(e)
                result = "ERROR: CalledProcess #" + str(e.returncode)
                err = True
                pass
            except PermissionError as e:
                logging.error(e)
                result = "ERROR: Permission #" + str(e.errno)
                err = True
                pass
            except FileNotFoundError as e:
                logging.error(e)
                result = "ERROR: FileNotFound #" + str(e.errno)
                err = True
                pass
            except KeyError as e:
                logging.error(e)
                result = "ERROR: KeyError #" + str(e)
                err = True
                pass

            record['result'] = result
            record['done'] = 2 if err else 1
            self.server.edit(record)

            # implement this, it is the only way to propertly reboot
            # os.system("reboot now")