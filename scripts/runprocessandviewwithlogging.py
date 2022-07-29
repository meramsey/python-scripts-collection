#!/usr/bin/env python3
# import io
import logging
import pathlib
import os
import datetime as DT

dstamp = DT.datetime.now().strftime("%Y%m%d")

log_path_folder = "/home/ubuntu/logs/"
debug_log_name = "debug.log"
info_log_name = "info.log"
log_folder = pathlib.Path(log_path_folder)

DEBUGFORMATTER = "%(filename)s:%(name)s:%(funcName)s:%(lineno)d: %(message)s"
"""Debug file formatter."""

INFOFORMATTER = "%(message)s"
"""Log file and stream output formatter."""


def init_log_files(log, mode="w"):
    """
    Initiate log files.

    Two files are initiated:

    1. :py:attr:`myapp.logger.DEBUGFILE`
    2. :py:attr:`myapp.logger.INFOFILE`

    Adds the two files as log Handlers to :py:attr:`log`.

    Parameters
    ----------
    mode : str, (``'w'``, ``'a'``)
        The writing mode to the log files.
        Defaults to ``'w'``, overwrites previous files."""
    # here, I show a very simple configuration,
    # but you can extend it to how many handlers
    # and tweaks you need.
    pathlib.Path.mkdir(log_folder, parents=True, exist_ok=True)
    # print(f'Log Folder: {log_folder}')
    DEBUGFILE = os.path.join(log_path_folder, debug_log_name)
    INFOFILE = os.path.join(log_path_folder, info_log_name)
    # print(f'Log DEBUGFILE: {DEBUGFILE}')
    # print(f'Log INFOFILE: {INFOFILE}')
    db = logging.FileHandler(DEBUGFILE, mode=mode)
    db.setLevel(logging.DEBUG)
    db.setFormatter(logging.Formatter(DEBUGFORMATTER))

    info = logging.FileHandler(INFOFILE, mode=mode)
    info.setLevel(logging.INFO)
    info.setFormatter(logging.Formatter(INFOFORMATTER))

    log.addHandler(db)
    log.addHandler(info)


def get_logger():
    # import ... # Python standard library imports here
    import logging

    log = logging.getLogger(__name__)
    if log.hasHandlers():
        log.handlers = []
    log.setLevel(logging.DEBUG)
    _ch = logging.StreamHandler()
    _ch.setLevel(logging.INFO)
    _ch.setFormatter(logging.Formatter(INFOFORMATTER))
    log.addHandler(_ch)

    return log


log = get_logger()
init_log_files(log)


def run_command(cmd):
    from subprocess import Popen, PIPE, STDOUT
    from shlex import split
    import sys

    try:
        log.info(f"executing: {str(cmd)} ")
        process = Popen(split(cmd), stdout=PIPE, stderr=STDOUT, encoding="utf8")
        while True:
            output = process.stdout.readline()
            if output == "" and process.poll() is not None:
                # print("no output")
                log.info("no output")
                break
            if output:
                # print(output.strip())
                log.info(output.strip())
        rc = process.poll()
        return rc
    except KeyboardInterrupt:
        # process.terminate()
        exit()
    except Exception as ex:
        log.error("Encountered an error : ", ex)


# install netcat to use
# run_command('nc -k -l 6514')
# run_command('ls -lah')
cmd = '/bin/bash -c "/home/ubuntu/somescript.sh 2>&1"'
log.info(f"Running {cmd}")
run_command(cmd)
