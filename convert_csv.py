#!/usr/bin/python
# PYTHON_ARGCOMPLETE_OK
import argparse

################################################################################

parser = argparse.ArgumentParser(
    description='convert BBBank csv exports to HomeBank csv')

parser.add_argument('files', nargs='+',
                    help='input BBBank csv')
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

lines_out = set()

for file in args.files:
    reader = csv.reader(open(file, encoding='iso-8859-1'), delimiter=';')

    # read column header
    line = next(reader)

    # get indices by column headers
    i_date = line.index('Buchungstag')
    i_info = line.index('Verwendungszweck')
    i_payee = line.index('Name Zahlungsbeteiligter')
    i_amount = line.index('Betrag')

    # read transactions
    for line in reader:
        if not line or not any(line):
            continue
        date = line[i_date]
        info = line[i_info].replace('\n', ' ')
        payee = line[i_payee]
        amount = float(line[i_amount].replace('.', '').replace(',', '.'))

        if args.verbose:
            print('-'*80, file=sys.stderr)
            print('date', date, file=sys.stderr)
            print('info', info, file=sys.stderr)
            print('payee', payee, file=sys.stderr)
            print('amount', amount, file=sys.stderr)

        lines_out.add(';'.join([
            date,
            '0',  # payment
            info,
            payee,
            '',  # memo
            str(amount),
            '',  # category
            '',  # tags
        ]))

lines_out = list(lines_out)
lines_out.sort()

for l in lines_out:
    print(l, file=f_out)