from random import randint
from os import makedirs
from os.path import dirname, join
from collections import defaultdict
import pyConText_XML_mod as xmlGenerator

HEADER = '''<?xml version="1.0" encoding="UTF-8"?>
<eHOST_Project_Configure Version="1.0">
    <Handling_Text_Database>false</Handling_Text_Database>
    <OracleFunction_Enabled>false</OracleFunction_Enabled>
    <AttributeEditor_PopUp_Enabled>false</AttributeEditor_PopUp_Enabled>
    <OracleFunction>true</OracleFunction>
    <AnnotationBuilder_Using_ExactSpan>false</AnnotationBuilder_Using_ExactSpan>
    <OracleFunction_Using_WholeWord>true</OracleFunction_Using_WholeWord>
    <GraphicAnnotationPath_Enabled>true</GraphicAnnotationPath_Enabled>
    <Diff_Indicator_Enabled>true</Diff_Indicator_Enabled>
    <Diff_Indicator_Check_CrossSpan>true</Diff_Indicator_Check_CrossSpan>
    <Diff_Indicator_Check_Overlaps>false</Diff_Indicator_Check_Overlaps>
    <StopWords_Enabled>false</StopWords_Enabled>
    <Output_VerifySuggestions>false</Output_VerifySuggestions>
    <Pre_Defined_Dictionary_DifferentWeight>false</Pre_Defined_Dictionary_DifferentWeight>
    <PreAnnotated_Dictionaries Owner="NLP_Assistant" />'''

FOOTER = '''    </classDefs>
</eHOST_Project_Configure>'''

CLASSDEF = '''        <classDef>
            <Name>{target}</Name>
            <RGB_R>{r}</RGB_R>
            <RGB_G>{g}</RGB_G>
            <RGB_B>{b}</RGB_B>
            <InHerit_Public_Attributes>true</InHerit_Public_Attributes>
        </classDef>'''

ATTRDEFHEAD = '''    <attributeDefs>
        <attributeDef>
            <Name>modifier</Name>
            <is_Linked_to_UMLS_CUICode_and_CUILabel>false</is_Linked_to_UMLS_CUICode_and_CUILabel>
            <is_Linked_to_UMLS_CUICode>false</is_Linked_to_UMLS_CUICode>
            <is_Linked_to_UMLS_CUILabel>false</is_Linked_to_UMLS_CUILabel>'''
#<attributeDefOptionDef>unspecified</attributeDefOptionDef>
ATTRDEFFOOT = '''        </attributeDef>
    </attributeDefs>
    <Relationship_Rules />
    <classDefs>'''

def _class_attr_creator(mode, class_set, attr_set):
    class_attr_str = "\n"
    if mode == "combined":
        for c in class_set:
            class_attr_str += CLASSDEF.format(target=c,r=randint(64,255),g=randint(64,255),b=randint(64,255))+'\n'
    elif mode == "separate":
        class_attr_str += ATTRDEFHEAD+'\n'
        for a in attr_set:
            class_attr_str += '            <attributeDefOptionDef>'+a+'</attributeDefOptionDef>\n'
        class_attr_str += ATTRDEFFOOT+'\n'
        for c in class_set:
            class_attr_str += CLASSDEF.format(target=c,r=randint(64,255),g=randint(64,255),b=randint(64,255))+'\n'
    return class_attr_str

def create_config_file(mode, file_path, class_set, attr_set=None):
    makedirs(dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as f:
        f.write(HEADER + _class_attr_creator(mode, class_set, attr_set) + FOOTER)

def knowtator_writer(mode, edir, batch_results):
    createdAnnots = list()
    for doc_annots in batch_results:
        ct=1
        for annot in doc_annots:
            if mode == 'combined':
                                                         # ct,    doc_id,        phrase,   span,                     class
                an = xmlGenerator.createAnnotation(mode, str(ct), str(annot[0]), annot[1], str((annot[2],annot[3])), annot[4])
            elif mode == 'separate':
                                                         # ct,    doc_id,        phrase,   span,                     Target,   Modifier
                an = xmlGenerator.createAnnotation(mode, str(ct), str(annot[0]), annot[1], str((annot[2],annot[3])), annot[4], annot[5])
            createdAnnots.append(an)
            ct+=1
        xmlGenerator.writeKnowtator(mode, createdAnnots, join(edir, 'saved'), str(annot[0]))
        createdAnnots.clear()