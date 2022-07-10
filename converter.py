import xml.etree.ElementTree as ET
import representation as MR
import csv

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


def write_mr_to_csv(initial_mr_analysis, gen_mrs_analyses, ga_params, field_data, constants, output_file_name=None):
    if output_file_name is None:
        output_file_name = "output/evaluation.csv"

    with open(output_file_name, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)

        for p in ga_params:
            csv_writer.writerow(p)
        # statement, sum_tp, sum_tn, score, scores_list
        header_row = ['LPLV', 'LPOP', 'LPRV', 'RPLV', 'RPOP', 'RPRV', 'sum_tp', 'sum_tn', 'Score']
        for k, v in (initial_mr_analysis[4]).items():
            header_row.append(k + '-tp')
            header_row.append(k + '-tn')
            header_row.append(k + '-score')

        csv_writer.writerow(header_row)
        ret = convert_statement_with_header(initial_mr_analysis[0], field_data, constants)
        ret.append(initial_mr_analysis[1])
        ret.append(initial_mr_analysis[2])
        ret.append(initial_mr_analysis[3])
        for k, v in (initial_mr_analysis[4]).items():
            ret.append(v[0])
            ret.append(v[1])
            ret.append(v[2])
        csv_writer.writerow(ret)

        csv_writer.writerow(header_row)

        for m in gen_mrs_analyses:
            ret = convert_statement_with_header(m[0], field_data, constants)
            ret.append(m[1])
            ret.append(m[2])
            ret.append(m[3])
            for k, v in (m[4]).items():
                ret.append(v[0])
                ret.append(v[1])
                ret.append(v[2])
            csv_writer.writerow(ret)


def convert_statement_with_header(statement, field_data, constants):
    statement = convert_time(statement)
    retval = []
    if statement.p_left.v_left.type == MR.VAL_TYPE_CONS:
        retval.append(list(constants)[statement.p_left.v_left.index])
    else:
        retval.append(list(field_data)[statement.p_left.v_left.index] + ' t+' + str(statement.p_left.v_left.time))

    retval.append(statement.p_left.op)

    if statement.p_left.v_right.type == MR.VAL_TYPE_CONS:
        retval.append(list(constants)[statement.p_left.v_right.index])
    else:
        retval.append(list(field_data)[statement.p_left.v_right.index] + ' t+' + str(statement.p_left.v_right.time))

    if statement.p_right.v_left.type == MR.VAL_TYPE_CONS:
        retval.append(list(constants)[statement.p_right.v_left.index])
    else:
        retval.append(list(field_data)[statement.p_right.v_left.index] + ' t+' + str(statement.p_right.v_left.time))

    retval.append(statement.p_right.op)

    if statement.p_right.v_right.type == MR.VAL_TYPE_CONS:
        retval.append(list(constants)[statement.p_right.v_right.index])
    else:
        retval.append(list(field_data)[statement.p_right.v_right.index] + ' t+' + str(statement.p_right.v_right.time))

    return retval


def convert_time(statement):
    list_time = []
    if statement.p_left.v_left.type == MR.VAL_TYPE_VAR:
        list_time.append(statement.p_left.v_left.time)
    if statement.p_left.v_right.type == MR.VAL_TYPE_VAR:
        list_time.append(statement.p_left.v_right.time)
    if statement.p_right.v_left.type == MR.VAL_TYPE_VAR:
        list_time.append(statement.p_right.v_left.time)
    if statement.p_right.v_right.type == MR.VAL_TYPE_VAR:
        list_time.append(statement.p_right.v_right.time)

    min_time = 0
    if len(list_time) != 0:
        min_time = min(list_time)
    if statement.p_left.v_left.type == MR.VAL_TYPE_VAR:
        statement.p_left.v_left.time -= min_time
    if statement.p_left.v_right.type == MR.VAL_TYPE_VAR:
        statement.p_left.v_right.time -= min_time
    if statement.p_right.v_left.type == MR.VAL_TYPE_VAR:
        statement.p_right.v_left.time -= min_time
    if statement.p_right.v_right.type == MR.VAL_TYPE_VAR:
        statement.p_right.v_right.time -= min_time
    return statement
