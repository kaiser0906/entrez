import argparse

import sys

try:
    from urlparse import urlsplit
    from urllib import unquote, urlencode
except ImportError:  # Python 3
    from urllib.parse import urlsplit, unquote, urlencode

import requests

from entrez.parser import Parser

API_ENDPOINT = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi'
DEFAULT_RETTYPE = 'fasta'
DEFAULT_RETMODE = 'xml'
DEFAULT_FILENAME = 'out.csv'
CHUNK_SIZE = 1024 ** 2 * 2  # 2MB


class EntrezAPI(object):
    """API retrieves sequence record in the GenBank databases for DNA and
    protein sequences and perform a simple string-based analysis of the data.
    """

    def __init__(self, db, uid, pattern, filename=None, **kwargs):
        """
        Args:
            db (str): name of the database
            uid (str): unique identifier of the record
            pattern (str): regex pattern for searching
            filename (str): file path of the result
            rettype (str): optional, default: fasta, type of retrieve
            retmode (str): optional, default: xml, mode of retrieve
        """
        self.db = db
        self.uid = uid
        self.pattern = pattern
        self.filename = filename or DEFAULT_FILENAME
        self.rettype = kwargs.pop('rettype', DEFAULT_RETTYPE)
        self.retmode = kwargs.pop('retmode', DEFAULT_RETMODE)

    @property
    def url(self):
        """Returns url based on the db name and uid for search.
        """
        if not getattr(self, '_url', None):
            query = (('db', self.db),
                     ('id', self.uid),
                     ('rettype', self.rettype),
                     ('retmode', self.retmode))
            self._url = '%s?%s' % (API_ENDPOINT, urlencode(query=query))
        return self._url

    def run(self):
        """Downloads data stream via the search url and
        publishes regex hit sequences to file as well as screen.
        """
        with requests.get(self.url, stream=True) as r:
            if r.status_code != requests.codes.ok:
                print('%s %s' % (r.status_code, r.reason), file=sys.stderr)
                return

            # Run when the request succeed.
            with Parser(pattern=self.pattern, filename=self.filename) as p:
                for chunk in r.iter_content(chunk_size=CHUNK_SIZE):
                    p.feed(chunk)


def main():
    """No need the use of required=True for displaying better help message.
    """
    arg_parser = argparse.ArgumentParser(add_help=True)
    arg_parser.add_argument('-d', '--db', type=str,
                            help='NCBI sequence database with possible values nucleotide or protein.')
    arg_parser.add_argument('-i', '--uid', type=str,
                            help='Unique identifier (UID) to retrieve from database.')
    arg_parser.add_argument('-r', '--regex', type=str,
                            help='Regular expression pattern to match.')
    arg_parser.add_argument('-f', '--file', type=str,
                            help='(optional, default: out.csv) name of CSV file to receive hit data consisting of specific hit sequence, start and stop.')
    args = arg_parser.parse_args()

    if not args.db or not args.uid or not args.regex:
        arg_parser.print_help()
        return
    api = EntrezAPI(db=args.db, uid=args.uid, pattern=args.regex,
                    filename=args.file)
    api.run()


if __name__ == '__main__':
    main()
