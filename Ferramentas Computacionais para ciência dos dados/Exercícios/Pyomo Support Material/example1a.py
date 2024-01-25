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



