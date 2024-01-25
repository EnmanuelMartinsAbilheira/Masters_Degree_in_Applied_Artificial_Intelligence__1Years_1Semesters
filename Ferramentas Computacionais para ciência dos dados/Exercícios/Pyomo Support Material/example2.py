from pyomo.environ import *

# create a model
model = ConcreteModel()

# declare decision variables
model.x = Var(domain=NonNegativeReals)
model.y = Var(domain=NonNegativeReals)

# declare objective
model.profit = Objective(expr = 40*model.x + 30*model.y, sense=maximize)

# declare constraints
model.demand = Constraint(expr = model.x <= 40)
model.laborA = Constraint(expr = model.x + model.y <= 80)
model.laborB = Constraint(expr = 2*model.x + model.y <= 100)

model.pprint()

def display_solution(model):

    # display solution
    print('\nProfit = ', model.profit())

    print('\nDecision Variables')
    print('x = ', model.x.value)
    print('y = ', model.y())

    print('\nConstraints')
    print('Demand  = ', model.demand())
    print('Labor A = ', model.laborA())
    print('Labor B = ', model.laborB())

#SolverFactory('clp').solve(model, tee=True).write()
SolverFactory('cbc').solve(model, tee=True).write()
#SolverFactory('ipopt').solve(model, tee=True).write()
#SolverFactory('bonmin').solve(model, tee=True).write()
#SolverFactory('couenne').solve(model, tee=True).write()

display_solution(model)



