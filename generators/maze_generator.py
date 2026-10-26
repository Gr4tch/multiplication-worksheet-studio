"""
Multiples Pathfinder Maze Generator.
Generates an algorithmic path-finding maze with guaranteed solvable route.
Supports Grade 2 scaffolds, Grade 3 core, and Grade 4 extensions.
"""

import random
from typing import List, Dict, Any, Optional
from generators.math_engine import generate_extension_challenge, generate_scaffold_support

def generate_maze_path(rows: int, cols: int, rng: random.Random) -> List[tuple]:
    """Generates a random self-avoiding path from (0,0) to (rows-1, cols-1)."""
    current = (0, 0)
    target = (rows - 1, cols - 1)
    path = [current]
    visited = {current}
    
    while current != target:
        r, c = current
        possible_moves = [(r + 1, c), (r, c + 1), (r - 1, c), (r, c - 1)]
        
        valid_moves = []
        for nr, nc in possible_moves:
            if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in visited:
                valid_moves.append((nr, nc))
                
        if not valid_moves:
            if len(path) > 1:
                path.pop()
                current = path[-1]
                continue
            else:
                return generate_maze_path(rows, cols, rng)
                
        valid_moves.sort(key=lambda pos: abs(pos[0] - target[0]) + abs(pos[1] - target[1]))
        if len(valid_moves) > 1 and rng.random() < 0.25:
            next_step = valid_moves[1]
        else:
            next_step = valid_moves[0]
            
        visited.add(next_step)
        path.append(next_step)
        current = next_step
        
    return path

def build_maze_puzzle(
    target_numbers: List[int],
    is_half_page: bool = False,
    differentiation_level: str = "core",
    seed: Optional[int] = None
) -> Dict[str, Any]:
    """Builds a complete Pathfinder Maze puzzle."""
    rng = random.Random(seed)
    
    rows = 5 if is_half_page else 7
    cols = 5 if is_half_page else 7
    
    path_coords = generate_maze_path(rows, cols, rng)
    path_set = set(path_coords)
    
    all_numbers = list(range(1, 13))
    decoy_numbers = [n for n in all_numbers if n not in target_numbers]
    if not decoy_numbers:
        decoy_numbers = [n for n in all_numbers if n != target_numbers[0]]
        
    grid = []
    solution_grid = []
    
    for r in range(rows):
        row_cells = []
        sol_row = []
        for c in range(cols):
            if (r, c) in path_set:
                t = rng.choice(target_numbers)
                other = rng.randint(1, 10 if differentiation_level == "scaffold" else 12)
                if rng.choice([True, False]):
                    text = f"{t} × {other}"
                else:
                    text = f"{other} × {t}"
                row_cells.append({"text": text, "is_path": True, "r": r, "c": c})
                sol_row.append(1)
            else:
                d1 = rng.choice(decoy_numbers)
                d2 = rng.choice([n for n in decoy_numbers if n != d1] or decoy_numbers)
                text = f"{d1} × {d2}"
                row_cells.append({"text": text, "is_path": False, "r": r, "c": c})
                sol_row.append(0)
        grid.append(row_cells)
        solution_grid.append(sol_row)
        
    targets_str = ", ".join(str(n) for n in target_numbers)
    
    extension_challenge = None
    scaffold_support = None
    if not is_half_page:
        if differentiation_level == "extension":
            extension_challenge = generate_extension_challenge(target_numbers, rng)
        elif differentiation_level == "scaffold":
            scaffold_support = generate_scaffold_support(target_numbers)

    return {
        "type": "maze",
        "title": "Multiples Pathfinder Maze",
        "instructions": f"Help Astro navigate the maze from START to FINISH! Color only the squares that multiply by {targets_str}.",
        "rows": rows,
        "cols": cols,
        "grid": grid,
        "solution_grid": solution_grid,
        "path_coords": path_coords,
        "targets_str": targets_str,
        "is_half_page": is_half_page,
        "differentiation_level": differentiation_level,
        "extension_challenge": extension_challenge,
        "scaffold_support": scaffold_support,
        "checkpoint_prompt": (not is_half_page and differentiation_level == "core")
    }
