"""
Get prices from one file and use this prices fo all products in another file.
write result with correct prices in output file.

Usage:
    fix_price.py --if=<infile> --df=<datafile> --of=<output_file>
"""
from docopt import docopt
from clint.textui import progress
arguments = docopt(__doc__)
ifile = arguments['--if']
dfile = arguments['--df']
ofile = arguments['--of']

prices = {}
with open(ifile) as inf:
    for line in inf.readlines():
        game_data = line.split('\t')
        name = game_data[1]
        price = game_data[2]
        prices[name] = price

new_lines = []
with open(dfile) as df:
    for line in df.readlines():
        game_data = line.split('\t')
        name = game_data[1]
        game_data[2] = prices.get(name,'0')
        new_lines.append('\t'.join(game_data))

with open(ofile,'w') as of:
    of.writelines(new_lines)
