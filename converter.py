import xml.etree.ElementTree as ET
import representation as MR

TAG_BODY = 'body'
TAG_INPUT = 'input'
TAG_STATEMENT = 'statement'
TAG_PROP = 'prop'
TAG_VALUE = 'value'
TAG_TYPE = 'type'
TAG_INDEX = 'index'
TAG_TIME = 'time'
TAG_OP = 'op'

ATTRIB_NAME = 'name'
ATTRIB_LEFT = 'left'
ATTRIB_RIGHT = 'right'

VAL_TYPE_VAR = 'v'
VAL_TYPE_CONS = 'c'


def parse_mr_xml(file_name):
    root = ET.parse(file_name).getroot()

    s_list = []
    for s in root.findall('statement'):  # Find all statements
        index = int(s.attrib[ATTRIB_NAME].split('_')[1])
        lp = MR.Prop()
        rp = MR.Prop()
        for p in s.findall(TAG_PROP):  # Find all propositions
            lv = MR.Value()
            rv = MR.Value()
            for pf in p.findall(TAG_VALUE):  # Find left and right values in the proposition
                if pf.attrib[ATTRIB_NAME] == ATTRIB_LEFT:
                    if pf.find(TAG_TIME) is None:
                        lv = MR.Value(pf.find(TAG_TYPE).text, int(pf.find(TAG_INDEX).text))
                    else:
                        lv = MR.Value(pf.find(TAG_TYPE).text, int(pf.find(TAG_INDEX).text),
                                      int(pf.find(TAG_TIME).text))
                else:
                    if pf.find(TAG_TIME) is None:
                        rv = MR.Value(pf.find(TAG_TYPE).text, int(pf.find(TAG_INDEX).text))
                    else:
                        rv = MR.Value(pf.find(TAG_TYPE).text, int(pf.find(TAG_INDEX).text),
                                      int(pf.find(TAG_TIME).text))
            op = p.find(TAG_OP).text

            if p.attrib[ATTRIB_NAME] == ATTRIB_LEFT:
                lp = MR.Prop(lv, op, rv)
            else:
                rp = MR.Prop(lv, op, rv)

        statement = MR.Statement(index, lp, rp)
        s_list.append(statement)

    return s_list


def write_mr_to_csv(generated_mr, output_file_name=""):
    return True
