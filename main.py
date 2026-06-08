from pulp import *

# =====================================
# PODACI
# =====================================

agents = ["A1", "A2", "A3", "A4", "A5"]
supervisors = ["S1", "S2"]

days = ["Pon", "Uto", "Sri", "Cet", "Pet"]

agent_shifts = ["7_15", "8_16", "10_18", "11_19"]
supervisor_shifts = ["6_14", "14_22"]

times = [f"T{i}" for i in range(1, 33)]

max_breaks_same_time = 2

# =====================================
# PRETVORBA T1-T32 U STVARNO VRIJEME
# =====================================

time_labels = {}

hour = 6
minute = 0

for i in range(1, 33):

    start = f"{hour:02d}:{minute:02d}"

    minute += 30

    if minute == 60:
        minute = 0
        hour += 1

    end = f"{hour:02d}:{minute:02d}"

    time_labels[f"T{i}"] = f"{start}-{end}"

# =====================================
# MODEL
# =====================================

model = LpProblem("CallCenterScheduling", LpMinimize)

# =====================================
# VARIJABLE
# =====================================

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

# =====================================
# FUNKCIJA CILJA
# =====================================

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

# =====================================
# JEDNA SMJENA DNEVNO
# =====================================

for a in agents:
    for d in days:
        model += (
            lpSum(
                x_agent[a][d][s]
                for s in agent_shifts
            ) <= 1
        )

for sv in supervisors:
    for d in days:
        model += (
            lpSum(
                x_supervisor[sv][d][s]
                for s in supervisor_shifts
            ) <= 1
        )

# =====================================
# 40 SATI TJEDNO
# =====================================

for a in agents:
    model += (
        lpSum(
            x_agent[a][d][s]
            for d in days
            for s in agent_shifts
        ) == 5
    )

for sv in supervisors:
    model += (
        lpSum(
            x_supervisor[sv][d][s]
            for d in days
            for s in supervisor_shifts
        ) == 5
    )

# =====================================
# MINIMALNA POPUNJENOST
# PRIMJER
# =====================================

for d in days:

    model += (
        lpSum(
            x_agent[a][d][s]
            for a in agents
            for s in agent_shifts
        ) >= 4
    )

    model += (
        lpSum(
            x_supervisor[sv][d][s]
            for sv in supervisors
            for s in supervisor_shifts
        ) >= 1
    )

# =====================================
# TOČNO JEDNA PAUZA AKO RADI
# =====================================

for a in agents:
    for d in days:

        model += (
            lpSum(
                breaks_agent[a][d][t]
                for t in times
            )
            ==
            lpSum(
                x_agent[a][d][s]
                for s in agent_shifts
            )
        )

for sv in supervisors:
    for d in days:

        model += (
            lpSum(
                breaks_supervisor[sv][d][t]
                for t in times
            )
            ==
            lpSum(
                x_supervisor[sv][d][s]
                for s in supervisor_shifts
            )
        )

# =====================================
# DOPUŠTENI SLOTOVI PAUZA
# =====================================

shift_slots_agent = {
    "7_15": list(range(3, 19)),
    "8_16": list(range(5, 21)),
    "10_18": list(range(9, 25)),
    "11_19": list(range(11, 27))
}

shift_slots_supervisor = {
    "6_14": list(range(1, 17)),
    "14_22": list(range(17, 33))
}

for a in agents:
    for d in days:
        for t in range(1, 33):

            allowed = lpSum(
                x_agent[a][d][s]
                for s in agent_shifts
                if t in shift_slots_agent[s]
            )

            model += (
                breaks_agent[a][d][f"T{t}"]
                <=
                allowed
            )

for sv in supervisors:
    for d in days:
        for t in range(1, 33):

            allowed = lpSum(
                x_supervisor[sv][d][s]
                for s in supervisor_shifts
                if t in shift_slots_supervisor[s]
            )

            model += (
                breaks_supervisor[sv][d][f"T{t}"]
                <=
                allowed
            )

# =====================================
# MAX ISTOVREMENIH PAUZA
# =====================================

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

# =====================================
# SOLVE
# =====================================

model.solve(PULP_CBC_CMD(msg=True))

print("\nSTATUS:", LpStatus[model.status])

# =====================================
# ISPIS SMJENA
# =====================================

print("\n===== AGENTI =====")

for a in agents:
    for d in days:
        for s in agent_shifts:

            if value(x_agent[a][d][s]) == 1:

                print(
                    f"{a:3} | {d:3} | Smjena: {s}"
                )

print("\n===== SUPERVIZORI =====")

for sv in supervisors:
    for d in days:
        for s in supervisor_shifts:

            if value(x_supervisor[sv][d][s]) == 1:

                print(
                    f"{sv:3} | {d:3} | Smjena: {s}"
                )

# =====================================
# ISPIS PAUZA
# =====================================

print("\n===== PAUZE =====")

for a in agents:
    for d in days:
        for t in times:

            if value(breaks_agent[a][d][t]) == 1:

                print(
                    f"{a:3} | {d:3} | Pauza: {time_labels[t]}"
                )

for sv in supervisors:
    for d in days:
        for t in times:

            if value(breaks_supervisor[sv][d][t]) == 1:

                print(
                    f"{sv:3} | {d:3} | Pauza: {time_labels[t]}"
                )
