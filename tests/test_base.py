try:
    from mock import patch
    from StringIO import StringIO
except ImportError:
    from io import StringIO
    from unittest.mock import patch
import re
from unittest import TestCase

from entrez.base import timer


class TimerTestCase(TestCase):

    @patch('sys.stdout', new_callable=StringIO)
    def test_timer(self, mock_out):
        func = lambda: 1
        decorated = timer(func)
        res = decorated()
        output = mock_out.getvalue()
        self.assertEqual(res, 1)
        p = re.compile('Time running \[<lambda>]: {1}\d.{3}\d seconds')
        self.assertTrue(p.match(output))
