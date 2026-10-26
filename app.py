"""
Multiplication Worksheet Studio
Grade 3 Math Fact Practice Generator aligned with WA CCSS-M and Clear Math.
Optimized for classroom printing and Streamlit Community Cloud hosting.
"""

import json
import random
from pathlib import Path
import streamlit as st

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

# 2. Activity Type
st.sidebar.subheader("2. Engaging Practice Format")
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

# 3. Layout Mode
st.sidebar.subheader("3. Paper & Layout")
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

# 4. Math & Equation Settings
st.sidebar.subheader("4. Problem Options")
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
    help="WA CCSS 3.OA.A.4 algebraic unknown factor practice"
)

include_strategy_box = st.sidebar.checkbox(
    "Include Clear Math Strategy Helper Box",
    value=True,
    help="Prints a conceptual hint or visual anchor for struggling learners"
)

# 5. Typography & Title
st.sidebar.subheader("5. Appearance & Text")
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

# Retrieve Primary Strategy for selected numbers
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
        seed=st.session_state["seed_a"]
    )
    puzzle_data_b = build_riddle_puzzle(
        target_numbers=target_nums,
        category=selected_category,
        is_half_page=is_half_page,
        include_missing_factors=include_missing,
        orientation=orientation_val,
        seed=st.session_state["seed_b"]
    )
elif activity_type == "Math Detective: Sneaky Pete's Error Hunt":
    puzzle_data_a = build_detective_puzzle(
        target_numbers=target_nums,
        is_half_page=is_half_page,
        orientation=orientation_val,
        seed=st.session_state["seed_a"]
    )
    puzzle_data_b = build_detective_puzzle(
        target_numbers=target_nums,
        is_half_page=is_half_page,
        orientation=orientation_val,
        seed=st.session_state["seed_b"]
    )
else: # Maze
    puzzle_data_a = build_maze_puzzle(
        target_numbers=target_nums,
        is_half_page=is_half_page,
        seed=st.session_state["seed_a"]
    )
    puzzle_data_b = build_maze_puzzle(
        target_numbers=target_nums,
        is_half_page=is_half_page,
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
    font_choice="Helvetica"
)

# --- MAIN DISPLAY PANEL ---
# Header Action Bar
top_cols = st.columns([3, 1, 1])
with top_cols[0]:
    st.title("🖨️ Multiplication Fact Studio")
    st.markdown(
        f"**Target Numbers:** `{', '.join(str(n) for n in target_nums)}` | "
        f"**Format:** `{activity_type}` | **Layout:** `{layout_choice}`"
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
# Load CSS font
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
        <div style="text-align: center; margin-bottom: 12px;">
            <h2 style="margin: 0; font-size: 20px; text-transform: uppercase; letter-spacing: 0.5px;">{custom_title} {form_label}</h2>
        </div>
    """
    
    # Strategy Hint Box
    if include_strategy_box and strategy_info:
        html += f"""
        <div style="border: 1.5px solid #000; background: #fdfdfd; padding: 8px 12px; border-radius: 4px; margin-bottom: 14px; font-size: 12px;">
            <strong>💡 Clear Math Strategy Tip:</strong> {strategy_info.get('student_tip', '')}<br/>
            <strong>📐 Visual Anchor:</strong> {strategy_info.get('visual_hint', '')}
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
            if p.get("display_orientation") == "vertical":
                vert_html = f"""
                <div style="display: inline-block; text-align: right; border-bottom: 1.5px solid #000; padding-right: 6px; width: 35px; line-height: 1.1;">
                    {p['factor1']}<br/>× {p['factor2']}
                </div>
                """
                html += f"""
                <div style="display: flex; align-items: center; gap: 8px; font-size: 14px; font-weight: bold; padding: 4px 0;">
                    <span style="background: #000; color: #fff; padding: 2px 7px; border-radius: 3px; font-size: 13px;">{p['letter']}</span>
                    {vert_html} <span style="font-size: 15px;">= _____</span>
                </div>
                """
            else:
                html += f"""
                <div style="display: flex; align-items: center; gap: 8px; font-size: 14px; font-weight: bold; padding: 4px 0;">
                    <span style="background: #000; color: #fff; padding: 2px 7px; border-radius: 3px; font-size: 13px;">{p['letter']}</span>
                    <span>{p['prompt_str']}</span>
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
            html += f"""
            <tr style="border-bottom: 1px solid #000;">
                <td style="border: 1px solid #000; padding: 6px; text-align: center; font-weight: bold;">{p['id']}</td>
                <td style="border: 1px solid #000; padding: 6px; font-size: 14px; font-weight: bold;">{eq_str}</td>
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
                <td style="border: 1.5px solid #000; width: 62px; height: 54px; text-align: center; vertical-align: middle; font-weight: bold; font-size: 12px; padding: 4px;">
                    {badge}
                    <div>{cell['text']}</div>
                </td>
                """
            html += "</tr>"
        html += """
            </table>
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

st.components.v1.html(preview_html, height=1100, scrolling=True)

# --- EXPANDABLE SECTIONS: ANSWER KEY & STANDARDS ---
col_exp1, col_exp2 = st.columns(2)

with col_exp1:
    with st.expander("🔑 Teacher Answer Key & Solution Notes", expanded=False):
        def render_ak_ui(p_data, label: str):
            if label:
                st.markdown(f"#### {label}")
            ptype = p_data.get("type")
            if ptype == "riddle":
                st.markdown(f"**Question:** *{p_data.get('question')}*")
                st.markdown(f"**Solved Punchline:** `{p_data.get('punchline')}`")
                st.table([
                    {
                        "Letter": p.get("letter"),
                        "Equation": f"{p['factor1']} × {p['factor2']} = {p['product']}",
                        "Code Value": p.get("answer"),
                        "Strategy": p.get("strategy")
                    }
                    for p in p_data.get("problems", [])
                ])
            elif ptype == "detective":
                st.markdown("**Sneaky Pete Error Analysis:**")
                st.table([
                    {
                        "#": p["id"],
                        "Pete's Equation": f"{p['factor1']} × {p['factor2']} = {p['displayed_answer']}",
                        "Verdict": "MISTAKE" if p["is_error"] else "CORRECT",
                        "True Product": p["correct_answer"],
                        "Misconception / Reasoning": p["error_reason"]
                    }
                    for p in p_data.get("problems", [])
                ])
            else:
                st.markdown(f"**Pathfinder Coordinates (Row, Col):** `{p_data.get('path_coords')}`")

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
        st.markdown("### Washington State Math Standards Aligned:")
        st.markdown("- **3.OA.A.1**: Interpret products of whole numbers as equal groups.")
        st.markdown("- **3.OA.A.4**: Determine unknown whole numbers in multiplication equations.")
        st.markdown("- **3.OA.B.5**: Apply properties of operations (Distributive, Commutative).")
        st.markdown("- **3.OA.C.7**: Fluently multiply within 100.")
        st.markdown("---")
        st.markdown("### Scaffolding & Extensions in Knowledge Base:")
        st.markdown("- **Grade 2 Bridge (2.OA.C.4)**: Equal groups and arrays.")
        st.markdown("- **Grade 4 Extension (4.OA.A.1, 4.NBT.B.5)**: Multiplicative comparison and area models.")
