"""
Math Detective Generator: "Sneaky Pete's Error Hunt".
Models authentic 3rd-grade student misconceptions (SMP 3 reasoning).
"""

import random
from typing import List, Dict, Any, Optional
from generators.math_engine import get_strategy_tag

def create_misconception_answer(f1: int, f2: int, rng: random.Random) -> (int, str):
    """
    Generates a realistic 3rd-grade mistake based on cognitive error patterns.
    Returns (incorrect_product, pedagogical_explanation).
    """
    correct = f1 * f2
    error_types = ["additive", "off_by_one_group", "digit_swap"]
    if 2 in (f1, f2) or 4 in (f1, f2) or 8 in (f1, f2):
        error_types.append("doubling_slip")
        
    chosen_type = rng.choice(error_types)
    
    if chosen_type == "additive":
        wrong = f1 + f2
        if wrong != correct:
            return wrong, f"Pete added {f1} + {f2} instead of multiplying!"
            
    if chosen_type == "off_by_one_group":
        # Off by 1 group (either added an extra group or missed one)
        step = f1 if rng.choice([True, False]) else f2
        wrong = correct + step if (rng.choice([True, False]) or correct - step <= 0) else correct - step
        if wrong != correct and wrong > 0:
            return wrong, f"Pete was off by one group of {step}!"
            
    if chosen_type == "doubling_slip":
        # Forgot to double again or halved
        if f1 in (4, 8) or f2 in (4, 8):
            wrong = correct // 2
            if wrong != correct and wrong > 0:
                return wrong, "Pete doubled once, but forgot to double again!"
                
    if chosen_type == "digit_swap" and (f1 == 9 or f2 == 9) and correct >= 10:
        # Inverted digits (e.g., 36 -> 63 or 54 -> 45)
        tens = correct // 10
        ones = correct % 10
        wrong = (ones * 10) + tens
        if wrong != correct and wrong > 0:
            return wrong, f"Pete flipped the tens and ones digits on his 9s fact!"

    # Fallback plausible mistake: off by 2 or 4
    delta = rng.choice([-4, -2, 2, 4])
    wrong = max(0, correct + delta)
    if wrong == correct:
        wrong = correct + 3
    return wrong, f"Pete miscalculated by {abs(correct - wrong)}."

def build_detective_puzzle(
    target_numbers: List[int],
    is_half_page: bool = False,
    orientation: str = "horizontal",
    seed: Optional[int] = None
) -> Dict[str, Any]:
    """Builds a complete Sneaky Pete Error Hunt activity."""
    rng = random.Random(seed)
    
    count = 6 if is_half_page else 10
    target_error_count = 2 if is_half_page else 3
    
    factor_pool = list(range(0, 13))
    pairs = []
    for t in target_numbers:
        for p in factor_pool:
            pairs.append((t, p))
            
    rng.shuffle(pairs)
    selected_pairs = pairs[:count]
    
    # Pick indices for errors
    error_indices = set(rng.sample(range(count), target_error_count))
    
    problems = []
    for idx, (f1, f2) in enumerate(selected_pairs, 1):
        if rng.choice([True, False]):
            f1, f2 = f2, f1
            
        correct_ans = f1 * f2
        is_error = idx - 1 in error_indices
        
        if is_error:
            displayed_ans, reason = create_misconception_answer(f1, f2, rng)
        else:
            displayed_ans = correct_ans
            reason = "Correct! Pete solved this accurately."
            
        disp_orientation = rng.choice(["horizontal", "vertical"]) if orientation == "mixed" else orientation
        
        problems.append({
            "id": idx,
            "factor1": f1,
            "factor2": f2,
            "displayed_answer": displayed_ans,
            "correct_answer": correct_ans,
            "is_error": is_error,
            "error_reason": reason,
            "display_orientation": disp_orientation,
            "strategy": get_strategy_tag(f1, f2)
        })
        
    return {
        "type": "detective",
        "character": "Sneaky Pete",
        "mission_title": "Math Detective: The Case of Sneaky Pete",
        "mission_brief": f"Sneaky Pete rushed his math and made exactly {target_error_count} sneaky mistakes! Put a check (✓) next to the correct facts, circle the mistakes, and write the TRUE product on the line.",
        "target_error_count": target_error_count,
        "problems": problems,
        "is_half_page": is_half_page
    }
