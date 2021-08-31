import csv
import logging
import pathlib
import yaml

"""
PARSER_CONF_PATH = 'parser_config.yaml'
with open(PARSER_CONF_PATH, 'r') as f:
    config = yaml.load(f, yaml.SafeLoader)
    # TODO: Validation / error checking and graceful exit on error
"""

logger = logging.getLogger(__name__)

class RequiredFieldMissingError(Exception):
    def __init__(self, file, field):
        message = f'Field \'{field}\' is required, but was not found\nFile: \'{file}\''
        super().__init__(message)

def parse(path: str, program: str, sep: str, fields: list) -> dict:
    # Default headers that should be always exported
    # TODO: Configure similarly for programs other than Qualipoc
    if program.lower() == 'qpoc':
        TIME_FIELD = 'Time'
        LATITUDE_FIELD = 'Lat'
        LONGITUDE_FIELD = 'Long'
        SPEED_FIELD = 'Speed o.g.'
        ALTITUDE_FIELD = 'Altitude'
    elif program.lower() == 'nemo':
        pass

    META_FIELDS = [TIME_FIELD, LATITUDE_FIELD, LONGITUDE_FIELD, SPEED_FIELD, ALTITUDE_FIELD]

    with open(path, 'r') as file:
        # Qualipoc uses 0-width space in some fields,
        # which ofc cannot be seen or typed into config...
        # so get rid of these
        headers = file.readline().replace('\u200b', '').replace('\n', '')

        reader = csv.DictReader(file, fieldnames=headers.split(sep), delimiter=sep)

        headers = headers.split(sep)

        if TIME_FIELD not in headers:
            raise RequiredFieldMissingError(file, TIME_FIELD)

        takeoff_altitude = None
        altitude_delta = None
        parsed = {}
        for field in fields:
            parsed[field] = []
        present_meta_fields = (field for field in META_FIELDS if field in headers) # doc: Generator expressions
        for field in present_meta_fields:
            parsed[field] = []
        if ALTITUDE_FIELD in fields:
            parsed['altitude_delta'] = []
        
        for row in reader:
            if ALTITUDE_FIELD in fields:
                if row[ALTITUDE_FIELD] == None or row[ALTITUDE_FIELD] == '':
                    continue
                if altitude_delta == None:
                    altitude_delta = float(row[ALTITUDE_FIELD])
                if takeoff_altitude == None:
                    takeoff_altitude = float(row[ALTITUDE_FIELD])

                parsed['altitude_delta'].append(float(row[ALTITUDE_FIELD]) - takeoff_altitude)
        
            for field in set(parsed.keys() - present_meta_fields - {'altitude_delta'}): #fields:
                if field not in parsed: print("fuck")
                if field not in row: print("shit")
                parsed[field].append(row[field])

    return parsed
