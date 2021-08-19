import csv
import tkinter as tk
import pathlib
import logging
import os
import multiprocessing as mp
import json

from queue import Queue

from . import Argparser
from .misc import error as error

import parser4k.qpoc_parser as qpoc
import parser4k.ts3k_parser as ts3k
import parser4k.clocker_parser as clocker

def get_extension(path) -> str:
    return str(path).split('.')[-1]

def start(config) -> None:
    send_queue = Queue()


    qpoc_parser_proc = mp.Process(target=qpoc.parse args=(qpoc_files, qpoc_params))
    #nemo_parser_proc = mp.Process(target=nemo.parse, args=(nemo_files, nemo_params))

    while qpoc_parser_proc.is_alive() \
    or not send_queue.empty():
        documents = ''

        

        while not send_queue.empty() \
        and line_counter % config['ex_max_documents_per_request'] != 0:
            try:
                item = send_queue.get(timeout=1)
            except Empty:
                pass
            else:
                documents += str(item) + '\n'
                line_counter += 1






    # All subprocesses have quit
    # So we can update the database
    # Currently all files _should_ be uploaded
    # Save file paths and timestamps to db

    with open(config['db_file'], 'r') as f:
        db = json.loads(f.read())

    for program in config['programs']:
        rootdir = program['rootdir']
        for profile in program['profiles']:
            subdir = profile['subdir']
            for fname in pathib.Path(program_root, rootdir, subdir).iterdir():
                if not fname.is_file() \
                or get_extension(fname) != 'csv':
                    continue

                timestamp = fname.stat().st_mtime

                if program not in db:
                    db[program] = {}
                if profile not in db[program]:
                    db[profile] = {}
                if str(fname) not in db[program][profile]:
                    db[program][profile][str(fname)] = { 'last_modified': timestamp }
                elif timestamp < db[program][profile][str(fname)]['last_modified']:
                    db[program][profile][str(fname)]['last_modified'] = timestamp

    with open(config['db_file'], 'w') as f:
        f.write(json.dumps(db, sort_keys=False, indent=4))


def validate_config(file) -> bool:
    # TODO: Somehow validate the configuration file --- or maybe just rely on error handling
    return true

if __name__ == '__main__':
    logging.basicConfig(level=logging.WARNING)
    argd = Argparser.get_cli_args()
    if args['config'] == '':
        error('Must specify a config file!')
    else if not os.path.isfile(argd['config']):
        error('Invalid configuration file name!')
    else if not validate_config(argd['config']):
        error('Bad config file!')
    else:
        try:
            with open(argd['config'], 'r') as f:
            config = yaml.load(f, yaml.SafeLoader)
        except:
            error('Bad config file!')
        else:    
            start(config)
        

    """
    if argd['type'] == 'qpoc':
        qpoc.parse(argd['files'], argd['preview_flag'])
    elif argd['type'] == 'ts3k':
        ts3k.parse(argd['files'])
    elif argd['type'] == 'clocker':
        clocker.parse(argd['files'])
    else:
        error('Unknown type!')
    """
