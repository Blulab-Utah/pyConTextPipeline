#!/usr/bin/python3
"""
PyConTextPipeline v1.2.1
garrett.cole@hsc.utah.edu/garrett.cole@va.gov
Apache 2.0
"""

import argparse, re, pipeUtils, pyodbc, sys
from os import path, makedirs, getpid
from shutil import copyfile
import eHOSTTools as eht
from multiprocessing_on_dill import Pool, cpu_count
from timeit import default_timer
from yaml import safe_load_all, dump, add_representer
from difflib import SequenceMatcher
from functools import partial
from collections import OrderedDict

class Tee(object):
    """
    stdout to console and log file
    https://stackoverflow.com/a/17866768
    """
    def __init__(self, *files):
        self.files = files
    def write(self, obj):
        for f in self.files:
            f.write(obj)
    def flush(self):
        pass

class pyConTextPipeline(object):
    """"""
    def __init__(self):
        self.verbose = args.verbose
        # sanitize non-parameterizable SQL elements
        self.svr = re.sub(r'[^A-Za-z0-9_]', '', args.svr)
        self.db = re.sub(r'[^A-Za-z0-9_]', '', args.db)
        self.itab = re.sub(r'[^A-Za-z0-9_\.]', '', args.itab)
        self.otab = re.sub(r'[^A-Za-z0-9_\.]', '', args.otab)
        if self.otab == self.itab:
            raise Exception("Output table cannot be input table")
        self.clear = args.clear
        self.edir = path.abspath(args.edir) if args.edir else None
        self.mode = args.mode
        self.idcol = re.sub(r'[^A-Za-z0-9_]', '', args.idcol)
        self.txtcol = re.sub(r'[^A-Za-z0-9_]', '', args.txtcol)
        self.rncol = re.sub(r'[^A-Za-z0-9_]', '', args.rncol)
        self.start = int(args.start)
        if self.start < 1:
            self.start = 0
        self.end = int(args.end)
        if self.end < self.start and not self.end < 1:
            raise ValueError("Ending row cannot be less than starting row.")
        self.batch = int(args.batch)
        if self.batch < 1:
            raise ValueError("Batch size must be positive.")
        self.stok = args.stok
        self.mfile = args.mfile
        self.tfile = args.tfile
        self._tmfile = path.splitext(self.tfile)[0]+'+misspellings'+path.splitext(self.tfile)[1]
        self.roc = float(args.roc)
        if args.roc < 0.0 or args.roc > 1.0:
            raise ValueError("Ratcliff/Obershelp coefficient must be between 0 and 1.")
        self.processes = int(args.processes)
        if self.end < 1:
            self.end = self._table_maxrn()

    def _represent_ordered_dicts(self):
        """
        Allow OrderedDicts to be dumped into YAML
        https://stackoverflow.com/a/8661021
        """
        represent_dict_order = lambda self, data: self.represent_mapping('tag:yaml.org,2002:map', data.items())
        add_representer(OrderedDict, represent_dict_order)

    def _table_maxrn(self):
        """
        Return maximum rncol from input table
        """
        conn = pyodbc.connect('Driver={SQL Server Native Client 11.0};Server='+self.svr+';Database='+self.db+';Trusted_Connection=yes;')
        max_rn = conn.execute('''SELECT max({rncol}) as maxrn FROM {itab} WITH (NOLOCK)'''.format(rncol=self.rncol, itab=self.itab)).fetchone().maxrn
        conn.close()
        return max_rn

    def _db_creator(self):
        conn = pyodbc.connect('Driver={SQL Server Native Client 11.0};Server='+self.svr+';Database='+self.db+';Trusted_Connection=yes;autocommit=False;')
        cursor = conn.cursor()
        try:
            if self.mode == 'combined':
                cursor.execute('''CREATE TABLE {otab} ({idcol} bigint, Snippet varchar(8000), Span_Start int, Span_End int, Class varchar(64), Target_Code varchar(32))'''.format(otab=self.otab, idcol=self.idcol))
            elif self.mode == 'separate':
                cursor.execute('''CREATE TABLE {otab} ({idcol} bigint, Snippet varchar(8000), Span_Start int, Span_End int, Target varchar(32), Modifier varchar(32), Target_Code varchar(32))'''.format(otab=self.otab, idcol=self.idcol))
            conn.commit()
            if self.verbose:
                print("Created table", self.otab)
        except pyodbc.ProgrammingError:
            if self.verbose:
                print("Table exists")
        if self.clear:
            cursor.execute('''TRUNCATE TABLE {otab}'''.format(otab=self.otab)) # deletes all records in the table, will error if mode was changed
            conn.commit()
            if self.verbose:
                print("Table cleared")
        else:
            if self.verbose:
                print("Appending to table")
        conn.close()

    def _db_reader(self, rowstart, rowend):
        """"""
        conn = pyodbc.connect('Driver={SQL Server Native Client 11.0};Server='+self.svr+';Database='+self.db+';Trusted_Connection=yes;')
        cursor = conn.cursor()
        cursor.execute('''SELECT {idcol}, {txtcol} FROM {itab} WITH (NOLOCK) WHERE {rncol} >= ? AND {rncol} <= ?'''.format(idcol=self.idcol, txtcol=self.txtcol, itab=self.itab, rncol=self.rncol), rowstart, rowend)
        fetched_records = cursor.fetchall()
        conn.close()
        return fetched_records

    def _db_writer(self, batch_results):
        """"""
        batch_results_list = list()
        for doc in batch_results:
            for annot in doc:
                batch_results_list.append((annot[0],annot[1],annot[2],annot[3],annot[4],annot[5],annot[6]))
        conn = pyodbc.connect('Driver={SQL Server Native Client 11.0};Server='+self.svr+';Database='+self.db+';Trusted_Connection=yes;autocommit=False;')
        cursor = conn.cursor()
        cursor.fast_executemany = True # pyodbc has problems with fast_executemany if there are varchar(max)s or empty values. Comment out this line if there are issues (possible performance hit).
        if self.mode == 'combined':
            cursor.executemany('''INSERT INTO {otab} ({idcol}, Snippet, Span_Start, Span_End, Class, Target_Code) VALUES (?,?,?,?,?,?)'''.format(otab=self.otab, idcol=self.idcol), batch_results_list)
        elif self.mode == 'separate':
            cursor.executemany('''INSERT INTO {otab} ({idcol}, Snippet, Span_Start, Span_End, Target, Modifier, Target_Code) VALUES (?,?,?,?,?,?,?)'''.format(otab=self.otab, idcol=self.idcol), batch_results_list)
        cursor.commit()
        conn.close()

    def _gsplit(self, a, n):
        """
        Split a list into N parts of approximately equal length
        https://stackoverfow.com/a/2135920
        """
        k, m = divmod(len(a), n)
        return (a[i * k + min(i, m):(i + 1) * k + min(i + i, m)] for i in range(n))

    def _is_similar(self, vocabulary_chunk, targets):
        results = set()
        for c in targets:
            for w in vocabulary_chunk:
                if SequenceMatcher(None, c['Lex'], w).ratio() >= self.roc:
                    results.add(('Misspelling of '+c['Lex'], c['Direction'], w, c['Type'], c['Code']))
        return results

    def find_misspellings(self):
        """
        Optional misspelling finder
        """
        if self.roc != 1.0:
            print("Finding misspellings...")
            self._represent_ordered_dicts()
            with open(self.tfile, 'r') as stream:
                targets = list(safe_load_all(stream))
            vocabulary = set()
            batch_start = self.start
            while(True):
                batch_end = batch_start+self.batch-1
                if batch_end > self.end:
                    batch_end = self.end
                for doc in self._db_reader(batch_start, batch_end):
                    if doc[1]:
                        vocabulary.update([word.lower() for word in re.split(r'-(?!\w)|(?<!\w)-|[^\w-]', doc[1]) if len(word) >= 4])
                print("Scanned records "+str(batch_start)+" through "+str(batch_end))
                batch_start+=self.batch
                if batch_start > self.end:
                    break
            print("Vocabulary:", len(vocabulary), "words >= 4 chars")
            print("Targets:", len(targets), "terms (Lex)")
            print("Splitting vocabulary into", self.processes, "groups for multiprocessing...")
            gsplitvocab = self._gsplit(list(vocabulary), self.processes)
            print("Finding words in vocabulary similar to targets ("+str(self.roc)+")...")

            _is_similar_p = partial(self._is_similar, targets=targets)
            with Pool(self.processes) as pool2:
                similar_results = pool2.map(_is_similar_p, gsplitvocab)

            new_targets = [x for x in set.union(*similar_results) if x[2].lower() not in [t['Lex'].lower() for t in targets]]
            if len(new_targets) > 0:
                for new_target in new_targets:
                    print("*"+new_target[0]+":",new_target[2],"("+new_target[3]+")")
                print("New similar terms: ", len(new_targets))
                print("Writing to", self._tmfile+'...')
                copyfile(self.tfile, self._tmfile)
                with open(self._tmfile, 'a') as out:
                    for new_target in new_targets:
                        out.write('---\n')
                        dump(OrderedDict([('Comments',new_target[0]), ('Direction',new_target[1]), ('Lex',new_target[2]), ('Regex',''), ('Type',new_target[3]), ('Code',new_target[4])]), default_flow_style=False, stream=out)
                print("If this list contains errors or you want to verify before execution, edit the new targets+misspellings.yml file now and continue or exit, edit it, and re-run without the \"-roc\" argument.")

    def execute(self):
        """"""
        print("Starting NLP pipeline...")
        myPipe = pipeUtils.MyPipe(self.verbose,
                                  self.mode,
                                  self.stok,
                                  self._tmfile if path.isfile(self._tmfile) else self.tfile,
                                  self.mfile)
        self._db_creator()
        if self.edir:
            print("Warning! PHI will be written to disk as an eHOST project.")
            class_set = set()
            attr_set = None
            if self.mode == 'separate':
                attr_set = set()
        # batching
        batch_start = self.start
        while(True):
            batch_end = batch_start+self.batch-1
            if batch_end > self.end:
                batch_end = self.end
            batch_records = self._db_reader(batch_start, batch_end)
            # write batch notes to disk if edir is set
            if self.edir:
                makedirs(path.join(self.edir, 'corpus'), exist_ok=True)
                for record in batch_records:
                    with(open(path.join(self.edir, 'corpus', str(record[0])+'.txt'), 'w')) as f:
                        f.write(record[1])
            with Pool(self.processes) as pool:
                batch_results = [x for x in pool.map(myPipe.process, batch_records) if x]
            if batch_results:
                self._db_writer(batch_results)
                if self.edir:
                    eht.knowtator_writer(self.mode, self.edir, batch_results)
                    class_set.update([y[3] for x in batch_results for y in x])
                    if self.mode == 'separate':
                        attr_set.update([y[4] for x in batch_results for y in x])
            batch_results.clear()
            print("Records "+str(batch_start)+" through "+str(batch_end)+" processed")
            batch_start+=self.batch
            if batch_start > self.end:
                break
        if self.edir:
            eht.create_config_file(self.mode, path.join(self.edir, 'config', 'projectschema.xml'), class_set, attr_set)
        print("done")

    def __str__(self):
        """"""
        if self.roc != 1.0 and path.isfile(self._tmfile):
            roalert = '\n    WILL OVERWRITE AND USE {}'.format(self._tmfile)
        elif self.roc != 1.0 and not path.isfile(self._tmfile):
            roalert = '\n    WILL CREATE AND USE {}'.format(self._tmfile)
        elif self.roc == 1.0 and path.isfile(self._tmfile):
            roalert = '\n    WILL USE EXISTING {}'.format(self._tmfile)
        else:
            roalert = ''
        return 'Verbose output: {}\nServer name: {}\nDatabase name: {}\nInput table name: {}\nOutput table name: {}\nClear output table: {}\nOutput Mode: {}\neHOST output directory: {}\nDocument ID column name: {}\nDocument text column name: {}\nRow number column name: {}\nStarting row number: {}\nEnding row number: {}\nBatch size: {}\nSentence tokenizer: {}\nMisspellings similarity coefficient: {}\npyConTextNLP targets file: {}{}\npyConTextNLP modifiers file: {}\nNumber of processes to spawn: {}'.format(self.verbose, self.svr, self.db, self.itab, self.otab, self.clear, self.mode, path.abspath(self.edir) if self.edir else None, self.idcol, self.txtcol, self.rncol, self.start, self.end if self.end else '0 (max RowNo)', self.batch, self.stok, '1 (off)' if self.roc == 1.0 else self.roc, self.tfile, roalert, self.mfile, self.processes)

