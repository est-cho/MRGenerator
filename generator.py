import converter
import representation as MR
import evaluator
import random

NUM_POP = 200
XOVER_RATE = 0.6
XOVER_PROP_RATE = 1.0
MUT_RATE = 0.2
MUT_PROP_RATE = 1.0
BUDGET = 10


def get_ga_params():
    params = [['Population Size', str(NUM_POP)],
              ['Crossover Rate', str(XOVER_RATE)],
              ['Proposition Crossover Rate', str(XOVER_PROP_RATE)],
              ['Mutation Rate', str(MUT_RATE)],
              ['Proposition Mutation Rate', str(MUT_PROP_RATE)],
              ['Budget', str(BUDGET)]]
    return params


# field_data: dictionary of field data name and list of values
# constants: dictionary of constant name and value pair
def evolve(initial_mr, field_data, constants):
    penalty_cohesion = 0
    population = generate_population_from_seed(initial_mr, len(field_data), len(constants), len(list(field_data.values())[0]))
    population_fitness = evaluator.evaluate_population(population, field_data, constants, penalty_cohesion)
    population_fitness = sorted(population_fitness, key=lambda x: (x[5], x[1]), reverse=True)

    idx = 0
    while idx < BUDGET:
        print('.', end='')
        idx += 1
        parent_fitness = population_fitness[:NUM_POP]
        parents = [pf[0] for pf in parent_fitness]

        p_len = len(parents)
        p_half = int(p_len / 2)
        offspring = []

        for i in range(p_len):
            if i >= p_half:
                break
            copy_s1 = parents[i].copy()
            copy_s2 = parents[i + p_half].copy()
            (o1, o2) = crossover(copy_s1, copy_s2, XOVER_RATE)
            o1 = mutate(o1, MUT_RATE, len(field_data), len(constants), len(list(field_data.values())[0]))
            o2 = mutate(o2, MUT_RATE, len(field_data), len(constants), len(list(field_data.values())[0]))

            o1 = converter.convert_time(o1)
            o2 = converter.convert_time(o2)

            if evaluator.check_statement(o1) and not o1 in parents and not o1 in offspring:
                offspring.append(o1)

            if evaluator.check_statement(o2) and not o2 in parents and not o2 in offspring:
                offspring.append(o2)

        population = parents + offspring
        population_fitness = evaluator.evaluate_population(population, field_data, constants, penalty_cohesion)
        population_fitness = sorted(population_fitness, key=lambda x: (x[5], x[1]), reverse=True)
        penalty_cohesion += float(1 / BUDGET)

    return population_fitness[:NUM_POP]


def generate_population_from_seed(initial_mr, num_var_types, num_const_types, time_range):
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
            for j in [x for x in range(num_var_types) if x != v.index]:
                copy_v = v.copy()
                copy_v.index = j
                mut_v.append(copy_v)
            for j in [x for x in range(time_range) if x != v.time]:
                copy_v = v.copy()
                copy_v.time = j
                mut_v.append(copy_v)
        else:
            for j in [x for x in range(num_const_types) if x != v.index]:
                copy_v = v.copy()
                copy_v.index = j
                mut_v.append(copy_v)

        for mv in mut_v:
            copy_mr = initial_mr.copy()
            if i == 0:
                copy_mr.p_left.v_left = mv
            elif i == 1:
                copy_mr.p_left.v_right = mv
            elif i == 2:
                copy_mr.p_right.v_left = mv
            else:
                copy_mr.p_right.v_right = mv

            copy_mr = converter.convert_time(copy_mr)
            if not copy_mr in population:
                population.append(copy_mr)
    return population


def crossover(copy_s1, copy_s2, crossover_rate):
    is_prop = random.random()
    if is_prop < XOVER_PROP_RATE:
        (o1, o2) = crossover_prop(copy_s1, copy_s2, crossover_rate)
    else:
        (o1, o2) = crossover_val_op(copy_s1, copy_s2, crossover_rate)
    return o1, o2


def crossover_prop(copy_s1, copy_s2, crossover_rate):
    is_direct = True

    if is_direct:
        do_crossover = random.random() < crossover_rate
        if do_crossover:
            (copy_s1.p_left, copy_s2.p_left) = (copy_s2.p_left, copy_s1.p_left)

        do_crossover = random.random() < crossover_rate
        if do_crossover:
            (copy_s1.p_right, copy_s2.p_right) = (copy_s2.p_right, copy_s1.p_right)
    else:
        do_crossover = random.random() < crossover_rate
        if do_crossover:
            (copy_s1.p_left, copy_s2.p_right) = (copy_s2.p_right, copy_s1.p_left)

        do_crossover = random.random() < crossover_rate
        if do_crossover:
            (copy_s1.p_right, copy_s2.p_left) = (copy_s2.p_left, copy_s1.p_right)
    return copy_s1, copy_s2


