--Remove invalid routes of administration caused by errors in sentence segmenting
--'ra-oral','ra-top','ra-iv','ra-im','ra-inh','ra-vag','ra-sup','ra-eye','ra-ear'

--Invalid separate Target/Modifier (default)
DELETE FROM [DATABASE].[SCHEMA].[NLP_OUTPUT_TABLE] WHERE
([Target] = 'azithromycin' AND [Modifier] in (					          'ra-top',        'ra-im','ra-inh','ra-vag','ra-sup',         'ra-ear')) OR
([Target] in ('amoxicillin','amoxicillin/clavulanate') AND [Modifier] in ('ra-top',        'ra-im','ra-inh','ra-vag','ra-sup','ra-eye','ra-ear')) OR
([Target] in ('penicillin','penicillin-v') AND [Modifier] in (  		  'ra-top',        'ra-im','ra-inh','ra-vag','ra-sup','ra-eye','ra-ear')) OR
([Target] = 'levofloxacin' AND [Modifier] in (      					  'ra-top',        'ra-im','ra-inh','ra-vag','ra-sup',         'ra-ear')) OR
([Target] = 'moxifloxacin' AND [Modifier] in (                            'ra-top',        'ra-im','ra-inh','ra-vag','ra-sup',         'ra-ear')) OR
([Target] = 'doxycycline' AND [Modifier] in (                             'ra-top',        'ra-im','ra-inh','ra-vag','ra-sup','ra-eye','ra-ear')) OR
([Target] = 'erythromycin' AND [Modifier] in (                                                     'ra-inh','ra-vag','ra-sup',         'ra-ear')) OR
([Target] = 'azithromycin' AND [Modifier] in (                            'ra-top',        'ra-im','ra-inh','ra-vag','ra-sup',         'ra-ear')) OR
([Target] = 'clindamycin' AND [Modifier] in (                                              'ra-im','ra-inh',         'ra-sup','ra-eye','ra-ear')) OR
([Target] = 'clarithromycin' AND [Modifier] in (                          'ra-top',        'ra-im','ra-inh','ra-vag','ra-sup','ra-eye','ra-ear')) OR
([Target] = 'linezolid' AND [Modifier] in (                               'ra-top',        'ra-im','ra-inh','ra-vag','ra-sup','ra-eye','ra-ear')) OR
([Target] = 'metronidazole' AND [Modifier] in (                                            'ra-im','ra-inh',                  'ra-eye','ra-ear')) OR
([Target] = 'tetracycline' AND [Modifier] in (                            'ra-top','ra-iv','ra-im','ra-inh','ra-vag','ra-sup','ra-eye','ra-ear')) OR
([Target] = 'minocycline' AND [Modifier] in (                                              'ra-im','ra-inh','ra-vag','ra-sup','ra-eye','ra-ear')) OR
([Target] = 'gatifloxacin' AND [Modifier] in (                            'ra-top',        'ra-im','ra-inh','ra-vag','ra-sup',         'ra-ear')) OR
([Target] = 'ciprofloxacin' AND [Modifier] in (                                            'ra-im','ra-inh','ra-vag','ra-sup'                  )) OR
([Target] = 'sulfamethoxazole/trimethoprim' AND [Modifier] in (           'ra-top',        'ra-im','ra-inh','ra-vag','ra-sup','ra-eye','ra-ear')) OR
([Target] = 'cefpodoxime' AND [Modifier] in (                             'ra-top','ra-iv','ra-im','ra-inh','ra-vag','ra-sup','ra-eye','ra-ear')) OR
([Target] = 'cefprozil' AND [Modifier] in (                               'ra-top','ra-iv','ra-im','ra-inh','ra-vag','ra-sup','ra-eye','ra-ear')) OR
([Target] = 'ceftazidime' AND [Modifier] in (                   'ra-oral','ra-top',                         'ra-vag','ra-sup','ra-eye','ra-ear')) OR
([Target] = 'cephalexin' AND [Modifier] in (                              'ra-top','ra-iv','ra-im','ra-inh','ra-vag','ra-sup','ra-eye','ra-ear')) OR
([Target] = 'cefuroxime' AND [Modifier] in (                              'ra-top',                'ra-inh','ra-vag','ra-sup','ra-eye','ra-ear'))
;

