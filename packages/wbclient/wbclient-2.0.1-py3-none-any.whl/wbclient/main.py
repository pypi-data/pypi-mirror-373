#!/usr/bin/env python
# -*- coding: utf-8 -*-

# main.py

import os
import sys
import datetime
import getpass
import time
import logging
import keyboard
from os import environ as env
from pathlib import Path
project_root = Path(__file__).parent.parent  # Assuming main.py is in wbclient/
sys.path.insert(0, str(project_root))
os.chdir(project_root)
from wbclient.wb_server import get_payload_global_id
from wbclient.wb_logfile import get_log_files
from wbclient.wb_processes import get_server_information, SystemInfo
from wbclient.wb_commands import CommandScanner
from wbclient.wb_config import load_global_config
logging.basicConfig(level=logging.INFO)

configuration = load_global_config()
if not configuration:
    print("Something very bad happened here...")
    print("Probably something in your wb_config.json file isn't set correctly")
    sys.exit()

global_record_id = get_payload_global_id()
if not global_record_id:
    print("Something went wrong loading the configuration from FileMaker")
    print("Probably something in your wb_config.json file isn't set correctly")
    sys.exit()

logging.info(f'running as user {getpass.getuser()}')

# PWA: keyboard control
stop_key = 'esc'
stop = False
next_loop_key = "right"
next_loop = False


def onkeypress(event):
    global stop
    global next_loop
    # print (event.name)
    if event.name == stop_key:
        logging.info(f"asked to stop using {stop_key} key…")
        stop = True
    elif event.name == next_loop_key:
        # print(f"asked to go into next loop using {next_loop_key} key…")
        next_loop = True


is_root = os.geteuid() == 0
if is_root:
    if env['keyboard_control'] == 'True':
        logging.info(f"keyboard control is active, use {stop_key} to exit, {next_loop_key} key to run the next loop")
        keyboard.on_press(onkeypress)
    else:
        logging.info("no keyboard control set in config")
else:
    logging.info("current user not root, no keyboard control 4 u")
    logging.info("current user not root, no cpu 4 u")

scanner = CommandScanner()
info = SystemInfo()

logs_to_process = get_log_files()
logging.debug(f"got {len(logs_to_process)} logs")


def exit_application():
    global scanner
    # so let's force logouts, so we do not have lingering connections
    # ask David if he can write a destructor that logs out
    if hasattr(scanner, 'server'):
        scanner.server.logout()
    if hasattr(info, 'server'):
        info.server.logout()
    for log_file in logs_to_process:
        if hasattr(log_file, 'server'):
            log_file.server.logout()

    sys.exit()


def main():
    interval = env['post_interval']
    global stop
    global next_loop
    global scanner
    global info
    # if not logs_to_process:
    #     sys.exit("could not connect")
    while True:
        scanner.scan_for_commands()
        if is_root:
            data_info = get_server_information()
            if data_info:
                logging.debug(data_info)
                # print("posting server info")
                now_datetime_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                info.post_info_data(data_info, global_record_id, now_datetime_str)
            else:
                logging.error('no server information')

        for log_file in logs_to_process:
            if stop:
                logging.debug("wil exit log loop")
                break
            logging.debug(log_file.file_path)
            data, last_timestamp, eof, row_count = log_file.read_log()
            logging.debug(data)
            if data:
                logging.info(f"posting data for '{log_file.file_path}' until {last_timestamp}")
                log_file.post_logfile_data(data, global_record_id, log_file.id_configuration, last_timestamp, eof)
            else:
                logging.debug(f"no data to send for log file '{log_file.file_path}'")
        # print(f"wil now sleep for {interval} seconds…")
        i = 0
        while i < int(interval):
            if stop:
                logging.debug("wil stop now")
                exit_application()
            if next_loop:
                # print("next loop")
                next_loop = False
                break
            time.sleep(1)

            i += 1


if __name__ == "__main__":
    main()