def crossover_val_op(copy_s1, copy_s2, crossover_rate):
    keep_prop_order = True
    keep_value_order = True

    if keep_prop_order:
        do_crossover = random.random() < crossover_rate
        if do_crossover:
            (copy_s1.p_left.op, copy_s2.p_left.op) = (copy_s2.p_left.op, copy_s1.p_left.op)

        do_crossover = random.random() < crossover_rate
        if do_crossover:
            (copy_s1.p_right.op, copy_s2.p_right.op) = (copy_s2.p_right.op, copy_s1.p_right.op)

        if keep_value_order:
            do_crossover = random.random() < crossover_rate
            if do_crossover:
                (copy_s1.p_left.v_left, copy_s2.p_left.v_left) = (copy_s2.p_left.v_left, copy_s1.p_left.v_left)

            do_crossover = random.random() < crossover_rate
            if do_crossover:
                (copy_s1.p_left.v_right, copy_s2.p_left.v_right) = (copy_s2.p_left.v_right, copy_s1.p_left.v_right)

            do_crossover = random.random() < crossover_rate
            if do_crossover:
                (copy_s1.p_right.v_left, copy_s2.p_right.v_left) = (copy_s2.p_right.v_left, copy_s1.p_right.v_left)

            do_crossover = random.random() < crossover_rate
            if do_crossover:
                (copy_s1.p_right.v_right, copy_s2.p_right.v_right) = (copy_s2.p_right.v_right, copy_s1.p_right.v_right)
        else:
            do_crossover = random.random() < crossover_rate
            if do_crossover:
                (copy_s1.p_left.v_left, copy_s2.p_left.v_right) = (copy_s2.p_left.v_right, copy_s1.p_left.v_left)

            do_crossover = random.random() < crossover_rate
            if do_crossover:
                (copy_s1.p_left.v_right, copy_s2.p_left.v_left) = (copy_s2.p_left.v_left, copy_s1.p_left.v_right)

            do_crossover = random.random() < crossover_rate
            if do_crossover:
                (copy_s1.p_right.v_left, copy_s2.p_right.v_right) = (copy_s2.p_right.v_right, copy_s1.p_right.v_left)

            do_crossover = random.random() < crossover_rate
            if do_crossover:
                (copy_s1.p_right.v_right, copy_s2.p_right.v_left) = (copy_s2.p_right.v_left, copy_s1.p_right.v_right)
    else:
        do_crossover = random.random() < crossover_rate
        if do_crossover:
            (copy_s1.p_left.op, copy_s2.p_right.op) = (copy_s2.p_right.op, copy_s1.p_left.op)

        do_crossover = random.random() < crossover_rate
        if do_crossover:
            (copy_s1.p_right.op, copy_s2.p_left.op) = (copy_s2.p_left.op, copy_s1.p_right.op)

        if keep_value_order:
            do_crossover = random.random() < crossover_rate
            if do_crossover:
                (copy_s1.p_left.v_left, copy_s2.p_right.v_left) = (copy_s2.p_right.v_left, copy_s1.p_left.v_left)

            do_crossover = random.random() < crossover_rate
            if do_crossover:
                (copy_s1.p_left.v_right, copy_s2.p_right.v_right) = (copy_s2.p_right.v_right, copy_s1.p_left.v_right)

            do_crossover = random.random() < crossover_rate
            if do_crossover:
                (copy_s1.p_right.v_left, copy_s2.p_left.v_left) = (copy_s2.p_left.v_left, copy_s1.p_right.v_left)

            do_crossover = random.random() < crossover_rate
            if do_crossover:
                (copy_s1.p_right.v_right, copy_s2.p_left.v_right) = (copy_s2.p_left.v_right, copy_s1.p_right.v_right)
        else:
            do_crossover = random.random() < crossover_rate
            if do_crossover:
                (copy_s1.p_left.v_left, copy_s2.p_right.v_right) = (copy_s2.p_right.v_right, copy_s1.p_left.v_left)

            do_crossover = random.random() < crossover_rate
            if do_crossover:
                (copy_s1.p_left.v_right, copy_s2.p_right.v_left) = (copy_s2.p_right.v_left, copy_s1.p_left.v_right)

            do_crossover = random.random() < crossover_rate
            if do_crossover:
                (copy_s1.p_right.v_left, copy_s2.p_left.v_right) = (copy_s2.p_left.v_right, copy_s1.p_right.v_left)

            do_crossover = random.random() < crossover_rate
            if do_crossover:
                (copy_s1.p_right.v_right, copy_s2.p_left.v_left) = (copy_s2.p_left.v_left, copy_s1.p_right.v_right)
    return copy_s1, copy_s2


