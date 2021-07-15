import csv
import tkinter as tk
import pathlib

from . import Argparser
from .misc import error as error

import parser4k.qpoc_parser as qpoc
import parser4k.ts3k_parser as ts3k
import parser4k.clocker_parser as clocker


if __name__ == '__main__':
    argd = Argparser.get_cli_args()
    if argd['type'] == 'qpoc':
        qpoc.parse(argd['files'])
    elif argd['type'] == 'ts3k':
        ts3k.parse(argd['files'])
    elif argd['type'] == 'clocker':
        clocker.parse(argd['files'])
    else:
        error('Unknown type!')
