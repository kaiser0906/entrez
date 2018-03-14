Entrez
======


A python application retrieves sequence record in the GenBank databases for DNA
and protein sequences and perform a simple string-based analysis of the data.

The application accepts 4 input parameters:
1. a database name
1. a database identifier
1. a regular expression (regex) string
1. and an output file name.

The application generates a network **request to the NCBI Database**. NCBI provides
a utility called "eFetch" that enables you to easily retrieve data.
Complete information about eFetch is available at:
http://www.ncbi.nlm.nih.gov/books/NBK25499.

For example, if you specify the **nucleotide** database and an id of
**30271926**, this corresponds to the complete genome of the SARS virus and is
retrieved with the following URL:
http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=nucleotide&id=30271926&rettype=fasta&retmode=xml

If you issue the request above, you will receive a document in the NCBI TinySeq
XMLformat, which looks something like this:

    <?xml version="1.0"?>
    <!DOCTYPE TSeqSet PUBLIC "-//NCBI//NCBI TSeq/EN" "http://www.ncbi.nlm.nih.gov/dtd/NCBI_TSeq.dtd">
    <TSeqSet>
    <TSeq>
    <TSeq_seqtype value="nucleotide"/>
    <TSeq_gi>30271926</TSeq_gi>
    <TSeq_accver>NC_004718.3</TSeq_accver>
    <TSeq_sid>gnl|NCBI_GENOMES|17014</TSeq_sid>
    <TSeq_taxid>227859</TSeq_taxid>
    <TSeq_orgname>SARS coronavirus</TSeq_orgname>
    <TSeq_defline>SARS coronavirus, complete genome</TSeq_defline>
    <TSeq_length>29751</TSeq_length>
    <TSeq_sequence>ATATTAGGTTTTTACCTACCCAGGAAAAGCCAACCAACCTC…
    …TAGCTTCTTAGGAGAATGACAAAAAAAAAAAAAAAAAAAAAAAA</TSeq_sequence>
    </TSeq>
    </TSeqSet>

The application parses the XML file and extracts the sequence data between the
`<TSeq_sequence>` and `</TSeq_sequence>` tags, and then identifies all
occurrences of the regex within the retrieved sequence.

The result will be stored to (1) a newly created file with the user-supplied file
name and also be shown (2) on the screen.

1. output to file:
    1. the specific hit sequences will be written
    1. their start and end locations in CSV format
    1. with one hit per row
1. output to screen:
    1. a list of specific hit sequences along with the number of times the
    specific hit was observed—tab-delimited and sorted (greatest to least) by
    the latter.

***NOTES***:
In regards to start and end locations in this output
(a) the first character in the retrieved sequence is at position 1
(i.e., by convention biologists start counting at 1, not 0), and 
(b) both of the start and end locations of the hits are inclusive
(i.e., the start and end locations of the hit should correspond to the offset
positions of the first and last characters, respectively).


Installation
-----

For useage:

    $ pip install git+https://github.com/kaiser0906/entrez.git@version

For development:

    $ git clone git@github.com/kaiser0906/entrez.git@version
    $ pip install entrez/
    # or
    $ python entrez/setup.py install


Example stdout and output file
-----

Run your application with the following input parameters:

    usage: entrez [-h] [-d DB] [-i UID] [-r REGEX] [-f FILE]

    optional arguments:
      -h, --help            show this help message and exit
      -d DB, --db DB        NCBI sequence database with possible values nucleotide
                            or protein.
      -i UID, --uid UID     Unique identifier (UID) to retrieve from database.
      -r REGEX, --regex REGEX
                            Regular expression pattern to match.
      -f FILE, --file FILE  (optional, default: out.csv) name of CSV file to
                            receive hit data consisting of specific hit sequence,
                            start and stop.

**Sample options:**

    Database = "nucleotide"
    Unique id = 224589800
    Regex pattern = "(A|C|G|T)"
    Output filename = "out.csv"

**Sample run commands:**

    $ entrez -d nucleotide -d 30271926 -r "A|T|C|G"
    # or
    $ python /path/to/entrez.py --db=nucleotide --id=30271926 --regex=(A|C|G|T) --file=out.txt
    T	9143
    A	8481
    G	6187
    C	5940
    Total elapsed time: 0.565 sec

**Sample of output file:**

    $ head /path/to/out.csv
    A,1,1
    T,2,2
    A,3,3
    T,4,4
    T,5,5
    A,6,6
    G,7,7
    G,8,8
    T,9,9
    T,10,10


For more details, check the help messages.

    $ entrez -h


***NOTES***:
1. Be aware that sequences may be very long.  For example, the sequence of human
chromosome 1 (nucleotide database id 224589800) is just shy of 250 million
characters long(approx. 250MB in file size).
2. Regex search with arbitrary sized block match such as `+`, `^`, `$` may not
work properly due to it requires loading the entire data into memory.
Thus, need another solution for the cases.
