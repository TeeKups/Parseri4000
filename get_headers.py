import argparse

parser = argparse.ArgumentParser()
parser.add_argument('PATH', nargs=1, help='File path')
parser.add_argument('-d', nargs=1, help='Delimiter: , for csv \\t for tsv etc')
args = vars(parser.parse_args())
with open(str(args['PATH'][0]), 'r') as f:
    line = f.readline()

delim = args['d'][0]
line = line.replace(delim, f"'{delim}'")
print(f"['{line[0:-1]}']")
