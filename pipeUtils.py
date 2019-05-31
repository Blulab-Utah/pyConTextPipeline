#!/usr/bin/python
"""docstring here"""

from PyRuSH.RuSH import RuSH
from resplit.resplit import RESplit
import helpers_mod as helpers
from pyConTextNLP import pyConTextGraph
from pyConTextNLP.utils import get_document_markups
from itemData_mod import get_item_data
from os import path
from collections import namedtuple

class MyPipe:
    def __init__(self, verbose, mode, sentence_tokenizer, target_rules, modifier_rules):
        # initiate MyPipe necessary components here
        self.verbose = verbose
        self.mode = mode
        if sentence_tokenizer.lower() == 'pyrush':
            self.sentence_tokenizer = RuSH(path.abspath(path.join('kb', 'rush_rules.tsv')))
        elif sentence_tokenizer.lower() == 'resplit':
            self.sentence_tokenizer = RESplit(self.verbose, path.abspath(path.join('kb', 'resplit_rules.yml')))
        elif sentence_tokenizer.lower() == 'helpers':
            self.sentence_tokenizer = helpers.sentenceSplitter()
        self.targets = get_item_data(target_rules)
        self.modifiers = get_item_data(modifier_rules)

    def process(self, doc):
        """
        Process a document with pyConText
        
        Args:
            document: tuple or list with document id and text to process
        
        Returns:
            doc_annots: list of tuples representing the document ID, sentence text, the span, and class
        """
        # don't try to process null notes
        if not doc[1]:
            if self.verbose:
                print("Error segmenting doc",doc[0])
            return []
        # odd notes may throw an error. Just continue rather than stopping the entire process
        try:
            sentences = self.sentence_tokenizer.segToSentenceSpans(doc[1])
        except KeyError:
            if self.verbose:
                print("Error segmenting doc",doc[0])
            return []

        #context_doc = pyConTextGraph.ConTextDocument() # ConTextDoc not needed for simple usage

        doc_annots = list()

        for sentence in sentences:
            # run sentence tokenizer on input text, return the spans
            sentence_text = doc[1][sentence.begin:sentence.end]
            # process every sentence by adding markup
            markup = pyConTextGraph.ConTextMarkup()
            markup.setRawText(sentence_text)
            markup.cleanText()
            # apply targets and modifiers
            markup.markItems(self.targets, mode="target")
            markup.markItems(self.modifiers, mode="modifier")
            # address scope of modifiers to targets, remove inactive modifiers and self-modifying relationships
            markup.pruneMarks()
            markup.applyModifiers()
            markup.pruneSelfModifyingRelationships()
            markup.dropInactiveModifiers()

            marked_targets = markup.getMarkedTargets()
            for marked_target in marked_targets:
                modifiers = markup.getModifiers(marked_target)
                if not modifiers:
                    span = (sentence.begin+marked_target.getSpan()[0],sentence.begin+marked_target.getSpan()[1])
                    if self.mode == 'combined':
                        annot = (doc[0], marked_target.getPhrase(), span[0], span[1], marked_target.getCategory()[0]+'_unspecified', marked_target.getCode())
                    elif self.mode == 'separate':
                        annot = (doc[0], marked_target.getPhrase(), span[0], span[1], marked_target.getCategory()[0], 'unspecified', marked_target.getCode())
                    if annot not in doc_annots:
                        doc_annots.append(annot)
                else:
                    for modifier in modifiers:
                        if marked_target.getSpan()[0] < modifier.getSpan()[0]:
                            span = (sentence.begin+marked_target.getSpan()[0],sentence.begin+modifier.getSpan()[1])
                        else:
                            span = (sentence.begin+modifier.getSpan()[0],sentence.begin+marked_target.getSpan()[1])
                        if self.mode == 'combined':
                            annot = (doc[0], doc[1][span[0]:span[1]], span[0], span[1], marked_target.getCategory()[0]+'_'+modifier.getCategory()[0], marked_target.getCode())
                        elif self.mode == 'separate':
                            annot = (doc[0], doc[1][span[0]:span[1]], span[0], span[1], marked_target.getCategory()[0], modifier.getCategory()[0], marked_target.getCode())
                        if annot not in doc_annots:
                            doc_annots.append(annot)

            #context_doc.addMarkup(markup)

        return doc_annots
