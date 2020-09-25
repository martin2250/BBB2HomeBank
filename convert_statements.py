#!/usr/bin/python
# PYTHON_ARGCOMPLETE_OK
import argparse

################################################################################

parser = argparse.ArgumentParser(
    description='convert BBBank pdf statements to HomeBank csv')

parser.add_argument('files',
                    nargs='+',
                    help='input BBBank pdfs')
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
    import subprocess
    import re
    import pathlib
    from dataclasses import dataclass
    from typing import List
    import multiprocessing
    from concurrent.futures import ThreadPoolExecutor

################################################################################


@dataclass
class Transaction:
    date: str
    info: str
    amount: float
    payee: str


def readfile(path: pathlib.Path, transactions: List[Transaction]):
    if args.verbose:
        print('reading ', path, file=sys.stderr)
    # extract year from file name, eg. XXXXXXX_2019_Nr.007_Kontoauszug_vom_XXXXXX.pdf
    _, year, _ = path.name.split('_', maxsplit=2)
    # extract pdf text with pdfbox
    command = [
        'java', '-jar', '/usr/share/pdfbox/pdfbox.jar',
        'ExtractText',
        '-console',
        path
    ]
    text = subprocess.check_output(
        command, stderr=subprocess.DEVNULL).decode(errors='ignore')
    # current transaction (references span multiple lines)
    transaction = None
    # go through text
    for line in text.split('\n'):
        # remove newline
        line = line.rstrip()
        # last line contained a transaction
        if transaction:
            # transaction continued
            if line.startswith('              '):
                # first continuation contains the payee
                if transaction.payee == '':
                    transaction.payee = line.strip()
                else:
                    transaction.info += ' ' + line.strip()
            # stop transaction
            else:
                transactions.append(transaction)
                transaction = None
        # new transactions start with date (day.month.) eg. "25.07. 25.07. "
        if re.match(r'^\d\d\.\d\d\. \d\d\.\d\d\. ', line):
            date, _, text = line.split(' ', maxsplit=2)
            text, amount, sh = text.rsplit(' ', maxsplit=2)
            amount = float(amount.replace('.', '').replace(',', '.'))
            # 'S' soll -> money spent, 'H' haben -> money received
            if sh == 'S':
                amount *= -1
            elif sh != 'H':
                raise Exception(f'invalid S or H in line "{sh}"')
            transaction = Transaction(date + year, text.strip(), amount, '')


################################################################################

files = []
for path in args.files:
    path = pathlib.Path(path)
    if not path.exists():
        print(f'input file {path} does not exist')
        exit(1)
    files.append(path)

################################################################################

transactions = []
tpe = ThreadPoolExecutor(max_workers=multiprocessing.cpu_count())

for path in files:
    tpe.submit(readfile, path, transactions)

tpe.shutdown()

transactions.sort(key=lambda tr: ''.join(tr.date.split('.')[::-1]))

################################################################################

f_out = sys.stdout
if args.output:
    f_out = open(args.output, 'w')

for transaction in transactions:
    if args.verbose:
        print('-'*80, file=sys.stderr)
        print('date', transaction.date, file=sys.stderr)
        print('info', transaction.info, file=sys.stderr)
        print('payee', transaction.payee, file=sys.stderr)
        print('amount', transaction.amount, file=sys.stderr)

    print(';'.join([
        transaction.date,
        '0',  # payment
        transaction.info,
        transaction.payee,
        '',  # memo
        str(transaction.amount),
        '',  # category
        '',  # tags
    ]), file=f_out)