--Invalid combined Target/Modifier Class
DELETE FROM [DATABASE].[SCHEMA].[NLP_OUTPUT_TABLE] WHERE
([Class] in (                      'azithromycin_ra-top',                     'azithromycin_ra-im',           'azithromycin_ra-inh',           'azithromycin_ra-vag',           'azithromycin_ra-sup',                                            'azithromycin_ra-ear')) OR
([Class] in (                      'amoxicillin_ra-top',                      'amoxicillin_ra-im',            'amoxicillin_ra-inh',            'amoxicillin_ra-vag',            'amoxicillin_ra-sup',            'amoxicillin_ra-eye',            'amoxicillin_ra-ear')) OR
([Class] in (                      'amoxicillin/clavulanate_ra-top',          'amoxicillin/clavulanate_ra-im','amoxicillin/clavulanate_ra-inh','amoxicillin/clavulanate_ra-vag','amoxicillin/clavulanate_ra-sup','amoxicillin/clavulanate_ra-eye','amoxicillin/clavulanate_ra-ear')) OR
([Class] in (                      'penicillin_ra-top',                       'penicillin_ra-im',             'penicillin_ra-inh',             'penicillin_ra-vag',             'penicillin_ra-sup',             'penicillin_ra-eye',             'penicillin_ra-ear')) OR
([Class] in (                      'penicillin-v_ra-top',                     'penicillin-v_ra-im',           'penicillin-v_ra-inh',           'penicillin-v_ra-vag',           'penicillin-v_ra-sup',           'penicillin-v_ra-eye',           'penicillin-v_ra-ear')) OR
([Class] in (                      'levofloxacin_ra-top',                     'levofloxacin_ra-im',           'levofloxacin_ra-inh',           'levofloxacin_ra-vag',           'levofloxacin_ra-sup',                                            'levofloxacin_ra-ear')) OR
([Class] in (                      'moxifloxacin_ra-top',                     'moxifloxacin_ra-im',           'moxifloxacin_ra-inh',           'moxifloxacin_ra-vag',           'moxifloxacin_ra-sup',                                            'moxifloxacin_ra-ear')) OR
([Class] in (                      'doxycycline_ra-top',                      'doxycycline_ra-im',            'doxycycline_ra-inh',            'doxycycline_ra-vag',            'doxycycline_ra-sup',            'doxycycline_ra-eye',            'doxycycline_ra-ear')) OR
([Class] in (                                                                                                 'erythromycin_ra-inh',           'erythromycin_ra-vag',           'erythromycin_ra-sup',                                            'erythromycin_ra-ear')) OR
([Class] in (                      'azithromycin_ra-top',                     'azithromycin_ra-im',           'azithromycin_ra-inh',           'azithromycin_ra-vag',           'azithromycin_ra-sup',                                            'azithromycin_ra-ear')) OR
([Class] in (                                                                 'clindamycin_ra-im',            'clindamycin_ra-inh',                                             'clindamycin_ra-sup',            'clindamycin_ra-eye',            'clindamycin_ra-ear')) OR
([Class] in (                      'clarithromycin_ra-top',                   'clarithromycin_ra-im',         'clarithromycin_ra-inh',         'clarithromycin_ra-vag',         'clarithromycin_ra-sup',         'clarithromycin_ra-eye',         'clarithromycin_ra-ear')) OR
([Class] in (                      'linezolid_ra-top',                        'linezolid_ra-im',              'linezolid_ra-inh',              'linezolid_ra-vag',              'linezolid_ra-sup',              'linezolid_ra-eye',              'linezolid_ra-ear')) OR
([Class] in (                                                                 'metronidazole_ra-im',          'metronidazole_ra-inh',                                                                            'metronidazole_ra-eye',          'metronidazole_ra-ear')) OR
([Class] in (                      'tetracycline_ra-top','tetracycline_ra-iv','tetracycline_ra-im',           'tetracycline_ra-inh',           'tetracycline_ra-vag',           'tetracycline_ra-sup',           'tetracycline_ra-eye',           'tetracycline_ra-ear')) OR
([Class] in (                                                                 'minocycline_ra-im',            'minocycline_ra-inh',            'minocycline_ra-vag',            'minocycline_ra-sup',            'minocycline_ra-eye',            'minocycline_ra-ear')) OR
([Class] in (                      'gatifloxacin_ra-top',                     'gatifloxacin_ra-im',           'gatifloxacin_ra-inh',           'gatifloxacin_ra-vag',           'gatifloxacin_ra-sup',                                            'gatifloxacin_ra-ear')) OR
([Class] in (                                                                 'ciprofloxacin_ra-im',          'ciprofloxacin_ra-inh',          'ciprofloxacin_ra-vag',          'ciprofloxacin_ra-sup')) OR
([Class] in (                      'cefpodoxime_ra-top', 'cefpodoxime_ra-iv', 'cefpodoxime_ra-im',            'cefpodoxime_ra-inh',            'cefpodoxime_ra-vag',            'cefpodoxime_ra-sup',            'cefpodoxime_ra-eye',            'cefpodoxime_ra-ear')) OR
([Class] in (                      'cefprozil_ra-top',   'cefprozil_ra-iv',   'cefprozil_ra-im',              'cefprozil_ra-inh',              'cefprozil_ra-vag',              'cefprozil_ra-sup',              'cefprozil_ra-eye',              'cefprozil_ra-ear')) OR
([Class] in ('ceftazidime_ra-oral','ceftazidime_ra-top',                                                                                       'ceftazidime_ra-vag',            'ceftazidime_ra-sup',            'ceftazidime_ra-eye',            'ceftazidime_ra-ear')) OR
([Class] in (                      'cephalexin_ra-top',  'cephalexin_ra-iv',  'cephalexin_ra-im',             'cephalexin_ra-inh',             'cephalexin_ra-vag',             'cephalexin_ra-sup',             'cephalexin_ra-eye',             'cephalexin_ra-ear')) OR
([Class] in (                      'cefuroxime_ra-top',                                                       'cefuroxime_ra-inh',             'cefuroxime_ra-vag',             'cefuroxime_ra-sup',             'cefuroxime_ra-eye',             'cefuroxime_ra-ear')) OR
([Class] in (                      'sulfamethoxazole/trimethoprim_ra-top','sulfamethoxazole/trimethoprim_ra-im','sulfamethoxazole/trimethoprim_ra-inh','sulfamethoxazole/trimethoprim_ra-vag','sulfamethoxazole/trimethoprim_ra-sup','sulfamethoxazole/trimethoprim_ra-eye','sulfamethoxazole/trimethoprim_ra-ear'))
;
