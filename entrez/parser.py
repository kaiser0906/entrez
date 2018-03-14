from collections import defaultdict
import re
from xml.parsers import expat

TAG_SEQUENCE = 'TSeq_sequence'


class Parser(object):
    """
    NCBI TinySeq XML Parser. Results an output file and printing to screen.

    Attrs:
        element (str): XML tag element
        data (dict): stores xml data as k-v pair as tag-text excepts parent
            nodes as well as `TSeq_sequence`.
        pattern (str): regex pattern for searching.
        filename (str): filename(path) for the result.
        file (File): file object for storing result.
        position (int): last index of data in accumulated chunks.
        start (int): index of first sequence data matched.
        end (int): index of last sequence ata matched.
        hit (defaultdict): stores matches with counts and sorted by # in desc.
            i.e. {'AAAC': 5, 'AAAB': 3, 'AAAA': 1}
    """
    data_fields = ('accver', 'sid', 'taxid', 'orgname', 'defline', 'length',)

    def __init__(self, pattern, filename):
        self._parser = expat.ParserCreate()
        self._parser.StartElementHandler = self.start
        self._parser.EndElementHandler = self.end
        self._parser.CharacterDataHandler = self.data
        self.element = None
        self.data = {}
        self._pattern = pattern
        self.pattern = re.compile(pattern)
        self.filename = filename
        self.file = open(filename, 'wt')
        self.position = self.start = self.end = 0
        self.hit = defaultdict(int)
        self.window = ''

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def start(self, tag, attrs):
        """Tag started."""
        self.element = tag

    def end(self, tag):
        """Tag closed. Appends start and end position only for `TSeq_sequence`.
        """
        # print the hit result to screen
        if self.element == TAG_SEQUENCE:
            for k in sorted(self.hit, key=self.hit.get, reverse=True):
                print('%s\t%s' % (k, self.hit[k]))
        # Clear element when closing
        self.element = None

    def data(self, data):
        """Handles regex searches for `TSeq_sequence`. Stores other tags with
        values in `self.data`

        Using self.window for prepending left over from the previous chunk.
        min(len(pattern), last match end index) from the last will be cut and
        stored into self.window.
        i.e.
        Chunks received:    0123456789, ABCDEFG
        Data after prepend: 0123456789, 789ABCDEFG (789 is the left over)
        """
        # Store none sequence data for later use
        if self.element and self.element.split('_')[-1] in self.data_fields:
            self.data[self.element.split('_')[-1]] = data.strip()
        elif data and self.element == TAG_SEQUENCE:
            # Sequence data found
            # Run regex and get start, end, as well as matching value
            last_ended = 0
            data = self.window + data  # prepend
            for m in self.pattern.finditer(data):
                start = self.position + m.start() + 1
                end = self.position + m.end()
                last_ended = m.end()
                self.file.write('%s,%s,%s\n' % (m.group(), start, end))
                self.hit[m.group()] += 1
            # Update the last data position.
            # Next chunk's first data needs +1 because index starts 0
            self.position += len(data)
            # Set up window for matches can be broken by chunks.
            window_size = min(len(self._pattern), len(data) - last_ended)
            self.window = data[window_size * -1:] if window_size else ''
            self.position -= window_size

    def feed(self, data):
        """Parses xml data when data exists."""
        self._parser.Parse(data, 0)

    def close(self):
        """Ensure closing file object as well as xml parser."""
        self.file.close()
        self._parser.Parse("", 1)  # end of data
        del self._parser  # get rid of circular references
        # print('\n'.join(['%s: %s' % (k, v) for k, v in self.data.items()]))
