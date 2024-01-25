from pyomo.environ import *

import os

# provide an email address
os.environ['NEOS_EMAIL'] = 'jcsilva@ipca.pt'

model = ConcreteModel()

# declare decision variables
model.x = Var(domain=NonNegativeReals)

# declare objective
model.profit = Objective(
    expr = 40*model.x,
    sense = maximize)

# declare constraints
model.laborA = Constraint(expr = model.x <= 80)
model.laborB = Constraint(expr = 2*model.x <= 100)

def display_solution(model):

    # display solution
    print('\nProfit = ', model.profit())

    print('\nDecision Variables')
    print('x = ', model.x.value)

    print('\nConstraints')
    print('Labor A = ', model.laborA())
    print('Labor B = ', model.laborB())

# solve
#SolverFactory('cbc').solve(model).write()

SolverFactory('clp').solve(model, tee=True).write()

display_solution(model)



