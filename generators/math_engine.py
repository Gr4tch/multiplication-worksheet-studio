"""
Math fact generation engine for 3rd-grade multiplication practice.
Aligned with WA CCSS-M (3.OA.A.1, 3.OA.A.4, 3.OA.B.5, 3.OA.C.7) and Clear Math.
"""

import random
from typing import List, Dict, Any, Optional

def get_strategy_tag(f1: int, f2: int) -> str:
    """Returns the primary Clear Math conceptual strategy applicable to the fact."""
    factors = {f1, f2}
    if 0 in factors:
        return "Zero Property"
    if 1 in factors:
        return "Identity Property"
    if 2 in factors:
        return "Doubles"
    if 10 in factors:
        return "Place-Value Shift"
    if 5 in factors:
        return "Half-of-Ten"
    if 4 in factors:
        return "Double and Double Again"
    if 3 in factors:
        return "Double Plus One Group"
    if 9 in factors:
        return "Ten Minus One Group"
    if f1 == f2:
        return "Square Number"
    if 6 in factors:
        return "Five Plus One Group"
    if 7 in factors:
        return "Decompose (5s + 2s)"
    if 8 in factors:
        return "Double-Double-Double"
    if 11 in factors:
        return "Ten Plus One Group"
    if 12 in factors:
        return "Ten Plus Two Groups"
    return "Decomposition"

def generate_multiplication_problem(
    target_numbers: List[int],
    factor_pool: Optional[List[int]] = None,
    include_missing_factors: bool = False,
    orientation: str = "horizontal",
    rng: Optional[random.Random] = None
) -> Dict[str, Any]:
    """Generates a single multiplication problem guaranteeing a target factor."""
    if rng is None:
        rng = random.Random()
        
    if not target_numbers:
        target_numbers = [2, 3, 4, 5]
    if factor_pool is None:
        factor_pool = list(range(0, 13))

    f1 = rng.choice(target_numbers)
    f2 = rng.choice(factor_pool)
    
    # Commutative variety: 50% chance to flip order
    if rng.choice([True, False]):
        f1, f2 = f2, f1

    product = f1 * f2
    
    # Determine missing position
    missing_pos = "product"
    if include_missing_factors and rng.random() < 0.40:
        missing_pos = rng.choice(["factor1", "factor2"])

    # Determine display orientation
    if orientation == "mixed":
        disp_orientation = rng.choice(["horizontal", "vertical"])
    else:
        disp_orientation = orientation

    # Format text prompt
    if missing_pos == "product":
        answer = product
        prompt_str = f"{f1} × {f2} = ____"
    elif missing_pos == "factor1":
        answer = f1
        prompt_str = f"____ × {f2} = {product}"
    else:
        answer = f2
        prompt_str = f"{f1} × ____ = {product}"

    return {
        "factor1": f1,
        "factor2": f2,
        "product": product,
        "missing_pos": missing_pos,
        "answer": answer,
        "prompt_str": prompt_str,
        "display_orientation": disp_orientation,
        "strategy": get_strategy_tag(f1, f2)
    }

def generate_fact_set(
    target_numbers: List[int],
    count: int = 12,
    include_missing_factors: bool = False,
    orientation: str = "horizontal",
    seed: Optional[int] = None
) -> List[Dict[str, Any]]:
    """Generates an optimal set of distinct multiplication facts."""
    rng = random.Random(seed)
    factor_pool = list(range(0, 13))
    
    # Generate candidate combinations
    all_pairs = []
    for t in target_numbers:
        for p in factor_pool:
            all_pairs.append((t, p))
            if t != p:
                all_pairs.append((p, t))
    
    # Remove duplicate tuples
    all_pairs = list(set(all_pairs))
    rng.shuffle(all_pairs)
    
    problems = []
    used_signatures = set()
    
    for f1, f2 in all_pairs:
        if len(problems) >= count:
            break
        sig = (min(f1, f2), max(f1, f2))
        # Keep pairs diverse
        if sig in used_signatures and len(all_pairs) > count * 1.5:
            continue
        used_signatures.add(sig)
        
        product = f1 * f2
        missing_pos = "product"
        if include_missing_factors and rng.random() < 0.35:
            missing_pos = rng.choice(["factor1", "factor2"])
            
        disp_orientation = rng.choice(["horizontal", "vertical"]) if orientation == "mixed" else orientation
        
        if missing_pos == "product":
            answer = product
            prompt_str = f"{f1} × {f2} = ____"
        elif missing_pos == "factor1":
            answer = f1
            prompt_str = f"____ × {f2} = {product}"
        else:
            answer = f2
            prompt_str = f"{f1} × ____ = {product}"
            
        problems.append({
            "id": len(problems) + 1,
            "factor1": f1,
            "factor2": f2,
            "product": product,
            "missing_pos": missing_pos,
            "answer": answer,
            "prompt_str": prompt_str,
            "display_orientation": disp_orientation,
            "strategy": get_strategy_tag(f1, f2)
        })

    # If count not reached, fill with random draws
    while len(problems) < count:
        prob = generate_multiplication_problem(
            target_numbers=target_numbers,
            factor_pool=factor_pool,
            include_missing_factors=include_missing_factors,
            orientation=orientation,
            rng=rng
        )
        prob["id"] = len(problems) + 1
        problems.append(prob)
        
    return problems
