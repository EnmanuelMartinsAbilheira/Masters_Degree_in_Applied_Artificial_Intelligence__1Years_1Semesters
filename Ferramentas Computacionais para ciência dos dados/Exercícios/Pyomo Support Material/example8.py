import shutil
import sys
import os.path

from pyomo.environ import *

# iDemand requirements
Demand = {
   'Lon': 125,        # London
   'Ber': 175,        # Berlin
   'Maa': 225,        # Maastricht
   'Ams': 250,        # Amsterdam
   'Utr': 225,        # Utrecht
   'Hag': 200         # The Hague
}

# Supplies available at each of the sources
Supply = {
   'Arn': 600,        # Arnhem
   'Gou': 650         # Gouda
}

# Transportation costs
T = {
    ('Lon', 'Arn'): 1000,
    ('Lon', 'Gou'): 2.5,
    ('Ber', 'Arn'): 2.5,
    ('Ber', 'Gou'): 1000,
    ('Maa', 'Arn'): 1.6,
    ('Maa', 'Gou'): 2.0,
    ('Ams', 'Arn'): 1.4,
    ('Ams', 'Gou'): 1.0,
    ('Utr', 'Arn'): 0.8,
    ('Utr', 'Gou'): 1.0,
    ('Hag', 'Arn'): 1.4,
    ('Hag', 'Gou'): 0.8
}

# Step 0: Create an instance of the model
model = ConcreteModel()
model.dual = Suffix(direction=Suffix.IMPORT) #Importing extra information from a solver about the solution of a mathematical program
                                             # Suffix.IMPORT_EXPORT Suffix.EXPORT Suffix.IMPORT

# Step 1: Define index sets
CUS = list(Demand.keys())
SRC = list(Supply.keys())

# Step 2: Define the decision
model.x = Var(CUS, SRC, domain = NonNegativeReals)

# Step 3: Define Objective
@model.Objective(sense=minimize)
def cost(m):
    return sum([T[c,s]*model.x[c,s] for c in CUS for s in SRC])

# Step 4: Constraints
@model.Constraint(SRC)
def src(m, s):
    return sum([model.x[c,s] for c in CUS]) <= Supply[s]

@model.Constraint(CUS)
def dmd(m, c):
    return sum([model.x[c,s] for s in SRC]) == Demand[c]

results = SolverFactory('cbc').solve(model)
results.write()

model.x.display()

for c in CUS:
    for s in SRC:
        print(c, s, model.x[c,s]())

if 'ok' == str(results.Solver.status):
    print("Total Shipping Costs = ", model.cost())
    print("\nShipping Table:")
    for s in SRC:
        for c in CUS:
            if model.x[c,s]() > 0:
                print("Ship from ", s," to ", c, ":", model.x[c,s]())
else:
    print("No Valid Solution Found")

print("--------------------------------------------------------")
print("Analysis by source")

if 'ok' == str(results.Solver.status):
    print("Source      Capacity   Shipped    Margin")
    for s in SRC:
        print(f"{s:10s}{Supply[s]:10.1f}{model.src[s]():10.1f}{model.dual[model.src[s]]:10.4f}")
else:
    print("No Valid Solution Found")


print("--------------------------------------------------------")
print("Analysis by customer")

if 'ok' == str(results.Solver.status):    
    print("Customer      Demand   Shipped    Margin")
    for c in CUS:
        print(f"{c:10s}{Demand[c]:10.1f}{model.dmd[c]():10.1f}{model.dual[model.dmd[c]]:10.4f}")
else:
    print("No Valid Solution Found")
