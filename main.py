from pulp import *

employees = ["A1", "A2", "A3", "A4", "A5"]
days = ["Pon", "Uto", "Sri", "Cet", "Pet"]
shifts = ["Jutro", "Popodne"]

model = LpProblem("CallCenterScheduling", LpMinimize)

x = LpVariable.dicts(
    "shift",
    (employees, days, shifts),
    cat="Binary"
)

# funkcija cilja
model += 0

# jedna smjena dnevno
for e in employees:
    for d in days:
        model += lpSum(x[e][d][s] for s in shifts) <= 1

# minimalno 2 zaposlenika po smjeni
for d in days:
    for s in shifts:
        model += lpSum(x[e][d][s] for e in employees) >= 2

model.solve()

for e in employees:
    for d in days:
        for s in shifts:
            if value(x[e][d][s]) == 1:
                print(e, d, s)
