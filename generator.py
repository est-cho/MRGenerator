import representation as MR

NUM_POP = 200
XOVER_RATE = 0.6
MUT_RATE = 0.2
BUDGET = 100
TIME_RANGE = 100  # 1 tick ~ 50ms, 50 ticks ~ 2.5sec, 100 ticks ~ 5sec


# field_data: dictionary of field data name and list of values
# constants: dictionary of constant name and value pair
def evolve(initial_mr, field_data, constants):
    penalty_cohesion = 0
    population = generate_population_from_seed(initial_mr, len(field_data), len(constants))
    population_fitness = evaluate_population(population, field_data, constants, penalty_cohesion)

    # GA

    return population_fitness[:NUM_POP]


def generate_population_from_seed(initial_mr, variable_range, constant_range):
    population = []

    lp_op = initial_mr.p_left.op
    i = MR.OPERATORS.index(lp_op)

    for j in [x for x in range(len(MR.OPERATORS)) if x != i]:
        copy_mr = initial_mr.copy()
        copy_mr.p_left.op = MR.OPERATORS[j]
        population.append(copy_mr)

    rp_op = initial_mr.p_right.op
    i = MR.OPERATORS.index(rp_op)

    for j in [x for x in range(len(MR.OPERATORS)) if x != i]:
        copy_mr = initial_mr.copy()
        copy_mr.p_right.op = MR.OPERATORS[j]
        population.append(copy_mr)

    v_list = [initial_mr.p_left.v_left, initial_mr.p_left.v_right, initial_mr.p_right.v_left,
              initial_mr.p_right.v_right]

    for (i, v) in enumerate(v_list):
        mut_v = []
        if v.type == MR.VAL_TYPE_VAR:
            for j in [x for x in range(variable_range) if x != v.index]:
                copy_v = v.copy()
                copy_v.index = j
                mut_v.append(copy_v)
            for j in [x for x in range(TIME_RANGE) if x != v.time]:
                copy_v = v.copy()
                copy_v.time = j
                mut_v.append(copy_v)
        else:
            for j in [x for x in range(constant_range) if x != v.index]:
                copy_v = v.copy()
                copy_v.index = j
                mut_v.append(copy_v)

        for mv in mut_v:
            copy_mr = initial_mr.copy()
            if i == 0:
                copy_mr.p_left.v_left = mv
                population.append(copy_mr)
            elif i == 1:
                copy_mr.p_left.v_right = mv
                population.append(copy_mr)
            elif i == 2:
                copy_mr.p_right.v_left = mv
                population.append(copy_mr)
            else:
                copy_mr.p_right.v_right = mv
                population.append(copy_mr)
    return population


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

    return tp, tn, fp, fn, score
