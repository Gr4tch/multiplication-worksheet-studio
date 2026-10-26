"""
Riddle / Secret Code Generator for Multiplication Practice.
Maps unique letters of verified kid-friendly jokes to math facts.
"""

import json
import random
from pathlib import Path
from typing import Dict, Any, List, Optional
from generators.math_engine import generate_multiplication_problem, get_strategy_tag

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
    seed: Optional[int] = None
) -> Dict[str, Any]:
    """
    Builds a complete Riddle / Secret Code puzzle.
    Guarantees that each coded letter maps to a UNIQUE answer code.
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
    max_problems = 8 if is_half_page else 14
    min_problems = 6 if is_half_page else 10
    
    target_problem_count = min(len(unique_letters), max_problems)
    if target_problem_count < min_problems and len(unique_letters) >= min_problems:
        target_problem_count = min_problems

    # Select the letters to be solved by math problems
    coded_letters = unique_letters[:target_problem_count]
    free_letters = unique_letters[target_problem_count:] # letters pre-filled if any

    # Generate unique multiplication problems for each coded letter
    letter_to_problem = {}
    used_answers = set()
    used_factor_pairs = set()
    problems = []

    for idx, letter in enumerate(coded_letters, 1):
        # Find a problem with a unique answer
        attempts = 0
        problem = None
        while attempts < 100:
            prob = generate_multiplication_problem(
                target_numbers=target_numbers,
                include_missing_factors=include_missing_factors,
                orientation=orientation,
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
            # Fallback: allow duplicate factor pair if answer is unique
            for p in range(0, 13):
                t = rng.choice(target_numbers)
                ans = t * p
                if ans not in used_answers:
                    used_answers.add(ans)
                    problem = {
                        "factor1": t,
                        "factor2": p,
                        "product": ans,
                        "missing_pos": "product",
                        "answer": ans,
                        "prompt_str": f"{t} × {p} = ____",
                        "display_orientation": orientation if orientation != "mixed" else "horizontal",
                        "strategy": get_strategy_tag(t, p)
                    }
                    break

        problem["id"] = idx
        problem["letter"] = letter
        letter_to_problem[letter] = problem
        problems.append(problem)

    # Build blank slots for the punchline
    # Each slot: {"char": 'E', "is_alpha": True, "code": 24, "prefilled": False}
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

    return {
        "type": "riddle",
        "joke_id": selected_joke["id"],
        "category": selected_joke["category"],
        "question": selected_joke["question"],
        "punchline": punchline,
        "problems": problems,
        "punchline_structure": punchline_structure,
        "is_half_page": is_half_page
    }
