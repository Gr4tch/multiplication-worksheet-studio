"""
Multiplication Worksheet Studio
Grade 3 Math Fact Practice Generator aligned with WA CCSS-M and Clear Math.
Supports Grade 2 Scaffolds (2.OA.C.4), Grade 3 Core (3.OA.A.1-C.7), and Grade 4 Extensions (4.OA.A.1).
Optimized for classroom printing and Streamlit Community Cloud hosting.
"""

import json
import random
import importlib
from pathlib import Path
import streamlit as st

import generators.math_engine as math_engine_mod
import generators.riddle_generator as riddle_mod
import generators.detective_generator as detective_mod
import generators.maze_generator as maze_mod
import export.pdf_engine as pdf_mod

# Ensure hot-reloading in Streamlit Community Cloud without cached module stales
importlib.reload(math_engine_mod)
importlib.reload(riddle_mod)
importlib.reload(detective_mod)
importlib.reload(maze_mod)
importlib.reload(pdf_mod)

from generators.math_engine import get_strategy_tag
from generators.riddle_generator import build_riddle_puzzle, get_jokes_by_category
from generators.detective_generator import build_detective_puzzle
from generators.maze_generator import build_maze_puzzle
from export.pdf_engine import create_worksheet_pdf

DATA_DIR = Path(__file__).resolve().parent / "data"

