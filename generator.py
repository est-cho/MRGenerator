import representation as MR

NUM_POP = 200
XOVER_RATE = 0.6
MUT_RATE = 0.2
BUDGET = 100
TIME_RANGE = 100    # 1 tick ~ 50ms, 50 ticks ~ 2.5sec, 100 ticks ~ 5sec


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

    v_list = [initial_mr.p_left.v_left, initial_mr.p_left.v_right, initial_mr.p_right.v_left, initial_mr.p_right.v_right]

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
    return True
