import random

MAX_STEPS = 6
STALL_STOP = None
COST_PER_STEP = 9.50
SEED = 2

random.seed(SEED)

# Pretend "prompt" the code sends to a model
ANALYZER_PROMPT = """
You are an assistant helping an agent accomplish a goal.
Return a JSON object with keys:
- "next_action": either "toggle_cheese" or "place_order"
- "reason": short explanation
Return JSON only.
""".strip()

def call_model(prompt, order):
    """
    Simulates an LLM. Sometimes returns clean JSON, sometimes returns messy text.
    This is intentional: agents must handle imperfect model output.
    """
    # 70% chance: valid JSON
    if random.random() < 0.7:
        if order["cheese"] == "YES":
            return '{"next_action":"toggle_cheese","reason":"Cheese is still YES, try toggling it off."}'
        return '{"next_action":"place_order","reason":"Cheese is NO, place the order."}'

    # 30% chance: invalid / messy output
    return "I think you should toggle the cheese. next_action=toggle_cheese"

def parse_model_output(raw_text):
    """
    Minimal parsing to keep the lesson focused:
    Accept only strict JSON with required keys. Otherwise reject.
    """
    import json
    try:
        data = json.loads(raw_text)
    except Exception:
        return None, "ParseError: not valid JSON"

    if not isinstance(data, dict):
        return None, "SchemaError: not a JSON object"
    if "next_action" not in data or "reason" not in data:
        return None, "SchemaError: missing keys"
    if data["next_action"] not in ("toggle_cheese", "place_order"):
        return None, "SchemaError: invalid next_action"

    return data, "OK"

goal = "Order a burrito bowl with NO cheese"
order = {"item": "burrito bowl", "cheese": "YES"}
repeat_count = 0
cost = 0.0

def plan(order):
    # Code prepares context + prompt for the model
    prompt = f"{ANALYZER_PROMPT}\n\nGOAL: {goal}\nCURRENT_ORDER: {order}"
    raw = call_model(prompt, order)

    # Code parses and validates before trusting the output
    parsed, parse_status = parse_model_output(raw)

    if parsed is None:
        # Fallback: code refuses to trust model output and uses a safe heuristic
        if order["cheese"] == "YES":
            return {"plan_text": "Fallback: toggle cheese (heuristic)", "raw": raw, "parse": parse_status}
        return {"plan_text": "Fallback: place order (heuristic)", "raw": raw, "parse": parse_status}

    # Convert structured plan into the plan_text your act() already expects
    if parsed["next_action"] == "toggle_cheese":
        plan_text = "Try a quick fix: toggle the cheese setting"
    else:
        plan_text = "Place the order"

    return {"plan_text": plan_text, "raw": raw, "parse": parse_status}

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
print("STEP | plan                           | model_out (short)                 | parse | action                              | check   | cost   | decision")
print("-----------------------------------------------------------------------------------------------------------------------------------")

for step in range(1, MAX_STEPS + 1):
    plan_bundle = plan(order)
    plan_text = plan_bundle["plan_text"]
    raw_short = plan_bundle["raw"][:28].replace("\n", " ") + ("…" if len(plan_bundle["raw"]) > 28 else "")
    parse_status = plan_bundle["parse"]
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
        print(f"{step:>4} | {plan_text:<30} | {raw_short:<30} | {parse_status:<5} | {action:<34} | FAIL   | ${cost:<5.2f} | ✅ stop (done)")
        break

    if STALL_STOP is not None and repeat_count >= STALL_STOP:
        print(f"{step:>4} | {plan_text:<34} | {action:<34} | FAIL   | ${cost:<5.2f} | 🛑 stop (stalled → ask human)")
        print(f"{step:>4} | {plan_text:<30} | {raw_short:<30} | {parse_status:<5} | {action:<34} | FAIL   | ${cost:<5.2f} | 🛑 stop (stalled → ask human)")
        break

    print(f"{step:>4} | {plan_text:<30} | {raw_short:<30} | {parse_status:<5} | {action:<34} | FAIL   | ${cost:<5.2f} | continue")

if STALL_STOP is None:
    print("\nNote: We only stopped because MAX_STEPS ended (no guardrail).")