def mutate(individual, mutation_rate, num_var_types, num_const_types, time_range):
    is_prop = random.random()
    if is_prop < MUT_PROP_RATE:
        o1 = mutate_prop(individual, mutation_rate, num_var_types, num_const_types, time_range)
    else:
        o1 = mutate_val_op(individual, mutation_rate, num_var_types, num_const_types, time_range)
    return o1


def mutate_prop(individual, mutation_rate, num_var_types, num_const_types, time_range):
    is_replace = True
    if is_replace:
        do_mutate = random.random() < mutation_rate
        if do_mutate:
            individual.p_left = generate_proposition(num_var_types, num_const_types, time_range)
        do_mutate = random.random() < mutation_rate
        if do_mutate:
            individual.p_right = generate_proposition(num_var_types, num_const_types, time_range)
    else:
        do_mutate = random.random() < mutation_rate
        if do_mutate:
            (individual.p_left, individual.p_right) = (individual.p_right, individual.p_left)
    return individual


def mutate_val_op(individual, mutation_rate, num_var_types, num_const_types, time_range):
    is_replace = True
    within_prop = True
    keep_value_order = True
    if is_replace:
        do_mutate = random.random() < mutation_rate
        if do_mutate:
            rand_op = random.randrange(len(MR.OPERATORS))
            individual.p_left.op = MR.OPERATORS[rand_op]
        do_mutate = random.random() < mutation_rate
        if do_mutate:
            rand_op = random.randrange(len(MR.OPERATORS))
            individual.p_right.op = MR.OPERATORS[rand_op]
        do_mutate = random.random() < mutation_rate
        if do_mutate:
            individual.p_left.v_left = generate_value(num_var_types, num_const_types, time_range)
        do_mutate = random.random() < mutation_rate
        if do_mutate:
            individual.p_left.v_right = generate_value(num_var_types, num_const_types, time_range)
        do_mutate = random.random() < mutation_rate
        if do_mutate:
            individual.p_right.v_left = generate_value(num_var_types, num_const_types, time_range)
        do_mutate = random.random() < mutation_rate
        if do_mutate:
            individual.p_right.v_right = generate_value(num_var_types, num_const_types, time_range)
    else:
        do_mutate = random.random() < mutation_rate
        if do_mutate:
            (individual.p_left.op, individual.p_right.op) = (individual.p_right.op, individual.p_left.op)
        if within_prop:
            do_mutate = random.random() < mutation_rate
            if do_mutate:
                (individual.p_left.v_left, individual.p_left.v_right) = (
                    individual.p_left.v_right, individual.p_left.v_left)
            do_mutate = random.random() < mutation_rate
            if do_mutate:
                (individual.p_right.v_left, individual.p_right.v_right) = (
                    individual.p_right.v_right, individual.p_right.v_left)
        else:
            if keep_value_order:
                do_mutate = random.random() < mutation_rate
                if do_mutate:
                    (individual.p_left.v_left, individual.p_right.v_left) = (
                        individual.p_right.v_left, individual.p_left.v_left)
                do_mutate = random.random() < mutation_rate
                if do_mutate:
                    (individual.p_left.v_right, individual.p_right.v_right) = (
                        individual.p_right.v_right, individual.p_left.v_right)
            else:
                do_mutate = random.random() < mutation_rate
                if do_mutate:
                    (individual.p_left.v_left, individual.p_right.v_right) = (
                        individual.p_right.v_right, individual.p_left.v_left)
                do_mutate = random.random() < mutation_rate
                if do_mutate:
                    (individual.p_left.v_right, individual.p_right.v_left) = (
                        individual.p_right.v_left, individual.p_left.v_right)
    return individual


def generate_value(num_var_types, num_const_types, time_range):
    rand_v_type = random.randrange(num_const_types + num_var_types * time_range)
    v = MR.Value()
    if rand_v_type < num_const_types:
        v.type = MR.VAL_TYPE_CONS
        v.index = random.randrange(num_const_types)
    else:
        v.type = MR.VAL_TYPE_VAR
        v.index = random.randrange(num_var_types)
        v.time = random.randrange(time_range)
    return v


def generate_proposition(num_var_types, num_const_types, time_range):
    rand_op = random.randrange(len(MR.OPERATORS))
    op = MR.OPERATORS[rand_op]

    lv = generate_value(num_var_types, num_const_types, time_range)
    rv = generate_value(num_var_types, num_const_types, time_range)
    return MR.Prop(lv, op, rv)

