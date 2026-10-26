"""
Math Detective Generator: "Sneaky Pete's Error Hunt".
Models authentic 3rd-grade student misconceptions (SMP 3 reasoning).
Supports Grade 2 scaffolds, Grade 3 core, and Grade 4 extensions.
"""

import random
from typing import List, Dict, Any, Optional
from generators.math_engine import (
    get_strategy_tag, get_repeated_addition_hint,
    generate_extension_challenge, generate_scaffold_support
)

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
            return wrong, f"Pete added {f1} + {f2} = {wrong} instead of multiplying!"
            
    if chosen_type == "off_by_one_group":
        step = f1 if rng.choice([True, False]) else f2
        wrong = correct + step if (rng.choice([True, False]) or correct - step <= 0) else correct - step
        if wrong != correct and wrong > 0:
            return wrong, f"Pete was off by one group of {step}!"
            
    if chosen_type == "doubling_slip":
        if f1 in (4, 8) or f2 in (4, 8):
            wrong = correct // 2
            if wrong != correct and wrong > 0:
                return wrong, "Pete doubled once, but forgot to double again!"
                
    if chosen_type == "digit_swap" and (f1 == 9 or f2 == 9) and correct >= 10:
        tens = correct // 10
        ones = correct % 10
        wrong = (ones * 10) + tens
        if wrong != correct and wrong > 0:
            return wrong, f"Pete flipped the tens and ones digits on his 9s fact!"

    delta = rng.choice([-4, -2, 2, 4])
    wrong = max(0, correct + delta)
    if wrong == correct:
        wrong = correct + 3
    return wrong, f"Pete miscalculated by {abs(correct - wrong)}."

def build_detective_puzzle(
    target_numbers: List[int],
    is_half_page: bool = False,
    orientation: str = "horizontal",
    differentiation_level: str = "core",
    problem_count_override: Optional[int] = None,
    seed: Optional[int] = None,
    **kwargs
) -> Dict[str, Any]:
    """Builds a complete Sneaky Pete Error Hunt activity."""
    rng = random.Random(seed)
    
    if problem_count_override:
        count = problem_count_override
    else:
        count = 6 if is_half_page else 12
        
    target_error_count = 2 if is_half_page else 4
    
    factor_pool = list(range(1, 11)) if differentiation_level == "scaffold" else list(range(0, 13))
    pairs = []
    for t in target_numbers:
        for p in factor_pool:
            pairs.append((t, p))
            
    rng.shuffle(pairs)
    while len(pairs) < count:
        pairs.extend(pairs)
    selected_pairs = pairs[:count]
    
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
        rep_hint = get_repeated_addition_hint(f1, f2) if differentiation_level == "scaffold" else ""
        
        problems.append({
            "id": idx,
            "factor1": f1,
            "factor2": f2,
            "displayed_answer": displayed_ans,
            "correct_answer": correct_ans,
            "is_error": is_error,
            "error_reason": reason,
            "repeated_addition_hint": rep_hint,
            "display_orientation": disp_orientation,
            "strategy": get_strategy_tag(f1, f2)
        })
        
    extension_challenge = None
    scaffold_support = None
    if not is_half_page:
        if differentiation_level == "extension":
            extension_challenge = generate_extension_challenge(target_numbers, rng)
        elif differentiation_level == "scaffold":
            scaffold_support = generate_scaffold_support(target_numbers)

    return {
        "type": "detective",
        "character": "Sneaky Pete",
        "mission_title": "Math Detective: The Case of Sneaky Pete",
        "mission_brief": f"Sneaky Pete rushed his math and made exactly {target_error_count} sneaky mistakes! Put a check (✓) next to correct equations, circle the mistakes, and write the TRUE product on the line.",
        "target_error_count": target_error_count,
        "problems": problems,
        "is_half_page": is_half_page,
        "differentiation_level": differentiation_level,
        "extension_challenge": extension_challenge,
        "scaffold_support": scaffold_support,
        "case_notes_prompt": (not is_half_page and differentiation_level == "core")
    }
