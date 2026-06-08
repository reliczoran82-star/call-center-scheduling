from pulp import *

# =========================
# PODACI
# =========================

agents = ["A1", "A2", "A3", "A4", "A5"]
supervisors = ["S1", "S2"]

days = ["Pon", "Uto", "Sri", "Cet", "Pet"]

agent_shifts = ["7_15", "8_16", "10_18", "11_19"]
supervisor_shifts = ["6_14", "14_22"]

times = [f"T{i}" for i in range(1, 33)]  # 32 polusatna intervala

max_breaks_same_time = 2

# =========================
# MODEL
# =========================

model = LpProblem("CallCenterScheduling", LpMinimize)

# =========================
# VARIJABLE
# =========================

x_agent = LpVariable.dicts(
    "AgentShift",
    (agents, days, agent_shifts),
    cat="Binary"
)

x_supervisor = LpVariable.dicts(
    "SupervisorShift",
    (supervisors, days, supervisor_shifts),
    cat="Binary"
)

breaks_agent = LpVariable.dicts(
    "AgentBreak",
    (agents, days, times),
    cat="Binary"
)

breaks_supervisor = LpVariable.dicts(
    "SupervisorBreak",
    (supervisors, days, times),
    cat="Binary"
)

# =========================
# FUNKCIJA CILJA
# =========================

model += (
    lpSum(
        x_agent[a][d][s]
        for a in agents
        for d in days
        for s in agent_shifts
    )
    +
    lpSum(
        x_supervisor[sv][d][s]
        for sv in supervisors
        for d in days
        for s in supervisor_shifts
    )
)

# =========================
# 1. JEDNA SMJENA DNEVNO
# =========================

for a in agents:
    for d in days:
        model += (
            lpSum(x_agent[a][d][s] for s in agent_shifts)
            <= 1
        )

for sv in supervisors:
    for d in days:
        model += (
            lpSum(x_supervisor[sv][d][s] for s in supervisor_shifts)
            <= 1
        )

# =========================
# 2. 40 SATI TJEDNO
# 5 smjena × 8 sati
# =========================

for a in agents:
    model += (
        lpSum(
            x_agent[a][d][s]
            for d in days
            for s in agent_shifts
        )
        == 5
    )

for sv in supervisors:
    model += (
        lpSum(
            x_supervisor[sv][d][s]
            for d in days
            for s in supervisor_shifts
        )
        == 5
    )

# =========================
# 3. MINIMALNA POPUNJENOST
# (primjer)
# =========================

for d in days:

    model += (
        lpSum(
            x_agent[a][d][s]
            for a in agents
            for s in agent_shifts
        )
        >= 4
    )

    model += (
        lpSum(
            x_supervisor[sv][d][s]
            for sv in supervisors
            for s in supervisor_shifts
        )
        >= 1
    )

# =========================
# 4. TOČNO JEDNA PAUZA
# =========================

for a in agents:
    for d in days:
        model += (
            lpSum(breaks_agent[a][d][t] for t in times)
            ==
            lpSum(x_agent[a][d][s] for s in agent_shifts)
        )

for sv in supervisors:
    for d in days:
        model += (
            lpSum(breaks_supervisor[sv][d][t] for t in times)
            ==
            lpSum(x_supervisor[sv][d][s] for s in supervisor_shifts)
        )

# =========================
# 5. DOPUŠTENI SLOTOVI PAUZE
# =========================

shift_slots_agent = {
    "7_15": list(range(3, 19)),
    "8_16": list(range(5, 21)),
    "10_18": list(range(9, 25)),
    "11_19": list(range(11, 27)),
}

shift_slots_supervisor = {
    "6_14": list(range(1, 17)),
    "14_22": list(range(17, 33)),
}

for a in agents:
    for d in days:
        for t in range(1, 33):

            allowed = lpSum(
                x_agent[a][d][s]
                for s in agent_shifts
                if t in shift_slots_agent[s]
            )

            model += breaks_agent[a][d][f"T{t}"] <= allowed

for sv in supervisors:
    for d in days:
        for t in range(1, 33):

            allowed = lpSum(
                x_supervisor[sv][d][s]
                for s in supervisor_shifts
                if t in shift_slots_supervisor[s]
            )

            model += breaks_supervisor[sv][d][f"T{t}"] <= allowed

# =========================
# 6. MAX BROJ LJUDI NA PAUZI
# =========================

for d in days:
    for t in times:

        model += (
            lpSum(
                breaks_agent[a][d][t]
                for a in agents
            )
            +
            lpSum(
                breaks_supervisor[sv][d][t]
                for sv in supervisors
            )
            <= max_breaks_same_time
        )

# =========================
# SOLVE
# =========================

model.solve(PULP_CBC_CMD(msg=True))

print("Status:", LpStatus[model.status])

print("\nAGENTI")
for a in agents:
    for d in days:
        for s in agent_shifts:
            if value(x_agent[a][d][s]) == 1:
                print(a, d, s)

print("\nSUPERVIZORI")
for sv in supervisors:
    for d in days:
        for s in supervisor_shifts:
            if value(x_supervisor[sv][d][s]) == 1:
                print(sv, d, s)

print("\nPAUZE")
for a in agents:
    for d in days:
        for t in times:
            if value(breaks_agent[a][d][t]) == 1:
                print(a, d, t)

for sv in supervisors:
    for d in days:
        for t in times:
            if value(breaks_supervisor[sv][d][t]) == 1:
                print(sv, d, t)
