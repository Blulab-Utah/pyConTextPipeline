# Copyright  2018  Department of Biomedical Informatics, University of Utah
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from PyFastNER.FastCNER import FastCNER
from PyFastNER.IOUtils import Span
import logging
import logging.config
import os.path

BEGIN = 'stbegin'
END = 'stend'


def initLogger():
    config_file = '../conf/logging.ini'
    if not os.path.isfile(config_file):
        config_file = 'conf/logging.ini'
    if not os.path.isfile(config_file):
        config_file = 'logging.ini'
        with open(config_file, 'w') as f:
            f.write('''[loggers]
keys=root

[handlers]
keys=consoleHandler

[formatters]
keys=simpleFormatter

[logger_root]
level=WARNING
handlers=consoleHandler

[handler_consoleHandler]
class=StreamHandler
level=WARNING
formatter=simpleFormatter
args=(sys.stdout,)

[formatter_simpleFormatter]
format=%(asctime)s - %(name)s - %(levelname)s - %(message)s
datefmt=
''')
    logging.config.fileConfig(config_file)


#initLogger()


class RuSH:

    def __init__(self, rule_str, max_repeat=50):
        self.fastner = FastCNER(rule_str, max_repeat)
        self.fastner.span_compare_method = 'scorewidth'
        self.logger = logging.getLogger(__name__)
        # for old RuSh rule format (doesn't have PSEUDO and ACTUAL column), make the conversion.
        if not self.fastner.full_definition:
            self.backCompatableParseRule()
        pass

    def backCompatableParseRule(self):
        for id, rule in self.fastner.rule_store.items():
            if rule.score % 2 != 0:
                rule.type = 'PSEUDO'
        self.fastner.constructRuleMap(self.fastner.rule_store)
        pass

    def segToSentenceSpans(self, text):
        output = []
        result = self.fastner.processString(text)

        # log important message for debugging use
        if self.logger.isEnabledFor(logging.DEBUG):
            text = text.replace('\n', ' ')
            for concept_type, spans in result.items():
                self.logger.debug(concept_type)
                for span in spans:
                    rule = self.fastner.rule_store[span.rule_id]
                    self.logger.debug('\t{0}-{1}:{2}\t{3}<{4}>\t[Rule {5}:\t{6}\t{7}\t{8}\t{9}]'.format(
                        span.begin, span.end, span.score, text[:span.begin],
                        text[span.begin:span.begin + 1],
                        rule.id, rule.rule, rule.rule_name,
                        rule.score, rule.type
                    ))

        begins = result[BEGIN]
        ends = result[END]

        if begins is None or len(begins) == 0:
            begins = [Span(0, 1)]

        if ends is None or len(ends) == 0:
            ends = [Span(len(text) - 1, len(text))]

        st_begin = 0
        st_started = False
        st_end = 0
        j = 0

        for i in range(0, len(begins)):
            if not st_started:
                st_begin = begins[i].begin
                if st_begin < st_end:
                    continue
                st_started = True
            elif begins[i].begin < st_end:
                continue

            for k in range(j, len(ends)):
                if i < len(begins) - 1 and k < len(ends) - 1 and begins[i + 1].begin < ends[k].begin + 1:
                    break
                st_end = ends[k].begin + 1
                j = k
                while st_end >= 1 and (text[st_end - 1].isspace() or ord(text[st_end - 1]) == 160):
                    st_end -= 1
                if st_end < st_begin:
                    continue
                elif st_started:
                    output.append(Span(st_begin, st_end))
                    st_started = False
                    if i == len(begins) - 1 or (k < len(ends) - 1 and begins[i + 1].begin > ends[k + 1].end):
                        continue
                    break
                else:
                    output[len(output) - 1] = Span(st_begin, st_end)
                    st_started = False

        if self.logger.isEnabledFor(logging.DEBUG):
            for sentence in output:
                self.logger.debug(
                    'Sentence({0}-{1}):\t>{2}<'.format(sentence.begin, sentence.end, text[sentence.begin:sentence.end]))

        return output
