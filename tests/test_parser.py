try:
    from mock import patch
    from StringIO import StringIO
except ImportError:
    from io import StringIO
    from unittest.mock import patch
import os
from unittest import TestCase

from entrez.parser import Parser

BASE_DIR = os.path.dirname(__file__)
OUTPUT_FILE = os.path.join(BASE_DIR, 'out.csv')
SAMPLE_PART_1 = os.path.join(BASE_DIR, 'assets', 'sample_part_1.xml')
SAMPLE_PART_2 = os.path.join(BASE_DIR, 'assets', 'sample_part_2.xml')
SAMPLE_FASTA = os.path.join(BASE_DIR, 'assets', 'sample_fasta.xml')
SAMPLE_OUTPUT_1 = os.path.join(BASE_DIR, 'assets', 'out_test_xml_1.csv')
SAMPLE_OUTPUT_2 = os.path.join(BASE_DIR, 'assets', 'out_test_xml_2.csv')
SAMPLE_OUTPUT_3 = os.path.join(BASE_DIR, 'assets', 'out_test_xml_3.csv')

TEST_1_RESULT = """A	27
T	24
C	19
G	10
"""
TEST_2_RESULT = """ACC	5
ATC	2
"""
TEST_3_RESULT = """AAAAAG	15
AAAAAC	10
"""


class ParserTestCase(TestCase):

    def tearDown(self):
        try:
            os.remove(OUTPUT_FILE)
        except OSError:
            pass

    @patch('sys.stdout', new_callable=StringIO)
    def test_xml_1(self, mock_out):
        """SAMPLE_PART_1 and SAMPLE_PART_2 represent feeding data in 2 chunks.
        """
        with Parser(pattern='A|T|C|G', filename=OUTPUT_FILE) as p:
            with open(SAMPLE_PART_1, 'rb') as f:
                p.feed(f.read())
            with open(SAMPLE_PART_2, 'rb') as f:
                p.feed(f.read())
        output = mock_out.getvalue()
        self.assertEqual(output, TEST_1_RESULT)
        with open(OUTPUT_FILE, 'r') as f1, open(SAMPLE_OUTPUT_1, 'r') as f2:
            f1_data = f1.read()
            f2_data = f2.read()
            self.assertEqual(f1_data, f2_data)

    @patch('sys.stdout', new_callable=StringIO)
    def test_xml_2(self, mock_out):
        with Parser(pattern='A(C|T)C', filename=OUTPUT_FILE) as p:
            with open(SAMPLE_PART_1, 'rb') as f:
                p.feed(f.read())
            with open(SAMPLE_PART_2, 'rb') as f:
                p.feed(f.read())
        output = mock_out.getvalue()
        self.assertEqual(output, TEST_2_RESULT)

    @patch('sys.stdout', new_callable=StringIO)
    def test_xml_3(self, mock_out):
        """Test with SAMPLE_FASTA file.
        """
        with Parser(pattern='AAAAA(C|G)', filename=OUTPUT_FILE) as p:
            with open(SAMPLE_FASTA, 'rb') as f:
                p.feed(f.read())
        output = mock_out.getvalue()
        self.assertEqual(output, TEST_3_RESULT)
        with open(OUTPUT_FILE, 'r') as f1, open(SAMPLE_OUTPUT_3, 'r') as f2:
            f1_data = f1.read()
            f2_data = f2.read()
            self.assertEqual(f1_data, f2_data)
