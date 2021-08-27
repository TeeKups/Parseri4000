import json
import logging
import multiprocessing as mp
import pathlib
import re
import requests
import signal
import yaml

from collections import namedtuple
from shutil import copyfile
from sys import exit
from sys import version_info as version
from time import sleep

from . import Argparser
from . import parser

MIN_PYTHON_VERSION = (3, 9, 6) # 3.8.0 should be alright, but not tested
if version[0:3] < MIN_PYTHON_VERSION:
    exit('Python version %s.%s.%s or later is required!\n' % MIN_PYTHON_VERSION)

ROOT_PATH = pathlib.Path(__file__).parent

mutex = mp.Lock()
File = namedtuple('File', 'path, program, profile')

logger = logging.getLogger(__name__)

def get_extension(path: pathlib.Path) -> str:
    return str(path).split('.')[-1]

def read_db(db: str) -> dict:
    try: 
        with open(str(pathlib.Path(ROOT_PATH, config['db_file'])), 'r') as db_file:
            db = json.loads(db_file.read())
    except (json.decoder.JSONDecodeError, FileNotFoundError):
        db = {}
    finally:
        return db

def add_to_db(db: dict, file: File) -> None:
    mutex.acquire()

    if file.path not in db:
        db[file.path] = {}
    if file.program not in db[file.path]:
        db[file.path][file.program] = {}
    if file.profile not in db[file.path][file.program]:
        db[file.path][file.program][file.profile] = {}

    db[file.path][file.program][file.profile]['last_modified'] = pathlib.Path(ROOT_PATH, file.path).stat().st_mtime

    mutex.release()
   
def get_new_files(DATA_ROOT: str, config: dict, db: dict) -> list[tuple[File]]:
    new_files = []
    for program_name, program in config.items():
        root = program['root']
        extension = program['extension']
        for profile_name, profile in program['profiles'].items():
            logging.debug(f'Reading {str(pathlib.Path(DATA_ROOT, root, profile["subdir"]))}')
            for file in pathlib.Path(DATA_ROOT, root, profile['subdir']).iterdir():
                if get_extension(file) != extension:
                    continue
                elif str(file) not in db \
                or program_name not in db[str(file)] \
                or profile_name not in db[str(file)][program_name] \
                or db[str(file)][program_name][profile_name]['last_modified'] < file.stat().st_mtime \
                    : new_files.append(File(str(file), program_name, profile_name))

    if len(new_files) > 0:
        logging.info(f'{len(new_files)} new files found')

    return new_files

def send_to_es(file: tuple, config: dict) -> int:
    logger.info(f'Parsing {file.path}...')
    path = file.path
    program = file.program
    sep = config['programs'][file.program]['separator']
    fields = config['programs'][file.program]['profiles'][file.profile]['headers']

    parsed_fields = parser.parse(path, program, sep, fields)
    logger.info(f'Done parsing {path}')


    documents = ''
    index_template = '{"index": {"_index": "%s_%s_%s", "_type": "_doc", "_id": %d}\n'

    for i, row in enumerate(zip(*parsed_fields.values())):
        doc = ''
        for key,val in ((key,val) for (key,val) in zip(parsed_fields.keys(), row)):
            if re.match(r'^-?[0-9]+$', val) is not None:
                # int
                doc += f'"{key}": {val},'
            elif re.match(r'^-?[0-9]+\.[0-9]+$]', val) is not None:
                # float
                doc += f'"{key}": {val},'
            else:
                # string
                doc += f'"{key}": "{val}",'

        documents += index_template % (file.program, pathlib.Path(path).stem ,file.profile, i)
        documents += '{%s}\n' % (doc[0:-1])

    res = requests.put(config['es_url'], headers={'Content-Type': 'application/json'}, data=documents)
    
    for item in json.loads(res.text)['items']:
        if item['index']['status'] not in [200, 201]:
            logging.error(json.dumps(item, indent=2))
    
    return res.status_code

class DummyException(Exception):
    # For debugging
    pass

def main(config: dict) -> None:
    files_queue = mp.JoinableQueue()
    # TODO: Potential performance gains from actually synchronizing db operations
    #       and using a simple Queue instead of waiting for the JoinableQueue to finish
    #       between each process-pool run...
    #       Currently used jsut so that the DB is in a synchronized state before reading,
    #       and writing is done in serial

    DATA_ROOT = config['data_root']
    db_path = str(pathlib.Path(ROOT_PATH, config['db_file']))
    db = read_db(db_path)
    logging.debug(f'Database is at {db_path}')
    # TODO: **Maybe** turn this into an actual DB at some point, instead of just a json file

    running = True
    # TODO: Make some way to either quit/restart or daemonize/reload the program
    #       Currently just exit with Ctrl+C and start again

    def sent(*args):
        files_queue.task_done()

    def init_worker():
        signal.signal(signal.SIGINT, signal.SIG_IGN)

    with mp.Pool(initializer=init_worker) as pool: 
        new_iteration = True
        while running:
            try:
                # Gets newly added files
                # DB must be in a synchronized state -- i.e. all processed files/profiles are there
                if new_iteration:
                    print('Searching new files...')
                    new_iteration = False

                for file in (files := get_new_files(DATA_ROOT, config['programs'], db)):
                    files_queue.put(file)

                if files_queue.qsize() == 0:
                    sleep(1) # If no files were found, we can wait a second... This *really* reduces cpu load
                    continue

                print(f'Processing {files_queue.qsize()} files...')

                # Processes said files
                results = []
                while not files_queue.qsize() == 0:
                    results.append(pool.apply_async(send_to_es, args=(files_queue.get(), config), callback=sent))
                
                # Waits until files are processed
                for result in results:
                    result.get()

                files_queue.join()
                print('Files processed')

                # Updates DB
                logging.debug('Updating DB')
                for file in files:
                    add_to_db(db, file)

                new_iteration = True
                # Rinse and repeat
            except KeyboardInterrupt:
                print()
                running=False
                pass

    backup_path = db_path + '.bk'
    print(f'Saving database... In case of corruption, backup can be located at {backup_path}')
    copyfile(db_path, backup_path)

    with open(db_path, 'w') as f:
        json.dump(db, f, indent=4)

    print('DONE')


def validate_config(file) -> bool:
    # TODO: Somehow validate the configuration file --- or maybe just rely on error handling
    return True

if __name__ == '__main__':
    argd = Argparser.get_cli_args()
    
    logger = logging.getLogger(__name__)
    if argd['debug']:
        loglevel = logging.DEBUG
    elif argd['verbose']:
        loglevel = logging.INFO
    else:
        loglevel = logging.ERROR

    logging.basicConfig(format='{name} {levelname:8s}: {message}',
            style='{',
            level=loglevel)

    if argd['config'] == '':
        logging.critical('Must specify a config file!')
        exit()
    elif not pathlib.Path(argd['config']).is_file():
        logging.critical('Invalid configuration file name!')
        exit()
    elif not validate_config(argd['config']):
        logging.critical('Bad config file!')
        exit()

    try:
        with open(argd['config'], 'r') as f:
            config = yaml.load(f, yaml.SafeLoader)
    except Exception as e:
        logging.error(e)
        logging.critical('Bad config file!')
        exit()

    if argd['flush']:
        with open(str(pathlib.Path(ROOT_PATH, config['db_file'])), 'w') as db_file:
            db_file.write('{}')
        logging.info('Database flushed')

    try:
        main(config)
    except:
        pass


