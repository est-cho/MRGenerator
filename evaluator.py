import representation as MR
import data_parser

MAX_TIME_RANGE = 50  # 1 tick ~ 50ms, 50 ticks ~ 2.5sec, 100 ticks ~ 5sec

PENALTY_TIME = 0.9
PENALTY_COUPLING = 0.1


def evaluate_population(population, field_data, constants, penalty_cohesion):
    pop_fit = []
    for p in population:
        (tp, tn, fp, fn, score) = calculate_score(p, field_data, constants, penalty_cohesion)
        pop_fit.append((p, tp, tn, fp, fn, score))
    return pop_fit


def calculate_score(statement, field_data, constants, penalty_cohesion):
    time_len = []
    field_data_len = len(list(field_data.values())[0])

    if statement.p_left.v_left.type == MR.VAL_TYPE_VAR:
        lp_lv = list(field_data.values())[statement.p_left.v_left.index]
        lp_lv_t = statement.p_left.v_left.time
        time_len.append(lp_lv_t)
    else:
        lp_lv = [list(constants.values())[statement.p_left.v_left.index]] * field_data_len
        lp_lv_t = 0

    if statement.p_left.v_right.type == MR.VAL_TYPE_VAR:
        lp_rv = list(field_data.values())[statement.p_left.v_right.index]
        lp_rv_t = statement.p_left.v_right.time
        time_len.append(lp_rv_t)
    else:
        lp_rv = [list(constants.values())[statement.p_left.v_right.index]] * field_data_len
        lp_rv_t = 0

    if statement.p_right.v_left.type == MR.VAL_TYPE_VAR:
        rp_lv = list(field_data.values())[statement.p_right.v_left.index]
        rp_lv_t = statement.p_right.v_left.time
        time_len.append(rp_lv_t)
    else:
        rp_lv = [list(constants.values())[statement.p_right.v_left.index]] * field_data_len
        rp_lv_t = 0

    if statement.p_right.v_right.type == MR.VAL_TYPE_VAR:
        rp_rv = list(field_data.values())[statement.p_right.v_right.index]
        rp_rv_t = statement.p_right.v_right.time
        time_len.append(rp_rv_t)
    else:
        rp_rv = [list(constants.values())[statement.p_right.v_right.index]] * field_data_len
        rp_rv_t = 0

    data_len = [len(lp_lv), len(lp_rv), len(rp_lv), len(rp_rv)]

    min_time = 0
    if len(time_len) != 0:
        min_time = min(time_len)

    max_time = 0
    if lp_lv_t != 0:
        lp_lv_t -= min_time
        max_time = max(max_time, lp_lv_t)
    if lp_rv_t != 0:
        lp_rv_t -= min_time
        max_time = max(max_time, lp_rv_t)
    if rp_lv_t != 0:
        rp_lv_t -= min_time
        max_time = max(max_time, rp_lv_t)
    if rp_rv_t != 0:
        rp_rv_t -= min_time
        max_time = max(max_time, rp_rv_t)
    min_len = min(data_len) - max_time

    tp = 0
    tn = 0
    fp = 0
    fn = 0
    for i in range(min_len):
        first_left = lp_lv[i + lp_lv_t]
        first_right = lp_rv[i + lp_rv_t]
        first = MR.OPERATOR_DICT[statement.p_left.op](first_left, first_right)
        second_left = rp_lv[i + rp_lv_t]
        second_right = rp_rv[i + rp_rv_t]
        second = MR.OPERATOR_DICT[statement.p_right.op](second_left, second_right)
        if first and second:
            tp += 1
        elif first and not second:
            tn += 1
        elif not first and second:
            fp += 1
        elif not first and not second:
            fn += 1

    if (tp + tn) == 0:
        score = 0
    else:
        score = float(tp) / float(tp + tn) * 100.0
        score = get_adjusted_score(score, statement, field_data, constants, penalty_cohesion)
        if max_time >= MAX_TIME_RANGE:
            score = score * (1 - PENALTY_TIME)
    return tp, tn, fp, fn, score


def get_adjusted_score(raw_score, statement, field_data, constants, penalty_cohesion):
    left_field_cohesion, left_sys_cohesion = check_prop_cohesion(statement.p_left, field_data, constants)
    right_field_cohesion, right_sys_cohesion = check_prop_cohesion(statement.p_right, field_data, constants)

    (is_left_field_cohesive, left_prop_id) = left_field_cohesion
    (is_right_field_cohesive, right_prop_id) = right_field_cohesion

    (is_left_sys_cohesive, left_sys_id) = left_sys_cohesion
    (is_right_sys_cohesive, right_sys_id) = right_sys_cohesion

    score = raw_score
    if not is_left_field_cohesive:
        score = score * (1 - penalty_cohesion)
    if not is_right_field_cohesive:
        score = score * (1 - penalty_cohesion)

    if not is_left_sys_cohesive:
        score = score * (1 - penalty_cohesion)
    if not is_right_sys_cohesive:
        score = score * (1 - penalty_cohesion)

    return score


def check_prop_cohesion(proposition, field_data, constants):
    (lv, rv) = get_prop_value_names(proposition, field_data, constants)

    left_field_index, left_sys_index = categorize_value(lv)
    right_field_index, right_sys_index = categorize_value(rv)

    field_cohesion = (False, 0)
    if left_field_index != -1 and left_field_index == right_field_index:
        field_cohesion = (True, left_field_index)

    sys_cohesion = (False, 0)
    if left_sys_index != -1 and left_sys_index == right_sys_index:
        sys_cohesion = (True, left_sys_index)

    return field_cohesion, sys_cohesion


def get_prop_value_names(proposition, field_data, constants):
    if proposition.v_left.type == MR.VAL_TYPE_CONS:
        lv = list(constants)[proposition.v_left.index]
    else:
        lv = list(field_data)[proposition.v_left.index]
    if proposition.v_right.type == MR.VAL_TYPE_CONS:
        rv = list(constants)[proposition.v_right.index].lower()
    else:
        rv = list(field_data)[proposition.v_right.index].lower()
    return lv, rv


def categorize_value(value):
    retval_field_index = -1
    for (i, vt) in enumerate(data_parser.VAL_FIELD_TYPE):
        if vt in value:
            retval_field_index = i

    retval_sys_index = 0

    return retval_field_index, retval_sys_index


def check_statement_value_type(statement):
    if statement.p_left.v_left.type == MR.VAL_TYPE_CONS and statement.p_left.v_right.type == MR.VAL_TYPE_CONS:
        return False
    if statement.p_right.v_left.type == MR.VAL_TYPE_CONS and statement.p_right.v_right.type == MR.VAL_TYPE_CONS:
        return False
    return True


def check_statement_duplicate(statement):
    if statement.p_left == statement.p_right:
        return False

    if statement.p_left.v_left == statement.p_right.v_right and statement.p_left.v_right == statement.p_right.v_left and statement.p_left.op != statement.p_right.op:
        return False

    if statement.p_left.v_left == statement.p_left.v_right or statement.p_right.v_left == statement.p_right.v_right:
        return False
    return True


def check_statement(statement):
    if not check_statement_value_type(statement):
        return False
    if not check_statement_duplicate(statement):
        return False
    return True
