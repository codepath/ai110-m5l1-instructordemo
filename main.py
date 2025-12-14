import random

MAX_STEPS = 12
STALL_STOP = None 
COST_PER_STEP = 0.2
SEED = 2

random.seed(SEED)

bug_score = 5 
repeat_count = 0
cost = 0.0

def plan():
    return "Try quick fix A"

def act(plan):
    return "apply_fix_A"

def check(action, bug_score):
    roll = random.random()
    if roll < 0.1:
        return "PARTIAL", bug_score - 1
    return "FAIL", bug_score

print("\nSTEP | bug_score | cost  | decision")
print("--------------------------------------")

for step in range(1, MAX_STEPS + 1):
    p = plan()
    a = act(p)
    result, new_score = check(a, bug_score)

    cost += COST_PER_STEP

    if new_score == bug_score:
        repeat_count += 1
    else:
        repeat_count = 0

    bug_score = max(0, new_score)

    if bug_score == 0:
        print(f"{step:>4} | {bug_score:>9} | ${cost:<4.1f} | ✅ fixed")
        break

    if STALL_STOP is not None and repeat_count >= STALL_STOP:
        print(f"{step:>4} | {bug_score:>9} | ${cost:<4.1f} | 🛑 stalled → ask human")
        break

    print(f"{step:>4} | {bug_score:>9} | ${cost:<4.1f} | continue ({result})")

if bug_score != 0 and (STALL_STOP is None):
    print("\nNote: We only stopped because MAX_STEPS ended.")
