"""
Math fact generation engine for 3rd-grade multiplication practice.
Aligned with WA CCSS-M (Grade 2 Scaffolds: 2.OA.C.4; Grade 3 Core: 3.OA.A.1, 3.OA.A.4, 3.OA.B.5, 3.OA.C.7; Grade 4 Extensions: 4.OA.A.1, 4.NBT.B.5).
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
        return "Place-Value Slide"
    if 5 in factors:
        return "Clock & Nickels (5s)"
    if 4 in factors:
        return "Double-Double"
    if 3 in factors:
        return "Double + 1 Group"
    if 9 in factors:
        return "Ten Minus 1 Group"
    if f1 == f2:
        return "Square Number"
    if 6 in factors:
        return "High-Five + 1 Group"
    if 7 in factors:
        return "5 + 2 Split"
    if 8 in factors:
        return "Double-Double-Double"
    if 11 in factors:
        return "Twin Digits"
    if 12 in factors:
        return "10 + 2 Split"
    return "Decomposition"

def get_repeated_addition_hint(f1: int, f2: int) -> str:
    """Generates Grade 2 scaffold repeated addition string (e.g. 3 × 4 -> 4 + 4 + 4)."""
    if f1 <= 0 or f2 <= 0:
        return "0 total"
    if f1 == 1:
        return f"{f2}"
    if f1 <= 6:
        return " + ".join([str(f2)] * f1)
    if f2 <= 6:
        return " + ".join([str(f1)] * f2)
    return " + ".join([str(f2)] * min(f1, 4)) + "..."

def generate_multiplication_problem(
    target_numbers: List[int],
    factor_pool: Optional[List[int]] = None,
    include_missing_factors: bool = False,
    orientation: str = "horizontal",
    differentiation_level: str = "core", # 'scaffold', 'core', 'extension'
    rng: Optional[random.Random] = None
) -> Dict[str, Any]:
    """Generates a single multiplication problem guaranteeing a target factor."""
    if rng is None:
        rng = random.Random()
        
    if not target_numbers:
        target_numbers = [2, 3, 4, 5]
    if factor_pool is None:
        factor_pool = list(range(1, 11)) if differentiation_level == "scaffold" else list(range(0, 13))

    f1 = rng.choice(target_numbers)
    f2 = rng.choice(factor_pool)
    
    # Commutative variety: 50% chance to flip order
    if rng.choice([True, False]):
        f1, f2 = f2, f1

    product = f1 * f2
    
    # Determine missing position
    missing_pos = "product"
    if include_missing_factors and differentiation_level != "scaffold" and rng.random() < 0.40:
        missing_pos = rng.choice(["factor1", "factor2"])

    # Determine display orientation
    if orientation == "mixed":
        disp_orientation = rng.choice(["horizontal", "vertical"])
    else:
        disp_orientation = orientation

    # Format text prompt
    rep_hint = get_repeated_addition_hint(f1, f2) if differentiation_level == "scaffold" else ""
    
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
        "repeated_addition_hint": rep_hint,
        "display_orientation": disp_orientation,
        "strategy": get_strategy_tag(f1, f2)
    }

def generate_extension_challenge(target_numbers: List[int], rng: random.Random) -> Dict[str, Any]:
    """
    Generates a Grade 4 extension challenge (WA CCSS 4.OA.A.1 & 4.OA.A.2).
    Multiplicative comparison word problem with student equation blanks.
    """
    names = [("Maya", "Leo"), ("Sam", "Ella"), ("Lucas", "Chloe"), ("Noah", "Aria"), ("Oliver", "Mia")]
    n1, n2 = rng.choice(names)
    items = ["stickers", "colored pencils", "marbles", "reading books", "trading cards", "seashells"]
    item = rng.choice(items)
    
    base_count = rng.choice([3, 4, 5, 6, 7, 8])
    friendly_targets = [t for t in target_numbers if 2 <= t <= 10] or [3, 4, 5]
    multiplier = rng.choice(friendly_targets)
    
    total = base_count * multiplier
    
    prompt = f"⭐ <b>GRADE 4 STAR CHALLENGE:</b> {n1} has {base_count} {item}. {n2} has <b>{multiplier} times as many</b> {item} as {n1}. How many {item} does {n2} have in all?"
    equation_blank = "Equation: _____ × _____ = _____ " + item
    solution_str = f"{base_count} × {multiplier} = {total} {item}"
    
    return {
        "type": "multiplicative_comparison",
        "standard": "WA CCSS 4.OA.A.1",
        "prompt": prompt,
        "equation_blank": equation_blank,
        "solution": solution_str,
        "base_count": base_count,
        "multiplier": multiplier,
        "total": total
    }

def generate_scaffold_support(target_numbers: List[int]) -> Dict[str, Any]:
    """
    Generates Grade 2 scaffold support (WA CCSS 2.OA.C.4 & 2.NBT.A.2).
    Equal groups dot array and visual skip-counting track.
    """
    t = target_numbers[0] if target_numbers else 3
    dots_sample = " ".join(["[• • •]"] * min(t, 5)) if t > 0 else "[ ]"
    return {
        "type": "visual_scaffold",
        "standard": "WA CCSS 2.OA.C.4",
        "title": f"🌱 Grade 2 Visual Scaffold: Multiples of {t}",
        "dots_visual": f"Equal Groups of {t}: {dots_sample}",
        "repeated_addition_example": f"Example: 3 groups of {t} = {t} + {t} + {t} = {3 * t}"
    }

def generate_fact_set(
    target_numbers: List[int],
    count: int = 14,
    include_missing_factors: bool = False,
    orientation: str = "horizontal",
    differentiation_level: str = "core",
    seed: Optional[int] = None
) -> List[Dict[str, Any]]:
    """Generates an optimal set of distinct multiplication facts."""
    rng = random.Random(seed)
    factor_pool = list(range(1, 11)) if differentiation_level == "scaffold" else list(range(0, 13))
    
    all_pairs = []
    for t in target_numbers:
        for p in factor_pool:
            all_pairs.append((t, p))
            if t != p:
                all_pairs.append((p, t))
    
    all_pairs = list(set(all_pairs))
    rng.shuffle(all_pairs)
    
    problems = []
    used_signatures = set()
    
    for f1, f2 in all_pairs:
        if len(problems) >= count:
            break
        sig = (min(f1, f2), max(f1, f2))
        if sig in used_signatures and len(all_pairs) > count * 1.5:
            continue
        used_signatures.add(sig)
        
        prob = generate_multiplication_problem(
            target_numbers=target_numbers,
            factor_pool=factor_pool,
            include_missing_factors=include_missing_factors,
            orientation=orientation,
            differentiation_level=differentiation_level,
            rng=rng
        )
        prob["factor1"] = f1
        prob["factor2"] = f2
        prob["product"] = f1 * f2
        prob["answer"] = f1 * f2 if prob["missing_pos"] == "product" else (f1 if prob["missing_pos"] == "factor1" else f2)
        prob["id"] = len(problems) + 1
        problems.append(prob)

    while len(problems) < count:
        prob = generate_multiplication_problem(
            target_numbers=target_numbers,
            factor_pool=factor_pool,
            include_missing_factors=include_missing_factors,
            orientation=orientation,
            differentiation_level=differentiation_level,
            rng=rng
        )
        prob["id"] = len(problems) + 1
        problems.append(prob)
        
    return problems
