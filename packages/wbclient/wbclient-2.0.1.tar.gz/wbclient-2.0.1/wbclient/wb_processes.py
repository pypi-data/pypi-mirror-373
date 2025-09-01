import psutil as psu
import time
from datetime import timedelta
import json
import logging
from wbclient.wb_server import get_fmserver_connection
from os import environ as env
import fmrest
from fmrest.exceptions import BadGatewayError, FileMakerError, FMRestException, RequestException


class SystemInfo:
    def __init__(self):
        self.server = get_fmserver_connection("post")
        try:
            self.server.login()
        except RequestException as e:
            logging.error(f'Unable to connect to the server, check that the server url is correct: {str(e)}')
        except BadGatewayError as e:
            logging.error(f'Unable to connect to the server, make sure the Data API connector is enabled: {str(e)}')
        except fmrest.exceptions.FileMakerError as e:
            logging.error(f"An error happened getting the system info connection:{str(e)}")
        except FMRestException as e:
            logging.error(f"An error happened logging into FileMaker: {str(e)}")

    def post_info_data(self, the_data, record_id, last_timestamp):
        logging.debug("Sending server info to Whistleblower server")
        try:
            my_data = {
                "payload": the_data,
                "id_server": self.server.user,
                "timestamp_stop": last_timestamp,
            }
            self.server.edit_record(record_id, my_data, scripts={
                'after': [env['post_script'], 'info']
            })
            logging.debug(self.server.last_script_result)
            logging.debug("OK -")

            return True
        except RequestException as e:
            logging.error(f'Unable to connect to the server, check that the server url is correct: {str(e)}')
        except BadGatewayError as e:
            logging.error(f'Unable to connect to the server, make sure the Data API connector is enabled: {str(e)}')
        except fmrest.exceptions.FileMakerError as e:
            logging.error(f"An error happened posting info data:{str(e)}")
        except FMRestException as e:
            logging.error(f"An error happened logging into FileMaker: {str(e)}")
        return False


def get_server_information():
    data = []
    logging.debug("Collecting info")
    # cpu
    try:
        info = {
            "cpu_uptime": time.time() - psu.boot_time(),
            "cpu_usage": f"{psu.cpu_percent(interval=.1)}%",
            "cpu_time": f"{timedelta(seconds=psu.cpu_times().system + psu.cpu_times().user)}",
        }
    except psu.Error as e:
        info = {}
        # logging.error("failed to obtain cpu information")
        logging.error(str(e))
        pass

    data.append({"cpuInfo": info})
    # memory
    info = {
        "mem_usage": f"{psu.virtual_memory().percent}%",
        "mem_avail": f"{psu.virtual_memory().available / 1024 ** 2} GB",
    }
    data.append({"memInfo": info})
    # disk usage
    logging.debug("Collecting disk storage")
    partitions_list = []
    for part in psu.disk_partitions(all=False):
        try:
            partitions_list.append({
                "mount_point": part.mountpoint,
                "disk_used": f"{round(psu.disk_usage(part.mountpoint).used / 1024 ** 3, 2)} GB",
                "disk_free": f"{round(psu.disk_usage(part.mountpoint).free / 1024 ** 3, 2)} GB"
            })
        except psu.Error:
            # ignore the error, do not report using logging
            pass  # happens with CD roms etc.
    data.append({"diskInfo": partitions_list})
    # processes
    process_list = []
    logging.debug("Collecting process information")
    for proc in psu.process_iter(
            attrs={"name", "pid", "username", "create_time", "cpu_percent", "cpu_times", "num_threads",
                   "memory_percent"}):
        if "fms" in proc.name() or "apache" in proc.name() or "nginx" in proc.name():
            try:
                info = {
                    "name": proc.name(),
                    "pid": proc.pid,
                    "username": proc.username(),
                    "up_time": time.time() - proc.create_time(),
                    "cpu_usage": proc.cpu_percent(),
                    "threads": proc.num_threads(),
                    "mem_usage": f"{(round(proc.memory_percent(), 2))}%",
                }
                process_list.append(info)
            except psu.Error as e:
                logging.error(f"Failed to obtain process information for {proc.name()}: {str(e)}")
                pass
    data.append({"processInfo": process_list})

    data_str = json.dumps(data)
    return data_str
