import random

MAX_STEPS = 6
STALL_STOP = None
COST_PER_STEP = 9.50
SEED = 2

random.seed(SEED)

goal = "Order a burrito bowl with NO cheese"
order = {"item": "burrito bowl", "cheese": "YES"}
repeat_count = 0
cost = 0.0

def plan(order):
    if order["cheese"] == "YES":
        return "Try a quick fix: toggle the cheese setting"
    return "Place the order"

def act(plan_text, order):
    # The bug: the agent THINKS it toggled cheese, but the order doesn't actually change.
    if "toggle" in plan_text:
        return "Clicked 'No cheese' (but it didn't save)"
    return "Placed order"

def check(action, order):
    # "Reality check": what we actually ordered
    if action == "Placed order":
        if order["cheese"] == "NO":
            return "SUCCESS", "Order matches goal"
        return "FAIL", "Order still has cheese"
    return "FAIL", "No real change happened"

print("\n=== Agent Trace: Plan → Act → Check → Decide ===")
print(f"GOAL: {goal}\n")
print("STEP | plan                               | action                              | check   | cost   | decision")
print("--------------------------------------------------------------------------------------------------------------")

for step in range(1, MAX_STEPS + 1):
    plan_text = plan(order)
    action = act(plan_text, order)
    status, evidence = check(action, order)

    # Cost only happens when the agent places an order
    if action == "Placed order":
        cost += COST_PER_STEP

    # Stall detection: did we make any real progress toward the goal?
    # Progress means order['cheese'] flips to "NO".
    if order["cheese"] == "YES":
        repeat_count += 1
    else:
        repeat_count = 0

    if status == "SUCCESS":
        print(f"{step:>4} | {plan_text:<34} | {action:<34} | OK     | ${cost:<5.2f} | ✅ stop (done)")
        break

    if STALL_STOP is not None and repeat_count >= STALL_STOP:
        print(f"{step:>4} | {plan_text:<34} | {action:<34} | FAIL   | ${cost:<5.2f} | 🛑 stop (stalled → ask human)")
        break

    print(f"{step:>4} | {plan_text:<34} | {action:<34} | FAIL   | ${cost:<5.2f} | continue")

if STALL_STOP is None:
    print("\nNote: We only stopped because MAX_STEPS ended (no guardrail).")
