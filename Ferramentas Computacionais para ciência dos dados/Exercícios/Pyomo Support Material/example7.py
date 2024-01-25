from pyomo.environ import *

M = 100

model = ConcreteModel()

model.x = Var(domain=NonNegativeReals)

model.y = Var(domain=NonNegativeReals)
model.y0 = Var(bounds=(0, 20))
model.y1 = Var(domain=NonNegativeReals)
model.by = Var(domain=Binary)

model.z = Var(domain=NonNegativeReals)
model.z0 = Var(bounds=(0, 30))
model.z1 = Var(domain=NonNegativeReals)
model.bz = Var(domain=Binary)

model.profit = Objective(sense=maximize, expr = 
                         + 40*model.x \
                         + 30*model.y0 + 50*model.y1 + 200*model.by \
                         + 50*model.z0 + 60*model.z1 + 300*model.bz)

model.dy = Constraint(expr = model.y == model.y0 + model.y1)
model.dz = Constraint(expr = model.z == model.z0 + model.z1)

model.demand = Constraint(expr = model.x <= 40)
model.laborA = Constraint(expr = model.x + model.y <= 80)
model.laborB = Constraint(expr = 2*model.x + model.z <= 100)
model.laborC = Constraint(expr = model.z <= 50)

model.bonus_y0 = Constraint(expr = model.y0 >= 20 - M*(1 - model.by))
model.bonus_z0 = Constraint(expr = model.z0 >= 30 - M*(1 - model.bz))
model.bonus_y1 = Constraint(expr = model.y1 <= M*model.by)
model.bonus_z1 = Constraint(expr = model.z1 <= M*model.bz)

# solve
#SolverFactory('cbc').solve(model).write()
solver = SolverFactory('gurobi')
solver.options['MIPGap'] = 0.02
solution = solver.solve(model, tee=True)
solution.write()

print(f"Profit = ${model.profit()}")
print(f"X = {model.x()} units")
print(f"Y = {model.y0()} + {model.y1()} = {model.y()} units  {model.by()}")
print(f"Z = {model.z0()} + {model.z1()} = {model.z()} units  {model.bz()}")