if __name__ == "__main__":
    f = open('logfile', 'w')
    backup = sys.stdout
    sys.stdout = Tee(sys.stdout, f)

    parser = argparse.ArgumentParser(description='pyConTextPipeline: CLI and abstraction layer for pyConTextNLP')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    parser.add_argument('-svr', type=str, required=True, help='Server name')
    parser.add_argument('-db', type=str, required=True, help='Database name')
    parser.add_argument('-itab', type=str, required=True, help='Input table name')
    parser.add_argument('-otab', type=str, required=True, help='Output table name')
    parser.add_argument('-c', '--clear', action='store_true', required=False, help='Clear output table or append if missing')
    parser.add_argument('-idcol', type=str, required=True, help='Document ID SQL column name')
    parser.add_argument('-txtcol', type=str, required=True, help='Document text SQL column name')
    parser.add_argument('-rncol', type=str, required=True, help='Row number column name (for batching)')
    parser.add_argument('-start', type=int, default=1, required=False, help='Starting row number (defaults to 1)')
    parser.add_argument('-end', type=int, default=0, required=False, help='Ending row number (default of 0 will use maximum row number)')
    parser.add_argument('-batch', type=int, default=100, required=False, help='Batch size (defaults to 100)')
    parser.add_argument('-mode', type=str, choices=['combined', 'separate'], default='separate', required=False, help='Combined: output single table column and eHOST classes as target_modifier. Separate (default): output separate table columns for targets and modifiers and eHOST classes as targets with modifiers as attributes')
    parser.add_argument('-edir', type=str, default=None, required=False, help='Output directory for generated eHOST project, can be absolute or relative to the pyConTextPipeline directory (defaults to None)')
    parser.add_argument('-stok', type=str, choices=['pyrush', 'resplit', 'helpers'], default='pyrush', required=False, help='Sentence tokenizer - pyrush (default - for splitting medical documents), resplit (for splitting lists), or helpers (modified from pyConTextNLP built-in, for more normal text/delimiters)')
    parser.add_argument('-roc', type=float, default=1.0, required=False, help='Add misspellings/variations of target lexical terms >=4 characters based on the corpus (built-in Ratcliff/Obershelp algorithm). Coefficient of 1.0 (default/off) means include exact matches only and 0 means include very dissimilar matches (0.9 recommended for 1-2 character errors)')
    parser.add_argument('-tfile', type=str, default='./kb/targets.yml', required=False, help='pyConTextNLP targets file (defaults to ./kb/targets.yml)')
    parser.add_argument('-mfile', type=str, default='./kb/modifiers.yml', required=False, help='pyConTextNLP modifiers file (defaults to ./kb/modifiers.yml)')
    parser.add_argument('-p', '--processes', type=int, default=cpu_count(), required=False, help='Number of processes to spawn (defaults to number of logical CPU cores)')
    args = parser.parse_args()

    pctp = pyConTextPipeline()
    print("\nTask to be run...")
    print(pctp.__str__())
    print("Is this correct(y/n)?")
    if (input() != 'y'):#currrent logging method won't print input text until after input
        print("Exiting...")
        sys.stdout = backup
        sys.exit(0)
    else:
        if pctp.roc != 1.0:
            mf_time = default_timer()
            pctp.find_misspellings()
            hm = (divmod(default_timer()-mf_time,3600));print("--- Misspellings finder took %dh %dm %.2fs ---"%(hm[0],*divmod(hm[1],60)))
            print("Continue(y/n)?")
            if (input() != 'y'):
                print("Exiting...")
                sys.exit(0)
        start_time = default_timer()
        pctp.execute()
        hm = (divmod(default_timer()-start_time,3600));print("--- NLP pipeline took %dh %dm %.2fs ---"%(hm[0],*divmod(hm[1],60)))
        sys.stdout = backup
