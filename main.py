"""
Demo 1: Failure Scales with Repetition (Instructor Starter Code)

Goal:
Show how a small mistake becomes a big problem when an agent loop repeats.

How to run:
python demo_failure_scales.py

What this simulates:
- An "agent" tries to complete a task in a loop.
- It makes a plausible-but-wrong decision (a common agent failure).
- The loop repeats, so the same mistake compounds: attempts, cost, and "confidence".
- Then we run a guarded version to show how engineers keep loops under control.

Tip for teaching:
Pause before running each demo and ask students to predict what will happen.
"""

from __future__ import annotations

import random
import time
from dataclasses import dataclass


# -----------------------------
# Configuration
# -----------------------------
SLEEP_SECONDS = 0.15  # small delay so the trace feels "alive"
RANDOM_SEED = 7       # fixed seed so output is repeatable


@dataclass
class DemoState:
    attempts: int = 0
    total_cost: float = 0.0
    confidence: float = 0.35
    last_result: str = "UNKNOWN"


def pretend_plan(state: DemoState) -> str:
    """
    Planner step:
    Produces a plan that sounds reasonable, but may be based on a wrong assumption.
    """
    plans = [
        "Try the most likely fix first.",
        "Make a small change and re-check.",
        "Assume the last approach was close and retry.",
        "Proceed with a quick patch and validate.",
    ]
    return random.choice(plans)


def pretend_act(state: DemoState) -> str:
    """
    Action step:
    Produces an action. Here we intentionally simulate a failure pattern:
    the agent keeps repeating the same kind of action even when it doesn't work.
    """
    actions = [
        "Apply patch A (fast).",
        "Apply patch A again (confidence up).",
        "Apply patch A with tiny tweak.",
        "Reformat and retry (low effort).",
    ]
    # Subtle: as confidence rises, the agent becomes more likely to repeat itself.
    if state.confidence > 0.65:
        return "Apply patch A again (overconfident repeat)."
    return random.choice(actions)


def pretend_check(state: DemoState) -> tuple[bool, str]:
    """
    Evaluator step:
    Returns (success, result_string).

    For this demo, the agent almost never succeeds because the "patch" strategy is wrong.
    That is the point: repetition doesn't magically improve correctness.
    """
    # Simulate that success is rare, and does NOT meaningfully improve with confidence.
    success_probability = 0.05
    success = random.random() < success_probability

    if success:
        return True, "PASS (unexpected)"
    else:
        return False, "FAIL (root cause unchanged)"


def update_state_after_attempt(state: DemoState, success: bool, result: str) -> None:
    """
    Update loop metrics to show compounding effects.
    """
    state.attempts += 1
    state.last_result = result

    # Simulated "cost" per attempt (tokens, time, money, whatever you want to call it)
    state.total_cost += 0.12

    # Simulated confidence drift (a dangerous pattern: confidence can rise even when wrong)
    if success:
        state.confidence = min(0.99, state.confidence + 0.10)
    else:
        # Danger: agent becomes slightly *more* confident with each retry due to "momentum"
        state.confidence = min(0.95, state.confidence + 0.06)


def print_trace_line(step: str, message: str) -> None:
    print(f"{step:<10} | {message}")


def run_naive_agent_loop(max_attempts: int = 12) -> None:
    """
    Naive loop:
    Keeps going until max_attempts, even though it's repeating a bad strategy.
    """
    print("\n=== NAIVE AGENT LOOP (minimal controls) ===")
    print("Watch how attempts + cost grow, even though nothing gets better.\n")

    state = DemoState()
    for _ in range(max_attempts):
        plan = pretend_plan(state)
        print_trace_line("PLAN", plan)
        time.sleep(SLEEP_SECONDS)

        action = pretend_act(state)
        print_trace_line("ACT", action)
        time.sleep(SLEEP_SECONDS)

        success, result = pretend_check(state)
        print_trace_line("CHECK", result)
        time.sleep(SLEEP_SECONDS)

        update_state_after_attempt(state, success, result)

        print_trace_line(
            "STATE",
            f"attempts={state.attempts}, cost=${state.total_cost:.2f}, confidence={state.confidence:.2f}"
        )
        print()

        if success:
            print("✅ Agent succeeded (rare). Stopping.\n")
            return

    print("🛑 Stopped only because we hit the maximum attempts.\n")


def run_guarded_agent_loop(max_attempts: int = 12, fail_streak_stop: int = 4) -> None:
    """
    Guarded loop:
    Demonstrates simple engineering controls:
    - Hard max attempts
    - Stop early if repeated failures happen (fail streak)
    - Escalate to "human review" instead of blindly repeating
    """
    print("\n=== GUARDED AGENT LOOP (engineered controls) ===")
    print("Watch how simple guardrails prevent runaway repetition.\n")

    state = DemoState()
    fail_streak = 0

    for _ in range(max_attempts):
        plan = pretend_plan(state)
        print_trace_line("PLAN", plan)
        time.sleep(SLEEP_SECONDS)

        action = pretend_act(state)
        print_trace_line("ACT", action)
        time.sleep(SLEEP_SECONDS)

        success, result = pretend_check(state)
        print_trace_line("CHECK", result)
        time.sleep(SLEEP_SECONDS)

        update_state_after_attempt(state, success, result)

        if success:
            fail_streak = 0
        else:
            fail_streak += 1

        print_trace_line(
            "STATE",
            f"attempts={state.attempts}, cost=${state.total_cost:.2f}, confidence={state.confidence:.2f}, fail_streak={fail_streak}"
        )

        # Guardrail: stop early if it's repeating failure
        if fail_streak >= fail_streak_stop:
            print_trace_line("DECISION", "Stop and ask a human (repeated failures).")
            print("\n🧑‍⚖️ Handing off to human review to prevent compounding harm.\n")
            return

        print_trace_line("DECISION", "Continue (but monitor).")
        print()

    print("🛑 Hit max attempts. Stopping.\n")


def main() -> None:
    random.seed(RANDOM_SEED)

    # Demo flow: naive first (to feel the danger), then guarded (to show engineering control)
    run_naive_agent_loop(max_attempts=10)
    run_guarded_agent_loop(max_attempts=10, fail_streak_stop=3)

    print("Teaching note: Ask students what changed between the two runs.")
    print("- The model didn't get smarter.")
    print("- The loop got safer.")


if __name__ == "__main__":
    main()
