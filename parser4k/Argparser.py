import argparse

def get_cli_args():
    argd = {}

    parser = argparse.ArgumentParser(description='Ebin data parser', prog='Parser4k')
    parser.add_argument('TYPE', choices=['qpoc', 'ts3k', 'clocker'], help='Source data format.')
    parser.add_argument('FILES', nargs='+', help='File names for parsing.')

    args = parser.parse_args()
    argd['files'] = args.FILES
    argd['type'] = args.TYPE

    return argd
