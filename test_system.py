"""
Verification test for Intelligent Newton Math Fact Generator.
Validates all data files, generators, and ReportLab PDF outputs.
"""

import json
from pathlib import Path
from generators.math_engine import generate_fact_set, get_strategy_tag
from generators.riddle_generator import build_riddle_puzzle, load_jokes
from generators.detective_generator import build_detective_puzzle
from generators.maze_generator import build_maze_puzzle
from export.pdf_engine import create_worksheet_pdf

def test_data():
    print("Testing data files...")
    jokes = load_jokes()
    assert len(jokes) >= 30, f"Expected 30+ jokes, found {len(jokes)}"
    print(f"[OK] Loaded {len(jokes)} curated jokes.")

def test_math_engine():
    print("Testing math engine...")
    facts = generate_fact_set(target_numbers=[3, 4], count=10, include_missing_factors=True)
    assert len(facts) == 10
    for f in facts:
        assert f["factor1"] in [3, 4] or f["factor2"] in [3, 4]
    print("[OK] Math engine generated 10 valid target facts.")

def test_riddle_generator():
    print("Testing riddle generator...")
    riddle = build_riddle_puzzle(target_numbers=[6, 7], is_half_page=False)
    assert len(riddle["problems"]) >= 6
    assert len(riddle["punchline"]) > 0
    print(f"[OK] Riddle puzzle generated: '{riddle['question']}' -> {len(riddle['problems'])} problems.")

def test_detective_generator():
    print("Testing detective generator...")
    det = build_detective_puzzle(target_numbers=[8, 9], is_half_page=False)
    assert len(det["problems"]) == 12
    errors = [p for p in det["problems"] if p["is_error"]]
    assert len(errors) == det["target_error_count"]
    print(f"[OK] Sneaky Pete generated with {len(errors)} authentic errors.")

def test_maze_generator():
    print("Testing maze generator...")
    maze = build_maze_puzzle(target_numbers=[5], is_half_page=False)
    assert len(maze["path_coords"]) > 0
    assert maze["path_coords"][0] == (0, 0)
    assert maze["path_coords"][-1] == (maze["rows"]-1, maze["cols"]-1)
    print(f"[OK] Maze generated with solvable path length {len(maze['path_coords'])}.")

def test_pdf_engine():
    print("Testing PDF creation...")
    # Test 1: Full Page Riddle
    riddle = build_riddle_puzzle(target_numbers=[4, 8], is_half_page=False)
    pdf1 = create_worksheet_pdf(puzzle_data=riddle, layout_mode="full_page", include_answer_key=True)
    assert len(pdf1) > 1000, "PDF byte stream too small"
    
    # Test 2: Half Page Twin Detective
    det = build_detective_puzzle(target_numbers=[3], is_half_page=True)
    pdf2 = create_worksheet_pdf(puzzle_data=det, layout_mode="half_page_twin", include_answer_key=True)
    assert len(pdf2) > 1000
    
    # Test 3: Half Page A/B Maze
    maze_a = build_maze_puzzle(target_numbers=[7], is_half_page=True, seed=123)
    maze_b = build_maze_puzzle(target_numbers=[7], is_half_page=True, seed=456)
    pdf3 = create_worksheet_pdf(puzzle_data=maze_a, form_b_data=maze_b, layout_mode="half_page_ab", include_answer_key=True)
    assert len(pdf3) > 1000
    
    print(f"[OK] Generated 3 PDF files successfully (sizes: {len(pdf1)} bytes, {len(pdf2)} bytes, {len(pdf3)} bytes).")

if __name__ == "__main__":
    test_data()
    test_math_engine()
    test_riddle_generator()
    test_detective_generator()
    test_maze_generator()
    test_pdf_engine()
    print("\nALL 6 VERIFICATION SUITES PASSED PERFECTLY!")
