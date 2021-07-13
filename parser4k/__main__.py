import csv
import tkinter as tk
import pathlib

from . import Argparser
from .misc import error as error

if __name__ == '__main__':
    argd = Argparser.get_cli_args()
    if argd['type'] == 'qpoc':
        qpoc(argd['files'])
    elif argd['type'] == 'ts3k':
        ts3k(argd['files'])
    elif argd['type'] == 'clocker':
        clocker(argd['files'])
    else:
        error('Unknown type!')
