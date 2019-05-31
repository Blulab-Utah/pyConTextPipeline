#!/usr/bin/env python
# -*- coding: utf-8 -*-

r"""
RESplit takes a regular expression that matches the section of interest in the note, a primary
regular expression to capture each sentence within the section, and a secondary fall-back regular
expression for odd cases. It returns a list of named tuples for the sentence spans in the document.

The followoing works well for University of Utah GI Pathology notes:
sentence_rules = {'section_regex':r'(.*)(?:~?\d\d\/\d\d\/\d\d\s+\w{2,3}\/\w{2,3}~?\s+I\scertify\sthat\sI\spersonally\sconducted\sthe)',
                  'section_number':1,
                  'primary_regex':r'(?<=\d\.\s)(.*?)(?=~+(\d|\d-\d|\d,\s?\d)\.\s+|\n\-+\n|\Z)',
                  'fallback_regex':r'(\"?[A-Z, ]{5,}\"?[A-Z\,\ ]+\(?BIOPS(Y|IES)[A-Z, ]*?\)?:\s?~~-\s.*?)(?:\n\-+\n|\Z)',
                  'verbose':verbose}
"""

__version__ = "1.1.0"
__author__ = "Garrett Cole"
__email__ = "garrett.cole@hsc.utah.edu"
__license__ = "Apache 2.0"

import re
from yaml import safe_load
from collections import namedtuple

class RESplit():
    """Creates RESplit segmenter object"""
    def __init__(self, verbose, rules_str):
        """Initialize a RESplit segmenter object"""
        self.verbose = verbose
        try:
            with open(rules_str, 'r') as stream:
                rules = safe_load(stream)
        except OSError:
            rules = load(rules_str)
        self.section_regex = re.compile(rules['Section_regex'], re.S)
        self.section_number = rules['Section_number']-1 # make RE group match iter
        self.primary_regex = re.compile(rules['Primary_regex'], re.S)
        if rules['Fallback_regex']: #can be None
            self.fallback_regex = re.compile(rules['Fallback_regex'], re.S)
        else:
            self.fallback_regex = None

    def segToSentenceSpans(self, text):
        """
        Find spans of sentences based on given regex rules

        Args:
            document: Text to segment

        Returns:
            List of named tuples representing sentence spans
            sentence.span = (sentence.begin:sentence.end)
        """
        if self.verbose:
            print("--RESplit--")
        ItemSpan = namedtuple('span', 'begin, end')
        output = list()
        sections = self.section_regex.finditer(text)

        # RE matches are not subscriptable, so iterate until correct section
        for i, section in enumerate(sections):
            if i == self.section_number:
                if self.verbose:
                    print("Trying primary regex")
                sentences = self.primary_regex.finditer(section.group(1))
                for sentence in sentences:
                    span = ItemSpan(sentence.start(1), sentence.end(1))
                    if self.verbose:
                        print(sentence.group(1), span)
                    output.append(span)
                if not output and hasattr(self,'fallback_regex'):
                    if self.verbose:
                        print("Trying fallback regex")
                    sentences = self.fallback_regex.finditer(section.group(1))
                    for sentence in sentences:
                        span = ItemSpan(sentence.start(1), sentence.end(1))
                        if self.verbose:
                            print(sentence.group(1), span)
                        output.append(span)
        if self.verbose:
            if not output:
                print("no matches found...")
            print("--tilpSER--")
        return output