# Page Config
st.set_page_config(
    page_title="Multiplication Worksheet Studio",
    page_icon="✏️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load Standards and Strategies
@st.cache_data
def load_standards():
    with open(DATA_DIR / "wa_ccss_math.json", "r", encoding="utf-8") as f:
        return json.load(f)

@st.cache_data
def load_strategies():
    with open(DATA_DIR / "clear_math_strategies.json", "r", encoding="utf-8") as f:
        return json.load(f)

standards_db = load_standards()
strategies_db = load_strategies()

# Session State Initialization
if "seed_a" not in st.session_state:
    st.session_state["seed_a"] = random.randint(1000, 9999)
if "seed_b" not in st.session_state:
    st.session_state["seed_b"] = random.randint(10000, 99999)
if "active_joke_id" not in st.session_state:
    st.session_state["active_joke_id"] = None
if "selected_numbers" not in st.session_state:
    st.session_state["selected_numbers"] = [3, 4, 6]

# --- SIDEBAR CONTROLS ---
st.sidebar.title("✏️ Fact Studio Settings")
st.sidebar.caption("Grade 3 Multiplication Practice aligned to WA CCSS-M & Clear Math")

# 1. Preset Strategies Quick Select
st.sidebar.subheader("1. Clear Math Target Numbers")
preset_options = list(strategies_db["preset_clusters"].keys())
selected_preset = st.sidebar.selectbox("Choose a Strategy Preset:", ["-- Custom Selection --"] + preset_options)

if selected_preset != "-- Custom Selection --":
    st.session_state["selected_numbers"] = strategies_db["preset_clusters"][selected_preset]

# Number Checkboxes (0 to 12)
cols_nums = st.sidebar.columns(4)
current_selected = []
for idx, num in enumerate(range(0, 13)):
    with cols_nums[idx % 4]:
        checked = num in st.session_state["selected_numbers"]
        if st.checkbox(str(num), value=checked, key=f"num_chk_{num}"):
            current_selected.append(num)

st.session_state["selected_numbers"] = current_selected if current_selected else [3, 4]

# 2. Differentiation Level (Scaffolds & Extensions)
st.sidebar.subheader("2. Differentiation & Standards Level")
diff_level_choice = st.sidebar.radio(
    "Choose Level:",
    [
        "🟡 Core Practice (Grade 3 On-Level)",
        "🟢 Visual Support (Equal Groups & Repeated Addition)",
        "🟣 Star Challenge (Comparison Word Problems)"
    ]
)

diff_code = "core"
if "Grade 2" in diff_level_choice:
    diff_code = "scaffold"
elif "Grade 4" in diff_level_choice:
    diff_code = "extension"

# 3. Activity Type
st.sidebar.subheader("3. Engaging Practice Format")
activity_type = st.sidebar.radio(
    "Choose Student Activity:",
    [
        "Secret Code Riddle Decoder",
        "Math Detective: Sneaky Pete's Error Hunt",
        "Multiples Pathfinder Maze"
    ]
)

# Sub-options for Riddle
selected_category = "All"
if activity_type == "Secret Code Riddle Decoder":
    cat_cols = st.sidebar.columns([2, 1])
    with cat_cols[0]:
        selected_category = st.selectbox(
            "Joke Category:",
            ["All", "Animals", "School", "Food", "Science", "Silly Puns"]
        )
    with cat_cols[1]:
        st.write("")
        st.write("")
        if st.button("🔀 Shuffle", help="Pick another verified joke"):
            st.session_state["seed_a"] = random.randint(1000, 9999)
            st.session_state["seed_b"] = random.randint(10000, 99999)
            candidates = get_jokes_by_category(selected_category)
            if candidates:
                st.session_state["active_joke_id"] = random.choice(candidates)["id"]
            st.rerun()

# 4. Layout Mode
st.sidebar.subheader("4. Paper & Layout")
layout_choice = st.sidebar.radio(
    "Worksheet Layout:",
    [
        "Full Page (1-Up)",
        "Paper-Saver Half-Page (2-Up Twin Copies)",
        "Paper-Saver Half-Page (2-Up Form A & B Anti-Peeking)"
    ]
)

is_half_page = "Half-Page" in layout_choice
layout_code = "full_page"
if "Twin" in layout_choice:
    layout_code = "half_page_twin"
elif "Form A & B" in layout_choice:
    layout_code = "half_page_ab"

# Problem Density Slider
default_count = 8 if is_half_page else 14
problem_count = st.sidebar.slider(
    "Number of Problems:",
    min_value=6 if is_half_page else 10,
    max_value=10 if is_half_page else 18,
    value=default_count,
    step=2,
    help="Adjust problem density to fit class time"
)

# 5. Math & Equation Settings
st.sidebar.subheader("5. Problem Options")
orientation_opt = st.sidebar.selectbox(
    "Equation Orientation:",
    ["Horizontal (7 × 8 = ____)", "Vertical / Stacked", "Mixed"]
)
orientation_val = "horizontal"
if "Vertical" in orientation_opt:
    orientation_val = "vertical"
elif "Mixed" in orientation_opt:
    orientation_val = "mixed"

include_missing = st.sidebar.checkbox(
    "Include Missing Factors (e.g. 7 × ____ = 56)",
    value=False,
    disabled=(diff_code == "scaffold"),
    help="WA CCSS 3.OA.A.4 algebraic unknown factor practice"
)

include_strategy_box = st.sidebar.checkbox(
    "Include Clear Math Strategy Helper Box",
    value=True,
    help="Prints an enthusiastic kid-friendly hint with a concrete skip-counting track"
)

# 6. Typography & Title
st.sidebar.subheader("6. Appearance & Text")
font_choice = st.sidebar.selectbox(
    "Student-Friendly Font:",
    ["Lexend (Dyslexia & Flow Friendly)", "Comic Neue (Elementary Print)", "Inter (Clean Sans)"]
)
font_family = "Lexend"
if "Comic" in font_choice:
    font_family = "Comic Neue"
elif "Inter" in font_choice:
    font_family = "Inter"

default_titles = {
    "Secret Code Riddle Decoder": "The Secret Code Mission",
    "Math Detective: Sneaky Pete's Error Hunt": "Sneaky Pete's Homework Hunt",
    "Multiples Pathfinder Maze": "Multiples Pathfinder Expedition"
}
custom_title = st.sidebar.text_input(
    "Worksheet Title:",
    value=default_titles[activity_type]
)

include_answer_key = st.sidebar.checkbox("Include Teacher Answer Key", value=True)

# Generate Puzzle Data
target_nums = st.session_state["selected_numbers"]
primary_strat_key = str(target_nums[0]) if target_nums else "3"
strategy_info = strategies_db["strategies"].get(primary_strat_key, {})

if activity_type == "Secret Code Riddle Decoder":
    puzzle_data_a = build_riddle_puzzle(
        target_numbers=target_nums,
        joke_id=st.session_state.get("active_joke_id"),
        category=selected_category,
        is_half_page=is_half_page,
        include_missing_factors=include_missing,
        orientation=orientation_val,
        differentiation_level=diff_code,
        problem_count_override=problem_count,
        seed=st.session_state["seed_a"]
    )
    puzzle_data_b = build_riddle_puzzle(
        target_numbers=target_nums,
        category=selected_category,
        is_half_page=is_half_page,
        include_missing_factors=include_missing,
        orientation=orientation_val,
        differentiation_level=diff_code,
        problem_count_override=problem_count,
        seed=st.session_state["seed_b"]
    )
elif activity_type == "Math Detective: Sneaky Pete's Error Hunt":
    puzzle_data_a = build_detective_puzzle(
        target_numbers=target_nums,
        is_half_page=is_half_page,
        orientation=orientation_val,
        differentiation_level=diff_code,
        problem_count_override=problem_count,
        seed=st.session_state["seed_a"]
    )
    puzzle_data_b = build_detective_puzzle(
        target_numbers=target_nums,
        is_half_page=is_half_page,
        orientation=orientation_val,
        differentiation_level=diff_code,
        problem_count_override=problem_count,
        seed=st.session_state["seed_b"]
    )
else: # Maze
    puzzle_data_a = build_maze_puzzle(
        target_numbers=target_nums,
        is_half_page=is_half_page,
        differentiation_level=diff_code,
        seed=st.session_state["seed_a"]
    )
    puzzle_data_b = build_maze_puzzle(
        target_numbers=target_nums,
        is_half_page=is_half_page,
        differentiation_level=diff_code,
        seed=st.session_state["seed_b"]
    )

# Compile PDF
pdf_bytes = create_worksheet_pdf(
    puzzle_data=puzzle_data_a,
    form_b_data=puzzle_data_b if layout_code == "half_page_ab" else None,
    custom_title=custom_title,
    layout_mode=layout_code,
    include_strategy_box=include_strategy_box,
    strategy_info=strategy_info,
    include_answer_key=include_answer_key,
    differentiation_level=diff_code,
    font_choice="Helvetica"
)

# --- MAIN DISPLAY PANEL ---
top_cols = st.columns([3, 1, 1])
with top_cols[0]:
    st.title("🖨️ Multiplication Fact Studio")
    diff_badge = {"scaffold": "🟢 Grade 2 Scaffold", "core": "🟡 Grade 3 Core", "extension": "🟣 Grade 4 Extension"}[diff_code]
    st.markdown(
        f"**Target Numbers:** `{', '.join(str(n) for n in target_nums)}` | "
        f"**Level:** `{diff_badge}` | **Format:** `{activity_type}` | **Layout:** `{layout_choice}`"
    )

with top_cols[1]:
    st.download_button(
        label="📥 Download 8.5×11 PDF",
        data=pdf_bytes,
        file_name=f"multiplication_{activity_type.lower().replace(' ', '_')[:15]}.pdf",
        mime="application/pdf",
        use_container_width=True
    )

with top_cols[2]:
    if st.button("🔄 New Facts / Joke", use_container_width=True):
        st.session_state["seed_a"] = random.randint(1000, 9999)
        st.session_state["seed_b"] = random.randint(10000, 99999)
        st.session_state["active_joke_id"] = None
        st.rerun()

# --- HTML PREVIEW BUILDER ---
font_urls = {
    "Lexend": "https://fonts.googleapis.com/css2?family=Lexend:wght@400;500;600;700&display=swap",
    "Comic Neue": "https://fonts.googleapis.com/css2?family=Comic+Neue:wght@400;700&display=swap",
    "Inter": "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"
}

def render_html_worksheet(p_data, form_label=""):
    html = f"""
    <div style="font-family: '{font_family}', sans-serif; color: #000; padding: 18px 24px; border: 2px solid #000; border-radius: 6px; background: #fff; margin-bottom: 20px;">
        <!-- Header -->
        <div style="display: flex; justify-content: space-between; font-size: 13px; font-weight: bold; border-bottom: 1px solid #000; padding-bottom: 8px; margin-bottom: 12px;">
            <span>Name: ___________________________</span>
            <span>Class/Room: _______</span>
            <span>Date: _________</span>
        </div>
        
        <!-- Title -->
        <div style="text-align: center; margin-bottom: 10px;">
            <h2 style="margin: 0; font-size: 20px; text-transform: uppercase; letter-spacing: 0.5px;">{custom_title} {form_label}</h2>
        </div>
    """
    
    # Kid-Friendly Strategy Helper Box
    if include_strategy_box and strategy_info:
        kid_name = strategy_info.get("kid_title", "Clear Math Tip")
        tip = strategy_info.get("student_tip", "")
        skip_line = strategy_info.get("skip_count_line", "")
        
        html += f"""
        <div style="border: 1.5px solid #000; background: #fafafa; padding: 10px 14px; border-radius: 6px; margin-bottom: 14px; font-size: 13px;">
            <div style="font-weight: bold; font-size: 14px; margin-bottom: 4px;">{kid_name}</div>
            <div>{tip}</div>
            <div style="margin-top: 6px; font-size: 12px; background: #fff; border: 1px solid #ddd; padding: 4px 8px; border-radius: 4px;">
                <strong>👉 Skip-Counting Track:</strong> <span style="font-weight: bold; letter-spacing: 0.5px;">{skip_line}</span>
            </div>
        </div>
        """

    # Body Content by Puzzle Type
    ptype = p_data.get("type")
    if ptype == "riddle":
        html += f"""
        <div style="margin-bottom: 12px;">
            <p style="font-size: 14px; font-weight: bold; margin: 0 0 4px 0;">MISSION RIDDLE: <em>"{p_data.get('question')}"</em></p>
            <p style="font-size: 12px; color: #333; margin: 0;">Solve the facts below. Match the answers to the letter codes to decode the secret punchline!</p>
        </div>
        
        <!-- Problems Grid -->
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px 24px; margin-bottom: 16px;">
        """
        for p in p_data.get("problems", []):
            rep_hint_html = f"<div style='font-size: 11px; color: #555; margin-top: 2px;'>think: {p['repeated_addition_hint']}</div>" if p.get('repeated_addition_hint') else ""
            
            if p.get("display_orientation") == "vertical":
                vert_html = f"""
                <div style="display: inline-block; text-align: right; border-bottom: 1.5px solid #000; padding-right: 6px; width: 35px; line-height: 1.1;">
                    {p['factor1']}<br/>× {p['factor2']}
                </div>
                """
                html += f"""
                <div style="display: flex; align-items: center; gap: 8px; font-size: 14px; font-weight: bold; padding: 4px 0;">
                    <span style="background: #000; color: #fff; padding: 2px 7px; border-radius: 3px; font-size: 13px;">{p['letter']}</span>
                    <div>
                        <div style="display: flex; align-items: center; gap: 4px;">{vert_html} <span style="font-size: 15px;">= _____</span></div>
                        {rep_hint_html}
                    </div>
                </div>
                """
            else:
                html += f"""
                <div style="display: flex; align-items: center; gap: 8px; font-size: 14px; font-weight: bold; padding: 4px 0;">
                    <span style="background: #000; color: #fff; padding: 2px 7px; border-radius: 3px; font-size: 13px;">{p['letter']}</span>
                    <div>
                        <span>{p['prompt_str']}</span>
                        {rep_hint_html}
                    </div>
                </div>
                """
        html += """
        </div>
        
        <!-- Punchline Letter Blanks -->
        <div style="margin-top: 10px; padding: 12px; border: 1.5px dashed #000; border-radius: 6px; background: #fafafa;">
            <div style="font-size: 11px; font-weight: bold; text-transform: uppercase; margin-bottom: 8px;">Secret Punchline:</div>
            <div style="display: flex; flex-wrap: wrap; gap: 14px; justify-content: center;">
        """
        for word in p_data.get("punchline_structure", []):
            html += '<div style="display: flex; gap: 4px;">'
            for slot in word:
                if slot["is_alpha"]:
                    html += f"""
                    <div style="display: flex; flex-direction: column; align-items: center; width: 22px;">
                        <div style="height: 22px; width: 100%; border-bottom: 2px solid #000;"></div>
                        <span style="font-size: 10px; font-weight: bold; margin-top: 2px;">{slot['code']}</span>
                    </div>
                    """
                else:
                    html += f"""
                    <div style="display: flex; flex-direction: column; align-items: center; width: 12px; justify-content: flex-end;">
                        <span style="font-size: 14px; font-weight: bold;">{slot['char']}</span>
                        <div style="height: 12px;"></div>
                    </div>
                    """
            html += '</div>'
        html += """
            </div>
        </div>
        """

        # Full-Page Bottom Section
        if not is_half_page:
            if p_data.get("extension_challenge"):
                ext = p_data["extension_challenge"]
                html += f"""
                <div style="margin-top: 16px; padding: 12px 16px; border: 2px solid #000; border-radius: 6px; background: #fdfdfd;">
                    <div style="font-size: 13px; margin-bottom: 8px;">{ext['prompt']}</div>
                    <div style="font-size: 14px; font-weight: bold;">{ext['equation_blank']}</div>
                </div>
                """
            elif p_data.get("scaffold_support"):
                scaf = p_data["scaffold_support"]
                html += f"""
                <div style="margin-top: 16px; padding: 12px 16px; border: 1.5px solid #000; border-radius: 6px; background: #fdfdfd;">
                    <div style="font-weight: bold; font-size: 13px; margin-bottom: 4px;">{scaf['title']}</div>
                    <div style="font-size: 12px;"><strong>Visual Model:</strong> {scaf['dots_visual']}</div>
                    <div style="font-size: 12px; margin-top: 2px;"><strong>Repeated Addition:</strong> {scaf['repeated_addition_example']}</div>
                </div>
                """
            elif p_data.get("show_thinking"):
                html += """
                <div style="margin-top: 16px; padding: 12px 16px; border: 1.5px solid #000; border-radius: 6px; background: #fff;">
                    <div style="font-weight: bold; font-size: 13px;">🎨 SHOW YOUR THINKING:</div>
                    <div style="font-size: 12px; color: #444; margin-bottom: 8px;">Pick any fact from above. In the space below, sketch a <strong>rectangular array</strong> (rows × columns) to prove your answer!</div>
                    <div style="height: 70px; border: 1px dashed #999; border-radius: 4px; display: flex; align-items: center; justify-content: center; color: #888; font-size: 12px;">
                        [ Draw your array of dots or squares here ]
                    </div>
                </div>
                """

    elif ptype == "detective":
        html += f"""
        <div style="margin-bottom: 12px; font-size: 13px;">
            <strong>🕵️ DETECTIVE BRIEFING:</strong> {p_data.get('mission_brief')}
        </div>
        
        <table style="width: 100%; border-collapse: collapse; font-size: 13px;">
            <thead>
                <tr style="background: #f0f0f0; border: 1.5px solid #000;">
                    <th style="border: 1px solid #000; padding: 6px; text-align: center; width: 35px;">#</th>
                    <th style="border: 1px solid #000; padding: 6px; text-align: left;">Pete's Solved Equation</th>
                    <th style="border: 1px solid #000; padding: 6px; text-align: center; width: 180px;">Your Verdict</th>
                    <th style="border: 1px solid #000; padding: 6px; text-align: left; width: 200px;">True Product (if wrong)</th>
                </tr>
            </thead>
            <tbody>
        """
        for p in p_data.get("problems", []):
            eq_str = f"{p['factor1']} × {p['factor2']} = {p['displayed_answer']}"
            hint_str = f"<div style='font-size: 10px; color: #666;'>think: {p['repeated_addition_hint']}</div>" if p.get('repeated_addition_hint') else ""
            html += f"""
            <tr style="border-bottom: 1px solid #000;">
                <td style="border: 1px solid #000; padding: 6px; text-align: center; font-weight: bold;">{p['id']}</td>
                <td style="border: 1px solid #000; padding: 6px; font-size: 14px; font-weight: bold;">
                    {eq_str}
                    {hint_str}
                </td>
                <td style="border: 1px solid #000; padding: 6px; text-align: center;">
                    <span style="border: 1px solid #000; border-radius: 50%; display: inline-block; width: 14px; height: 14px; margin-right: 3px; vertical-align: middle;"></span> Correct &nbsp;&nbsp;
                    <span style="border: 1px solid #000; border-radius: 50%; display: inline-block; width: 14px; height: 14px; margin-right: 3px; vertical-align: middle;"></span> Mistake
                </td>
                <td style="border: 1px solid #000; padding: 6px;">___________________</td>
            </tr>
            """
        html += """
            </tbody>
        </table>
        """

        if not is_half_page:
            if p_data.get("extension_challenge"):
                ext = p_data["extension_challenge"]
                html += f"""
                <div style="margin-top: 16px; padding: 12px 16px; border: 2px solid #000; border-radius: 6px; background: #fdfdfd;">
                    <div style="font-size: 13px; margin-bottom: 8px;">{ext['prompt']}</div>
                    <div style="font-size: 14px; font-weight: bold;">{ext['equation_blank']}</div>
                </div>
                """
            elif p_data.get("case_notes_prompt"):
                html += """
                <div style="margin-top: 16px; padding: 12px 16px; border: 1.5px solid #000; border-radius: 6px; background: #fff;">
                    <div style="font-weight: bold; font-size: 13px;">📝 DETECTIVE CASE LOG (SMP 3 Reasoning):</div>
                    <div style="font-size: 12px; color: #444; margin-bottom: 8px;">Pick one of Pete's mistakes above (Problem #___). In the space below, explain <i>why</i> his answer was incorrect, and show how to solve it correctly:</div>
                    <div style="border-bottom: 1px solid #000; margin: 16px 0 8px 0;"></div>
                    <div style="border-bottom: 1px solid #000; margin: 16px 0 8px 0;"></div>
                </div>
                """

    elif ptype == "maze":
        html += f"""
        <div style="margin-bottom: 12px; font-size: 13px;">
            <strong>🚀 MAZE CHALLENGE:</strong> {p_data.get('instructions')}
        </div>
        <div style="display: flex; justify-content: center; margin: 16px 0;">
            <table style="border-collapse: collapse; border: 2.5px solid #000;">
        """
        grid = p_data.get("grid", [])
        for r_idx, row in enumerate(grid):
            html += "<tr>"
            for c_idx, cell in enumerate(row):
                badge = ""
                if r_idx == 0 and c_idx == 0:
                    badge = "<div style='font-size: 9px; font-weight: bold; background: #000; color: #fff; padding: 1px 3px; border-radius: 2px;'>START</div>"
                elif r_idx == len(grid) - 1 and c_idx == len(row) - 1:
                    badge = "<div style='font-size: 9px; font-weight: bold; background: #000; color: #fff; padding: 1px 3px; border-radius: 2px;'>FINISH</div>"
                html += f"""
                <td style="border: 1.5px solid #000; width: 62px; height: 50px; text-align: center; vertical-align: middle; font-weight: bold; font-size: 12px; padding: 4px;">
                    {badge}
                    <div>{cell['text']}</div>
                </td>
                """
            html += "</tr>"
        html += """
            </table>
        </div>
        """

        if not is_half_page:
            if p_data.get("extension_challenge"):
                ext = p_data["extension_challenge"]
                html += f"""
                <div style="margin-top: 16px; padding: 12px 16px; border: 2px solid #000; border-radius: 6px; background: #fdfdfd;">
                    <div style="font-size: 13px; margin-bottom: 8px;">{ext['prompt']}</div>
                    <div style="font-size: 14px; font-weight: bold;">{ext['equation_blank']}</div>
                </div>
                """
            elif p_data.get("checkpoint_prompt"):
                html += """
                <div style="margin-top: 16px; padding: 12px 16px; border: 1.5px solid #000; border-radius: 6px; background: #fff;">
                    <div style="font-weight: bold; font-size: 13px;">🏁 MULTIPLES CHECKPOINT:</div>
                    <div style="font-size: 12px; color: #444; margin-bottom: 8px;">List 5 multiples you discovered along your path from lowest to highest:</div>
                    <div style="display: flex; gap: 14px; justify-content: space-around; font-size: 13px; font-weight: bold;">
                        <span>1) _______</span><span>2) _______</span><span>3) _______</span><span>4) _______</span><span>5) _______</span>
                    </div>
                </div>
                """

    html += "</div>"
    return html

# Render Preview on Streamlit
preview_html = f"""
<link rel="stylesheet" href="{font_urls.get(font_family, '')}">
<div style="max-width: 820px; margin: 0 auto;">
"""

if layout_code == "full_page":
    preview_html += render_html_worksheet(puzzle_data_a)
elif layout_code == "half_page_twin":
    preview_html += render_html_worksheet(puzzle_data_a, "(Copy 1)")
    preview_html += """
    <div style="border-top: 2px dashed #000; text-align: center; margin: 18px 0; position: relative;">
        <span style="position: absolute; top: -10px; left: 50%; transform: translateX(-50%); background: #fff; padding: 0 10px; font-weight: bold; font-size: 11px;">✂ CUT HERE (TWIN COPIES) ✂</span>
    </div>
    """
    preview_html += render_html_worksheet(puzzle_data_a, "(Copy 2)")
else: # half_page_ab
    preview_html += render_html_worksheet(puzzle_data_a, "(Form A)")
    preview_html += """
    <div style="border-top: 2px dashed #000; text-align: center; margin: 18px 0; position: relative;">
        <span style="position: absolute; top: -10px; left: 50%; transform: translateX(-50%); background: #fff; padding: 0 10px; font-weight: bold; font-size: 11px;">✂ CUT HERE (ANTI-PEEKING FORM A & B) ✂</span>
    </div>
    """
    preview_html += render_html_worksheet(puzzle_data_b, "(Form B)")

preview_html += "</div>"

st.components.v1.html(preview_html, height=1300 if not is_half_page else 1100, scrolling=True)

# --- EXPANDABLE SECTIONS: ANSWER KEY & STANDARDS ---
col_exp1, col_exp2 = st.columns(2)

with col_exp1:
    with st.expander("🔑 Teacher Answer Key & Solution Notes", expanded=False):
        def render_ak_ui(p_data, label: str):
            if label:
                st.markdown(f"#### {label}")
            ptype = p_data.get("type")
            if ptype == "riddle":
                st.markdown(f"**Riddle Question:** *"{p_data.get('question')}"*")
                st.success(f"**🎉 SOLVED PUNCHLINE:** `{p_data.get('punchline')}`")
                
                # Uncluttered 2-column answer key with coaching look-fors
                c_k1, c_k2 = st.columns(2)
                probs = p_data.get("problems", [])
                half = (len(probs) + 1) // 2
                
                with c_k1:
                    for p in probs[:half]:
                        hint = f" — *{p['repeated_addition_hint']}*" if p.get("repeated_addition_hint") else ""
                        st.markdown(f"**[{p.get('letter')}]** `{p['factor1']} × {p['factor2']} =` **{p['product']}** {hint}")
                        st.caption(f"💡 {p.get('strategy', '')}")
                with c_k2:
                    for p in probs[half:]:
                        hint = f" — *{p['repeated_addition_hint']}*" if p.get("repeated_addition_hint") else ""
                        st.markdown(f"**[{p.get('letter')}]** `{p['factor1']} × {p['factor2']} =` **{p['product']}** {hint}")
                        st.caption(f"💡 {p.get('strategy', '')}")
                
                if p_data.get("show_thinking"):
                    st.markdown("---")
                    sample_fact = probs[0] if probs else {"factor1": 3, "factor2": 4, "product": 12}
                    s_r = min(sample_fact["factor1"], 4) or 3
                    s_c = min(sample_fact["factor2"], 6) or 4
                    dot_grid = "\n".join(["  ".join(["●"] * s_c) for _ in range(s_r)])
                    st.markdown(f"**🎨 Exemplar Array Model for `{sample_fact['factor1']} × {sample_fact['factor2']} = {sample_fact['product']}`:**")
                    st.code(f"{dot_grid}\n\nStructure: {s_r} Rows × {s_c} Columns = {sample_fact['product']} total\nTeacher Look-For: Verify straight rows and columns (equal groups), not a scattered cluster.")

            elif ptype == "detective":
                st.markdown("**🕵️ Sneaky Pete Mistake Key & Misconception Analysis:**")
                st.table([
                    {
                        "#": p["id"],
                        "Pete's Equation": f"{p['factor1']} × {p['factor2']} = {p['displayed_answer']}",
                        "Verdict": "✗ MISTAKE" if p["is_error"] else "✓ Correct",
                        "True Product": p["correct_answer"],
                        "Misconception / Reasoning": p["error_reason"]
                    }
                    for p in p_data.get("problems", [])
                ])
                if p_data.get("case_notes_prompt"):
                    st.markdown("**📝 Case Log Exemplar:**")
                    st.info("*"Problem #4: Pete wrote 6 × 4 = 10 because he added 6 + 4. To multiply, he needed 4 groups of 6, which equals 24 (double 6 is 12, double 12 is 24)."*")
            else:
                st.markdown(f"**🚀 Pathfinder Coordinates (Row, Col):** `{p_data.get('path_coords')}`")
                if p_data.get("checkpoint_prompt"):
                    st.markdown(f"**🏁 Multiples Checkpoint Exemplar:** Multiples of {p_data.get('targets_str')} (e.g. 4, 8, 12, 16, 20).")

            if p_data.get("extension_challenge"):
                st.success(f"⭐ **Star Challenge Key:** {p_data['extension_challenge']['solution']} (WA CCSS 4.OA.A.1)")
            elif p_data.get("scaffold_support"):
                st.info(f"🌱 **Visual Support Exemplar:** {p_data['scaffold_support']['repeated_addition_example']} (WA CCSS 2.OA.C.4)")

        if layout_code == "half_page_ab":
            tab_a, tab_b = st.tabs(["Form A (Top Half)", "Form B (Bottom Half)"])
            with tab_a:
                render_ak_ui(puzzle_data_a, "Form A Solution Key")
            with tab_b:
                render_ak_ui(puzzle_data_b, "Form B Solution Key")
        elif layout_code == "half_page_twin":
            st.info("ℹ️ Twin Copies Mode: Copy 1 and Copy 2 are identical.")
            render_ak_ui(puzzle_data_a, "Twin Copies Answer Key")
        else:
            render_ak_ui(puzzle_data_a, "")

with col_exp2:
    with st.expander("📐 WA CCSS-M Standards & Clear Math Pacing", expanded=False):
        st.markdown(f"### Currently Active: **{diff_badge}**")
        if diff_code == "scaffold":
            st.markdown("- **WA CCSS 2.OA.C.4**: Use addition to find total objects arranged in rectangular arrays; write equations as sums of equal addends.")
            st.markdown("- **WA CCSS 2.NBT.A.2**: Skip-count by 2s, 5s, and 10s.")
            st.markdown("- **Clear Math CPA Model**: Concrete Equal Groups $\\rightarrow$ Representational Skip-Counting.")
        elif diff_code == "extension":
            st.markdown("- **WA CCSS 4.OA.A.1**: Interpret a multiplication equation as a multiplicative comparison (e.g., $n$ times as many).")
            st.markdown("- **WA CCSS 4.OA.A.2**: Multiply or divide to solve comparison word problems.")
            st.markdown("- **WA CCSS 4.NBT.B.5**: Multi-digit and multi-step multiplication strategies.")
        else:
            st.markdown("- **WA CCSS 3.OA.A.1**: Interpret products of whole numbers as equal groups.")
            st.markdown("- **WA CCSS 3.OA.A.4**: Determine unknown whole numbers in multiplication equations.")
            st.markdown("- **WA CCSS 3.OA.B.5**: Apply properties of operations (Distributive, Commutative).")
            st.markdown("- **WA CCSS 3.OA.C.7**: Fluently multiply within 100.")
