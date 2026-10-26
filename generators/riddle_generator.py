"""
Riddle / Secret Code Generator for Multiplication Practice.
Maps unique letters of verified kid-friendly jokes to math facts.
Supports Grade 2 scaffolds, Grade 3 core, and Grade 4 extensions.
"""

import json
import random
from pathlib import Path
from typing import Dict, Any, List, Optional
from generators.math_engine import (
    generate_multiplication_problem, get_strategy_tag,
    generate_extension_challenge, generate_scaffold_support
)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

def load_jokes() -> List[Dict[str, Any]]:
    """Loads curated jokes from jokes_bank.json."""
    with open(DATA_DIR / "jokes_bank.json", "r", encoding="utf-8") as f:
        return json.load(f)["jokes"]

def get_jokes_by_category(category: Optional[str] = None) -> List[Dict[str, Any]]:
    jokes = load_jokes()
    if not category or category == "All":
        return jokes
    return [j for j in jokes if j["category"].lower() == category.lower()]

def build_riddle_puzzle(
    target_numbers: List[int],
    joke_id: Optional[str] = None,
    category: Optional[str] = None,
    is_half_page: bool = False,
    include_missing_factors: bool = False,
    orientation: str = "horizontal",
    differentiation_level: str = "core", # 'scaffold', 'core', 'extension'
    problem_count_override: Optional[int] = None,
    seed: Optional[int] = None
) -> Dict[str, Any]:
    """
    Builds a complete Riddle / Secret Code puzzle.
    In Full Page mode, generates a rich, balanced full-page layout with bonus facts and visual thinking tasks.
    """
    rng = random.Random(seed)
    candidates = get_jokes_by_category(category)
    
    if is_half_page:
        short_jokes = [j for j in candidates if j.get("length_category") == "short"]
        if short_jokes:
            candidates = short_jokes

    if joke_id:
        selected_joke = next((j for j in candidates if j["id"] == joke_id), candidates[0])
    else:
        selected_joke = rng.choice(candidates)

    punchline = selected_joke["punchline"].upper()
    words = punchline.split()

    # Find unique letters in punchline
    unique_letters = []
    for char in punchline:
        if char.isalpha() and char not in unique_letters:
            unique_letters.append(char)

    # Determine optimal problem count
    if problem_count_override:
        target_problem_count = problem_count_override
    else:
        target_problem_count = 8 if is_half_page else 14

    coded_letter_count = min(len(unique_letters), target_problem_count)
    coded_letters = unique_letters[:coded_letter_count]

    letter_to_problem = {}
    used_answers = set()
    used_factor_pairs = set()
    problems = []

    # 1. Generate problems for the riddle letters
    for idx, letter in enumerate(coded_letters, 1):
        attempts = 0
        problem = None
        while attempts < 100:
            prob = generate_multiplication_problem(
                target_numbers=target_numbers,
                include_missing_factors=include_missing_factors,
                orientation=orientation,
                differentiation_level=differentiation_level,
                rng=rng
            )
            ans = prob["answer"]
            pair = (min(prob["factor1"], prob["factor2"]), max(prob["factor1"], prob["factor2"]))
            
            if ans not in used_answers and pair not in used_factor_pairs:
                used_answers.add(ans)
                used_factor_pairs.add(pair)
                problem = prob
                break
            attempts += 1
            
        if problem is None:
            t = rng.choice(target_numbers)
            p = rng.randint(1, 10 if differentiation_level == "scaffold" else 12)
            ans = t * p
            used_answers.add(ans)
            problem = {
                "factor1": t,
                "factor2": p,
                "product": ans,
                "missing_pos": "product",
                "answer": ans,
                "prompt_str": f"{t} × {p} = ____",
                "repeated_addition_hint": f"{p} + {p} + {p}..." if differentiation_level == "scaffold" else "",
                "display_orientation": orientation if orientation != "mixed" else "horizontal",
                "strategy": get_strategy_tag(t, p)
            }

        problem["id"] = idx
        problem["letter"] = letter
        problem["is_bonus"] = False
        letter_to_problem[letter] = problem
        problems.append(problem)

    # 2. In Full-Page mode, fill remaining slots up to target_problem_count with Bonus Practice Facts!
    bonus_labels = ["★", "✦", "◆", "▲", "●", "■"]
    while len(problems) < target_problem_count:
        b_idx = len(problems) - coded_letter_count
        b_label = bonus_labels[b_idx % len(bonus_labels)]
        prob = generate_multiplication_problem(
            target_numbers=target_numbers,
            include_missing_factors=include_missing_factors,
            orientation=orientation,
            differentiation_level=differentiation_level,
            rng=rng
        )
        prob["id"] = len(problems) + 1
        prob["letter"] = b_label
        prob["is_bonus"] = True
        problems.append(prob)

    # 3. Build blank slots for the punchline
    punchline_structure = []
    for word in words:
        word_structure = []
        for char in word:
            if char.isalpha():
                if char in letter_to_problem:
                    code_val = letter_to_problem[char]["answer"]
                    word_structure.append({
                        "char": char,
                        "is_alpha": True,
                        "code": code_val,
                        "prefilled": False
                    })
                else:
                    word_structure.append({
                        "char": char,
                        "is_alpha": True,
                        "code": char,
                        "prefilled": True
                    })
            else:
                word_structure.append({
                    "char": char,
                    "is_alpha": False,
                    "code": char,
                    "prefilled": True
                })
        punchline_structure.append(word_structure)

    # 4. Scaffolds and Extensions metadata
    extension_challenge = None
    scaffold_support = None
    if not is_half_page:
        if differentiation_level == "extension":
            extension_challenge = generate_extension_challenge(target_numbers, rng)
        elif differentiation_level == "scaffold":
            scaffold_support = generate_scaffold_support(target_numbers)

    return {
        "type": "riddle",
        "joke_id": selected_joke["id"],
        "category": selected_joke["category"],
        "question": selected_joke["question"],
        "punchline": punchline,
        "problems": problems,
        "punchline_structure": punchline_structure,
        "is_half_page": is_half_page,
        "differentiation_level": differentiation_level,
        "extension_challenge": extension_challenge,
        "scaffold_support": scaffold_support,
        "show_thinking": (not is_half_page and differentiation_level == "core")
    }
