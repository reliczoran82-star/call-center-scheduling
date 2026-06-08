
from pulp import *

employees = ["A1", "A2", "A3", "A4", "A5"]
days = ["Pon", "Uto", "Sri", "Cet", "Pet"]
shifts = ["Jutro", "Popodne"]
times = ["T1","T2","T3","T4","T5","T6","T7","T8",
         "T9","T10","T11","T12","T13","T14","T15","T16"]

model = LpProblem("CallCenterScheduling", LpMinimize)

# VARIJABLE
x = LpVariable.dicts("shift", (employees, days, shifts), cat="Binary")
breaks = LpVariable.dicts("break", (employees, days, times), cat="Binary")

# dummy objective (samo da model bude validan)
model += lpSum(x[e][d][s] for e in employees for d in days for s in shifts)

# 1. max 1 smjena dnevno
for e in employees:
    for d in days:
        model += lpSum(x[e][d][s] for s in shifts) <= 1

# 2. minimalno 2 zaposlenika po smjeni
for d in days:
    for s in shifts:
        model += lpSum(x[e][d][s] for e in employees) >= 2

# 3. veza: pauza samo ako radi
for e in employees:
    for d in days:
        for t in times:
            model += breaks[e][d][t] <= lpSum(x[e][d][s] for s in shifts)

# 4. samo jedna pauza ako radi
for e in employees:
    for d in days:
        model += lpSum(breaks[e][d][t] for t in times) == lpSum(x[e][d][s] for s in shifts)

# 5. KLJUČNO: shift-based allowed break windows

for e in employees:
    for d in days:
        for t in times:

            # JUTRO → samo T1–T8
            if t in ["T1","T2","T3","T4","T5","T6","T7","T8"]:
                model += breaks[e][d][t] <= x[e][d]["Jutro"]

            # POPODNE → samo T9–T16
            else:
                model += breaks[e][d][t] <= x[e][d]["Popodne"]

# SOLVE 
model.solve(PULP_CBC_CMD(msg=True))

print("Status:", LpStatus[model.status])

# OUTPUT SMJENE
print("\nSHIFT ASSIGNMENTS:")
for e in employees:
    for d in days:
        for s in shifts:
            if value(x[e][d][s]) == 1:
                print(e, d, s)

# OUTPUT PAUZA
print("\nPauze:")
for e in employees:
    for d in days:
        for t in times:
            if value(breaks[e][d][t]) == 1:
                print(e, d, t)
