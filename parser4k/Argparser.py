import argparse

def get_cli_args():
    parser = argparse.ArgumentParser(description='This is the best data parser ever', prog='Parser4k')
    parser.add_argument('config', help='Specify configuration file.')
    parser.add_argument('-v', '--verbose', action='store_true', help='Sets logging level to info.')
    parser.add_argument('-d', '--debug', action='store_true', help='Sets logging level to debug.')
    parser.add_argument('--flush', action='store_true', help='Flushes database before running.')

    return vars(parser.parse_args())
