from __future__ import print_function

from ortools.algorithms import pywrapknapsack_solver
from ortools.linear_solver import pywraplp
from ortools.graph import pywrapgraph
from ortools.algorithms import pywrapknapsack_solver
from ortools.graph import pywrapgraph
from ortools.sat.python import cp_model
import time
import random
import sys

# lib_v vector con los libros que están en cada biblioteca
# size_v dado un orden de bibliotecas, size_v guarda el total de libros que puede escanear bib_i
# scores son los scores de los libros

def permutationToSizeV(perm, signup_time, flow, total_days):
    n = range(len(perm))
    s = 0
    size_v = []
    for i in range(len(perm)):
        size_v.append(0)
    for i in range(len(perm)):
        d = total_days - s - signup_time[perm[i]]
        if(d <= 0):
            size_v[perm[i]] = 0
        else:
            size_v[perm[i]] = flow[perm[i]]*d
        s = s + signup_time[perm[i]]
    return size_v


def applyKnapsack(lib_v, size_v, scores):
    knap = pywraplp.Solver('simple_mip_program', pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)
    x={}
    for l in range(len(lib_v)):
        for b in range(len(scores)):
            x[(l,b)] = knap.IntVar(0,1, 'library_book_%i_%i' % (l,b))
    for b in range(len(scores)):
        knap.Add(sum(x[(l,b)] for l in range(len(lib_v))) <= 1)
    for l in range(len(lib_v)):
        knap.Add(sum(x[(l,b)] for b in range(len(scores))) <= size_v[l])
    for l in range(len(lib_v)):
        for b in range(len(scores)):
            if( not (b in lib_v[l]) ):
                knap.Add(x[(l,b)] == 0)
    objective = knap.Objective()
    for l in range(len(lib_v)):
        for b in range(len(scores)):
            objective.SetCoefficient(x[(l,b)], scores[b])
    objective.SetMaximization()
    #knap.MakeLimit(time=1)
    status=knap.Solve()
    #if( status == pywraplp.Solver.OPTIMAL ):
    lib_choices = []
    for l in range(len(lib_v)):
        l_row = []
        for b in range(len(scores)):
            if x[(l,b)].solution_value() > 0:
                l_row.append(b)
        lib_choices.append(l_row)
    return lib_choices, objective.Value()


def get_scores(xs, lib_v, flow, signup_time, days, scores):
    sc = []
    sol = []
    for x in xs:
        k = applyKnapsack(lib_v, permutationToSizeV(x, signup_time, flow, days), scores)
        sc.append(k[1])
        sol.append(k[0])
    return sc, sol


def crossover(xs, ys):
    n = len(xs)
    co = [[(xs[i]+ys[i])*0.5,i] for i in range(n)]
    co.sort(key=lambda x : x[0])
    for i in range(n):
        co[i][0] = i
    co.sort(key=lambda x:x[1])
    return [x[0] for x in co]

def mutate(xs):
    changes = 4
    n = len(xs)
    for _ in range(changes):
        i = random.randrange(n)
        j = random.randrange(n)
        xs[i], xs[j] = xs[j], xs[i]
    return xs

def order_ga(n, lib_v, flow, signup_time, days, scores_books):
    num_rounds = 1
    n_perms = int(2)
    #print(n_perms)
    perms = []
    for i in range(n_perms):
        perm = list(range(n))
        random.shuffle(perm)
        perms.append(perm)
    for _ in range(num_rounds):
        scores_and_sol = get_scores(perms, lib_v, flow, signup_time, days, scores_books)
        scores = list(zip(scores_and_sol[0], range(n_perms)))
        #print(scores[:2])
        scores.sort(key=lambda x : -x[0])
        fst, snd = scores[0], scores[1]
        j = fst[1]
        k = snd[1]
        new_cross = crossover(perms[j], perms[k])
        new_elem = mutate(new_cross)

        x, i = scores.pop()
        perms.pop(i)
        perms.append(new_elem)
    scores_and_sol = get_scores(perms, lib_v, flow, signup_time, days, scores_books)
    scores = list(zip(scores_and_sol[0], range(n_perms)))
    scores.sort(key=lambda x : x[0])
    _, i = scores[0]
    return (perms[i], scores_and_sol[1][i])


def main(args):
    filename = args[0]

    fp = open(filename)
    # reading input:
    # l1 = fp.readline()
    # vl1 = l1.split(' ')
    l1 = fp.readline()
    n_books, n_libs, days = [ int(x) for x in l1.split(' ')]
    scores = []
    line = fp.readline()
    scores = [int(x)  for x in line.split(' ')]
    libs = []
    for _ in range(n_libs):
        l = fp.readline()
        num_books, signup, shipped = [ int(x) for x in l.split(' ')]
        line = fp.readline()
        books = [int(x) for x in line.split(' ')]
        libs.append([num_books, signup, shipped, books])
    fp.close()
    lib_v = []
    flow = []
    signup_time = []
    for l in libs:
        lib_v.append(l[3])
        flow.append(l[2])
        signup_time.append(l[1])
    p,sol = order_ga(len(lib_v), lib_v, flow, signup_time, days, scores)

    with open('./'+filename.split('.')[1]+".out","w") as fp:
        #writing output:
        n = len([x for x in sol if sol is not [] ])
        fp.write(str(n)+'\n')
        for p_i in p:
            if sol[p_i] is not []:
                fp.write(str(p_i)+' '+str(len(sol[p_i]))+'\n')
                fp.write(' '.join(map(str,sol[p_i]))+'\n')   

if __name__ == '__main__':
    # usage: python main.py ./data/<datasetname>
    main(sys.argv[1:])
