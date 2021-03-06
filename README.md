# PyConTextPipeline v1.2.1 (copy of internal VA VINCI repo - possibly outdated) 

Pipeline tool for pyConTextNLP (created for use on VA VINCI dev servers - current domain in KB files is antibiotics).

Author: Garrett Cole, MS 

Affiliations: University of Utah Division of Epidemilogy/University of Utah Dept. of Biomedical Informatics/U.S. Department of Veteran's Affairs (SLC HSR&D/IDEAS)

License: Apache 2.0

### Description
Pipeline tool and abstraction layer for [pyConTextNLP](https://pypi.org/project/pyConTextNLP/0.6.2.0/) (developed by the University of Utah Department of Biomedical Informatics) that adds a CLI, a misspellings finder, database input/output (pyodbc/MSSC), batching, multiprocessing, several sentence tokenizers, and optional eHOST project output. It was created to process very large document corpuses while running from a single VINCI dev server with minimal dependencies. Username/password/permissions are based on the domain and all processing is done in-memory with no intermediary files written.

## Setup/Usage

Requires a VINCI dev server with Anaconda and Python v3.6. All other dependencies are included. Python 3.6 may be required due to multiprossesing/dill changes with 3.7. I can't update until VINCI does. Clone project into a Vinci dev server, specify the "demo.bat" and "targets/modifiers.yml" files with your database and domain knowledge, and run.

It expects an input table with at least a document ID column, document text column, and row number column for batching (column names are set as arguments). See "Create_input_table.sql" in the tools folder for a corpus creation example. Also included is a post-processing SQL script to make document-level assertions (ABX y/n + affirmed name/s).

The presence of the "-roc" argument (Ratcliff/Obershelp algorithm coefficient) is what determines if the misspellings finder will be run. It only uses the "Lex:" tag of the targets.yml file. The generated "targets+misspellings.yml" file will always be used if it exists and falls back to the specified "-t targets.yml" if not. Delete or rename the targets+misspellings.yml file and run without "-roc" (or with "-roc 1") if you only want to use specified exact targets. Record scanning time is linear and total vocabulary levels out around 250k words, so the time it takes won't increase much after a certain point (~15 minutes).

"fast_executemany" improves database write time for larger batches, so I recommend you scale the batch size to the task and what would be an acceptable loss if the program was interrupted (~100-1000).

If the NLP pipeline is interrupted, remove "--clear" (to set table mode to append) and change the "-start" argument to be the last document displayed in the console/logfile plus 1. E.g set "-start 11" if log shows "Records 1 through 10 processed" before an error.

Only use the "-edir" argument (path to output directory for the created eHOST project containing NLP-generated annotations) for validation tasks of a few hundred documents. It is slower and less secure because it writes files to disk. If the "-mode" argument is set to "separate" (default), the targets will be the classes with the modifiers as attributes while "combined" will create single classes as a combined target and modifier.

### Arguments

*    -h, --help          | show this help message and exit
*    -v, --verbose       | Verbose output
*    -svr STRING         | Server name
*    -db STRING          | Database name
*    -itab STRING        | Input table name
*    -otab STRING        | Output table name
*    -c, --clear         | Clear output table or append if missing
*    -idcol STRING       | Document ID column name
*    -txtcol STRING      | Document text column name
*    -rncol STRING       | Row number column name (for batching)
*    -start INT          | Starting row number (defaults to 1)
*    -end INT            | Ending row number (default of 0 will use maximum row number)
*    -batch INT          | Batch size (defaults to 100)
*    -mode STRING        | {combined,separate} Combined: output single table column and eHOST classes as target_modifier. Separate (default): output separate table columns for targets and modifiers and eHOST classes as targets with modifers as attributes
*    -edir STRING        | Output directory for generated eHOST project, can be absolute or relative to the pyConTextPipeline directory (defaults to None)
*    -stok STRING        | {pyrush,resplit,helpers} Sentence tokenizer - pyrush (default - for splitting medical documents), resplit (for splitting lists), or helpers (modified from pyConTextNLP built-in, for more normal text/delimiters)
*    -roc FLOAT          | Add misspellings/variations of target lexical terms >=4 characters based on the corpus vocabulary (built-in Ratcliff/Obershelp algorithm). Coefficient of 1.0 (default/off) means include exact matches only and 0 means include very dissimilar matches (0.9 recommended for 1-2 character errors)
*    -tfile STRING       | pyConTextNLP targets file (defaults to ./kb/targets.yml)
*    -mfile STRING       | pyConTextNLP modifiers file (defaults to ./kb/modifiers.yml)
*    -p, --processes INT | Number of processes to spawn (defaults to number of logical CPU cores)


### Required/Included Dependencies:

*   Python 3.6
*   PyConTextNLP-0.6.2.0
      *   networkx-1.11
*   dill-0.2.9
      *   multiprocessing_on_dill-3.5.0a4
*   PyRuSH-1.0.2:
      *   PyFastNER-1.0.8.dev2
      *   intervaltree-2.1.0
           *   sortedcontainers-2.1.0

"_mod.py" files are files from dependencies modified for compatibility

"logfile" is just a copy stdout/print for now (overwiritten after each task).

## To Do:

    -Take targets and modifiers arguments as lists (E.g. "domain_modifiers.yaml, negation_modifiers.yaml")
    -cleanup/pylint
    -write setup.py install script for non-VA environments with internet access
    -allow to be imported by external script (initialize function)
    -docstrings, comments, documentation...
    -add logging and proper verbose/silent modes
    -unit tests
    -allow table joining on input
