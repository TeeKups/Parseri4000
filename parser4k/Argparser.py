import argparse

def get_cli_args():
    argd = {}

    parser = argparse.ArgumentParser(description='This is the best data parser ever', prog='Parser4k')
    parser.add_argument('CONFIG', help='Specify configuration file')
    "
    parser.add_argument('TYPE', choices=['qpoc', 'ts3k', 'clocker'], help='Source data format.')
    parser.add_argument('FILES', help='File names for parsing.')
    parser.add_argument('-p', '--preview', action='store_true', help='Include to preview, exclude to save file.')
    "

    args = parser.parse_args()
    argd['config'] = args.CONFIG
    "
    argd['files'] = args.FILES
    argd['type'] = args.TYPE
    argd['preview_flag'] = args.preview
    "

    return argd
