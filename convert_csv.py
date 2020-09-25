#!/usr/bin/python
# PYTHON_ARGCOMPLETE_OK
import argparse

################################################################################

parser = argparse.ArgumentParser(
    description='convert BBBank csv exports to HomeBank csv')

parser.add_argument('file',
                    help='input BBBank csv')
parser.add_argument('-s', '--skip',
                    help='skip lines',
                    default=13, type=int)
parser.add_argument('-o', '--output',
                    help='output homebank csv')
parser.add_argument('-v', '--verbose',
                    help='print info for each line',
                    action='store_true')

################################################################################

try:
    import argcomplete
    argcomplete.autocomplete(parser)
except ImportError:
    pass

################################################################################

args = parser.parse_args()

################################################################################
# trick isort

if True:
    import sys
    import csv

################################################################################

f_out = sys.stdout
if args.output:
    f_out = open(args.output, 'w')

f_in = open(args.file, errors='ignore')
for _ in range(args.skip):
    f_in.readline()

for line in csv.reader(f_in, delimiter=';'):
    if not line:
        continue
    if 'Anfangssaldo' in line or 'Endsaldo' in line:
        continue
    date = line[0]
    info = line[8].replace('\n', ' ')
    payee = line[3]
    amount = float(line[-2].replace('.', '').replace(',', '.'))
    if line[-1] == 'S':
        amount *= -1

    if args.verbose:
        print('-'*80, file=sys.stderr)
        print('date', date, file=sys.stderr)
        print('info', info, file=sys.stderr)
        print('payee', payee, file=sys.stderr)
        print('amount', amount, file=sys.stderr)

    print(';'.join([
        date,
        '0',  # payment
        info,
        payee,
        '',  # memo
        str(amount),
        '',  # category
        '',  # tags
    ]), file=f_out)
