#!/usr/bin/env python
""" Find citekeys from the LaTeX aux file and filter records matching these
    from a BibTeX database.
"""
import re

def parse_aux_citekeys(filename):
    """ Parse the LaTeX aux file for BibTeX citations and return their keys.
    """
    blacklist = {'REVTEX41Control', 'aip41Control'}
    citekeys = set()
    with open(filename, 'r') as f:
        for line in f:
            m = re.match(r'\\citation\{(.+)\}|\\abx@aux@cite\{(.+)\}', line)
            if not m:
                continue
            keys = [x.strip() for x in
                    (s for s in m.groups() if s is not None).next().split(',')]
            citekeys |= set(keys)
    return list(citekeys - blacklist)

class BibTeX(object):
    """ Dumb BibTeX parser using regular expressions. """ 
    def __init__(self, filename):
        self.filename = filename
        self.data = open(filename, 'r').read()

    def get_entry(self, citekey):
        """ Returns the BibTeX record for ``citekey`` if available. """
        regex = r'@\w+\{%s,\n.+?\n\}\n' % citekey
        m = re.search(regex, self.data, re.MULTILINE | re.DOTALL)
        return m.group(0).strip() if m is not None else None

if __name__ == '__main__':
    import argparse
    import sys
    parser = argparse.ArgumentParser(description='Find citekeys from the '
    'LaTeX aux file and filter records matching these from a BibTeX database.')
    parser.add_argument('database', help='BibTeX database filename')
    parser.add_argument('--aux', default=None,
            help='LaTeX aux file to read (default: first match of *.aux)')
    parser.add_argument('--output', default=sys.stdout,
            help='Output for filtered BibTeX records (default: stdout)')

    args = parser.parse_args()
    if args.aux is None:
        from glob import glob
        auxfiles = glob('*.aux')
        if len(auxfiles) == 0:
            print 'Error: no aux files available.'
            sys.exit(1)
        args.aux = auxfiles[0]
    
    citekeys = parse_aux_citekeys(args.aux)
    database = BibTeX(args.database)
    entries = [database.get_entry(x) for x in citekeys]
    
    output = args.output if type(args.output) is file else open(args.output, 'w')
    with output as f:
        for citekey, entry in zip(citekeys, entries):
            if entry is None:
                print 'Warning: citekey \'%s\' not found in database.' % citekey
                continue
            f.write('%s\n\n' % entry)
        
