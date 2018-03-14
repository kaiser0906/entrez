try:
    from mock import patch
    from StringIO import StringIO
except ImportError:
    from io import StringIO
    from unittest.mock import patch
import os
from unittest import TestCase, skip

from entrez.api import EntrezAPI, API_ENDPOINT, DEFAULT_RETTYPE, \
    DEFAULT_RETMODE, CHUNK_SIZE
from entrez.base import timer
from .test_parser import TEST_3_RESULT, SAMPLE_OUTPUT_3

DB = 'nucleotide'
ID = '30271926'
PATTERN = 'AAAAA(C|G)'

BASE_DIR = os.path.dirname(__file__)
OUTPUT_FILE = os.path.join(BASE_DIR, 'out.csv')
SAMPLE_FASTA = os.path.join(BASE_DIR, 'assets', 'sample_fasta.xml')
SAMPLE_LARGE = os.path.join(BASE_DIR, 'assets', 'large_data.xml')

LARGE_OUTPUT = '''AAAAAG	210122
AAAAAC	156336
'''


class MockResponse(object):
    """Fake Response class and serves binary data file as downloading.
    """

    def __init__(self, data, status_code=200, **kwargs):
        self.data = data
        self.status_code = status_code
        self.reason = kwargs.pop('reason', 'OK')
        self.content_path = kwargs.pop('content_path', None)

    def iter_content(self, chunk_size=CHUNK_SIZE):
        if not self.content_path:
            yield
        with open(self.content_path, 'rb') as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                yield chunk


def mocked_requests_get(*args, **kwargs):
    if args[0] == EntrezAPITestCase.get_url():
        return MockResponse(None, content_path=SAMPLE_FASTA)
    elif args[0] == SAMPLE_LARGE:
        return MockResponse(None, content_path=SAMPLE_LARGE)
    return MockResponse(None, 404, reason='Not Found')


class EntrezAPITestCase(TestCase):

    def setUp(self):
        self.api = EntrezAPI(db=DB, uid=ID, pattern=PATTERN,
                             filename=OUTPUT_FILE)

    def tearDown(self):
        try:
            os.remove(OUTPUT_FILE)
        except OSError:
            pass

    @staticmethod
    def get_url(db=None, uid=None):
        params = 'db=%s&id=%s&rettype=%s&retmode=%s'
        params = params % (db or DB, uid or ID, DEFAULT_RETTYPE, DEFAULT_RETMODE)
        return '%s?%s' % (API_ENDPOINT, params)

    def test_url(self):
        self.assertEqual(self.api.url, self.get_url())

    def test_url_encoding(self):
        self.api.db = '~mydb'
        self.assertEqual(self.api.url, self.get_url(db='%7Emydb'))

    @patch('sys.stdout', new_callable=StringIO)
    @patch('requests.get', side_effect=mocked_requests_get)
    def test_page_not_found(self, mock_get, mock_out):
        self.api._url = 'http://google.com/foo'
        self.api.run()
        output = mock_out.getvalue()
        self.assertEqual(output, '404 Not Found\n')

    @patch('sys.stdout', new_callable=StringIO)
    @patch('requests.get', side_effect=mocked_requests_get)
    def test_run(self, mock_get, mock_out):
        self.api.run()
        output = mock_out.getvalue()
        self.assertEqual(output, TEST_3_RESULT)
        with open(OUTPUT_FILE, 'r') as f1, open(SAMPLE_OUTPUT_3, 'r') as f2:
            f1_data = f1.read()
            f2_data = f2.read()
            self.assertEqual(f1_data, f2_data)

    @skip("only for local tests with a large file")
    @timer
    @patch('sys.stdout', new_callable=StringIO)
    @patch('requests.get', side_effect=mocked_requests_get)
    def test_run_large(self, mock_get, mock_out):
        self.api._url = SAMPLE_LARGE
        self.api.run()
        output = mock_out.getvalue()
        self.assertEqual(output, LARGE_OUTPUT)
