"""
ReportLab PDF Generation Engine for Printable Math Worksheets.
Generates vector-crisp, ink-friendly 8.5x11 B&W PDFs for school printing.
Matches preview canvas layout 1:1, fills Full-Page completely, and provides an Annotated Teacher Master Key (Option 3).
"""

import io
from typing import Dict, Any, List, Optional
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

def get_problem_look_for(p: Dict[str, Any]) -> str:
    """Generates an actionable Clear Math coaching prompt or misconception alert."""
    f1, f2 = p["factor1"], p["factor2"]
    prod = p["product"]
    strat = p.get("strategy", "")
    
    if (f1, f2) in [(7, 8), (8, 7)]:
        return "⚠️ Watch-for: 54 vs 56 slip. Tip: (5×8=40) + (2×8=16) = 56."
    if (f1, f2) in [(6, 7), (7, 6)]:
        return "💬 Tip: Friendly 5s fact (5×7=35) + 7 more = 42."
    if (f1, f2) in [(6, 8), (8, 6)]:
        return "💬 Tip: (5×8=40) + 8 = 48 (or double 24)."
    if (f1, f2) in [(7, 7)]:
        return "💬 Near 5s: (7×5=35) + (7×2=14) = 49."
    if (f1, f2) in [(8, 8)]:
        return "💬 Double-Double-Double: 8 → 16 → 32 → 64."
    if 4 in (f1, f2):
        other = f2 if f1 == 4 else f1
        return f"💡 Double-Double: Double {other} ({other*2}), double again ({prod})."
    if 3 in (f1, f2):
        other = f2 if f1 == 3 else f1
        return f"💡 Double+1: Double {other} ({other*2}), + {other} = {prod}."
    if 9 in (f1, f2):
        other = f2 if f1 == 9 else f1
        return f"💡 10 minus 1: (10×{other}={other*10}) - {other} = {prod}."
    if 6 in (f1, f2):
        other = f2 if f1 == 6 else f1
        return f"💡 5s fact + 1: (5×{other}) + {other} = {prod}."
    if 2 in (f1, f2):
        other = f2 if f1 == 2 else f1
        return f"💡 Double: {other} + {other} = {prod}."
    if 0 in (f1, f2):
        return "💥 Zap to Zero: 0 groups of anything is always 0."
    if 1 in (f1, f2):
        return "🪞 Mirror Rule: Multiplied by 1 stays the exact same."
    return f"💡 Strategy: {strat}"

def create_worksheet_pdf(
    puzzle_data: Dict[str, Any],
    form_b_data: Optional[Dict[str, Any]] = None,
    custom_title: Optional[str] = None,
    layout_mode: str = "full_page", # 'full_page', 'half_page_twin', 'half_page_ab'
    include_strategy_box: bool = True,
    strategy_info: Optional[Dict[str, Any]] = None,
    include_answer_key: bool = True,
    differentiation_level: str = "core",
    font_choice: str = "Helvetica",
    **kwargs
) -> bytes:
    """
    Generates a print-ready PDF byte stream matching preview styling 1:1.
    """
    buffer = io.BytesIO()
    
    margin = 0.35 * inch
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=margin,
        rightMargin=margin,
        topMargin=margin,
        bottomMargin=margin
    )
    
    printable_width = 612 - (2 * margin) # ~561.6 pt
    is_half_page = (layout_mode != "full_page")

    styles = getSampleStyleSheet()
    
    title_size = 12 if is_half_page else 15
    title_leading = 14 if is_half_page else 18
    body_size = 8 if is_half_page else 9
    body_leading = 10 if is_half_page else 12
    problem_size = 10 if is_half_page else 11
    problem_leading = 12 if is_half_page else 14

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=title_size,
        leading=title_leading,
        alignment=1,
        spaceAfter=2 if is_half_page else 4
    )
    
    header_style = ParagraphStyle(
        'DocHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=body_size,
        leading=body_leading
    )

    story_style = ParagraphStyle(
        'DocStory',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=body_size,
        leading=body_leading
    )
    
    problem_style = ParagraphStyle(
        'DocProblem',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=problem_size,
        leading=problem_leading
    )

    title_text = (custom_title or puzzle_data.get("title") or "Multiplication Fact Practice").upper()

    def build_punchline_table(struct: List[List[Dict[str, Any]]], max_width: float, prefill_letters: bool = False) -> List[Table]:
        slot_w = 20 if is_half_page else 24
        gap_w = 12 if is_half_page else 16
        
        lines = []
        current_line_words = []
        current_line_width = 0

        for word_slots in struct:
            word_w = len(word_slots) * slot_w
            needed = word_w if not current_line_words else word_w + gap_w
            if current_line_words and (current_line_width + needed > max_width):
                lines.append(current_line_words)
                current_line_words = [word_slots]
                current_line_width = word_w
            else:
                current_line_words.append(word_slots)
                current_line_width += needed

        if current_line_words:
            lines.append(current_line_words)

        tables = []
        for line_words in lines:
            col_widths = []
            row_letters = []
            row_codes = []
            underline_styles = []

            col_idx = 0
            for w_idx, word in enumerate(line_words):
                for slot in word:
                    col_widths.append(slot_w)
                    if slot["is_alpha"]:
                        # If teacher key: prefill letter in bold!
                        top_letter = slot["char"] if prefill_letters else ""
                        row_letters.append(top_letter)
                        row_codes.append(str(slot["code"]))
                        underline_styles.append(('LINEBELOW', (col_idx, 0), (col_idx, 0), 1.5, colors.black))
                    else:
                        row_letters.append(slot["char"])
                        row_codes.append("")
                    col_idx += 1

                if w_idx < len(line_words) - 1:
                    col_widths.append(gap_w)
                    row_letters.append("")
                    row_codes.append("")
                    col_idx += 1

            t_line = Table([row_letters, row_codes], colWidths=col_widths, hAlign='CENTER')
            t_line.setStyle(TableStyle([
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('BOTTOMPADDING', (0,0), (-1,0), 1),
                ('TOPPADDING', (0,1), (-1,1), 2),
                ('BOTTOMPADDING', (0,1), (-1,1), 1),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,0), 9 if is_half_page else 11),
                ('FONTNAME', (0,1), (-1,1), 'Helvetica-Bold'),
                ('FONTSIZE', (0,1), (-1,1), 7 if is_half_page else 8),
            ] + underline_styles))
            tables.append(t_line)

        return tables

    # 1. RENDER STUDENT WORKSHEET CARD
    def render_single_worksheet_flowables(p_data, form_label="") -> List[Any]:
        f = []
        inner_width = printable_width - (16 if is_half_page else 24)
        
        # Student Header (clean lines, zero standards)
        hdr_table_data = [[
            Paragraph("<b>Name:</b> ___________________________", header_style),
            Paragraph("<b>Class/Room:</b> _______", header_style),
            Paragraph("<b>Date:</b> _________", header_style)
        ]]
        col_w = inner_width / 3
        hdr_table = Table(hdr_table_data, colWidths=[col_w * 1.3, col_w * 0.8, col_w * 0.9])
        hdr_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
            ('TOPPADDING', (0,0), (-1,-1), 0),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
            ('LINEBELOW', (0,0), (-1,-1), 1, colors.black),
        ]))
        f.append(hdr_table)
        f.append(Spacer(1, 3 if is_half_page else 6))
        
        # Title
        full_title = f"{title_text} {form_label}".strip()
        f.append(Paragraph(full_title, title_style))
        f.append(Spacer(1, 2 if is_half_page else 4))
        
        # Kid-Friendly Clear Math Strategy Box (Zero teacher jargon)
        if include_strategy_box and strategy_info:
            kid_name = strategy_info.get("kid_title", "Clear Math Tip")
            tip = strategy_info.get("student_tip", "")
            skip_line = strategy_info.get("skip_count_line", "")
            
            strat_content = f"<b>{kid_name}</b> {tip}"
            if skip_line:
                strat_content += f"<br/><b>👉 Skip-Counting Track:</b> <font face='Helvetica-Bold'>{skip_line}</font>"
                
            strat_table_data = [[Paragraph(strat_content, story_style)]]
            strat_table = Table(strat_table_data, colWidths=[inner_width])
            strat_table.setStyle(TableStyle([
                ('BOX', (0,0), (-1,-1), 1, colors.black),
                ('TOPPADDING', (0,0), (-1,-1), 2 if is_half_page else 4),
                ('BOTTOMPADDING', (0,0), (-1,-1), 2 if is_half_page else 4),
                ('LEFTPADDING', (0,0), (-1,-1), 6),
                ('RIGHTPADDING', (0,0), (-1,-1), 6),
                ('BACKGROUND', (0,0), (-1,-1), colors.Color(0.98, 0.98, 0.98)),
            ]))
            f.append(strat_table)
            f.append(Spacer(1, 3 if is_half_page else 6))

        # Puzzle Body
        ptype = p_data.get("type")
        
        if ptype == "riddle":
            q_text = f"<b>MISSION RIDDLE:</b> <i>\"{p_data.get('question')}\"</i>"
            f.append(Paragraph(q_text, header_style))
            f.append(Paragraph("Solve the multiplication facts below. Match your answers to the letter codes to decode the secret punchline!", story_style))
            f.append(Spacer(1, 3 if is_half_page else 6))
            
            prob_items = p_data.get("problems", [])
            table_rows = []
            for i in range(0, len(prob_items), 2):
                p1 = prob_items[i]
                p2 = prob_items[i+1] if i+1 < len(prob_items) else None
                
                hint1 = f"<br/><font size='7' color='gray'>[think: {p1['repeated_addition_hint']}]</font>" if p1.get('repeated_addition_hint') else ""
                hint2 = f"<br/><font size='7' color='gray'>[think: {p2['repeated_addition_hint']}]</font>" if p2 and p2.get('repeated_addition_hint') else ""
                
                badge1 = f"<font color='white' backcolor='black'><b>&nbsp;{p1.get('letter')}&nbsp;</b></font>&nbsp;&nbsp;{p1.get('prompt_str')}{hint1}"
                badge2 = f"<font color='white' backcolor='black'><b>&nbsp;{p2.get('letter')}&nbsp;</b></font>&nbsp;&nbsp;{p2.get('prompt_str')}{hint2}" if p2 else ""
                table_rows.append([Paragraph(badge1, problem_style), Paragraph(badge2, problem_style)])
                
            p_col_w = inner_width / 2
            prob_table = Table(table_rows, colWidths=[p_col_w, p_col_w])
            prob_table.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('BOTTOMPADDING', (0,0), (-1,-1), 2 if is_half_page else 4),
                ('TOPPADDING', (0,0), (-1,-1), 2 if is_half_page else 4),
                ('LEFTPADDING', (0,0), (-1,-1), 4),
                ('RIGHTPADDING', (0,0), (-1,-1), 4),
            ]))
            f.append(prob_table)
            f.append(Spacer(1, 3 if is_half_page else 6))
            
            # Punchline Blanks Area
            punchline_box_items = [
                Paragraph("<b>SECRET PUNCHLINE:</b>", header_style),
                Spacer(1, 2 if is_half_page else 3)
            ]
            ptables = build_punchline_table(p_data.get("punchline_structure", []), inner_width - 20, prefill_letters=False)
            for pt in ptables:
                punchline_box_items.append(pt)
                punchline_box_items.append(Spacer(1, 2))
                
            punch_card = Table([[punchline_box_items]], colWidths=[inner_width])
            punch_card.setStyle(TableStyle([
                ('BOX', (0,0), (-1,-1), 1, colors.black),
                ('TOPPADDING', (0,0), (-1,-1), 3 if is_half_page else 5),
                ('BOTTOMPADDING', (0,0), (-1,-1), 3 if is_half_page else 5),
                ('LEFTPADDING', (0,0), (-1,-1), 8),
                ('RIGHTPADDING', (0,0), (-1,-1), 8),
                ('BACKGROUND', (0,0), (-1,-1), colors.Color(0.99, 0.99, 0.99)),
            ]))
            f.append(punch_card)

            # Bottom Section (Full Page)
            if not is_half_page:
                f.append(Spacer(1, 8))
                if p_data.get("extension_challenge"):
                    ext = p_data["extension_challenge"]
                    ext_content = [
                        Paragraph(f"{ext['prompt']}", story_style),
                        Spacer(1, 4),
                        Paragraph(f"<b>{ext['equation_blank']}</b>", problem_style)
                    ]
                    ext_card = Table([[ext_content]], colWidths=[inner_width])
                    ext_card.setStyle(TableStyle([
                        ('BOX', (0,0), (-1,-1), 1.5, colors.black),
                        ('BACKGROUND', (0,0), (-1,-1), colors.Color(0.96, 0.96, 0.96)),
                        ('TOPPADDING', (0,0), (-1,-1), 6),
                        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                        ('LEFTPADDING', (0,0), (-1,-1), 8),
                        ('RIGHTPADDING', (0,0), (-1,-1), 8),
                    ]))
                    f.append(ext_card)
                elif p_data.get("scaffold_support"):
                    scaf = p_data["scaffold_support"]
                    scaf_content = [
                        Paragraph(f"<b>{scaf['title']}</b>", header_style),
                        Spacer(1, 3),
                        Paragraph(f"<b>Visual Model:</b> {scaf['dots_visual']}", story_style),
                        Paragraph(f"<b>Repeated Addition:</b> {scaf['repeated_addition_example']}", story_style)
                    ]
                    scaf_card = Table([[scaf_content]], colWidths=[inner_width])
                    scaf_card.setStyle(TableStyle([
                        ('BOX', (0,0), (-1,-1), 1.5, colors.black),
                        ('BACKGROUND', (0,0), (-1,-1), colors.Color(0.96, 0.96, 0.96)),
                        ('TOPPADDING', (0,0), (-1,-1), 6),
                        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                        ('LEFTPADDING', (0,0), (-1,-1), 8),
                        ('RIGHTPADDING', (0,0), (-1,-1), 8),
                    ]))
                    f.append(scaf_card)
                elif p_data.get("show_thinking"):
                    think_content = [
                        Paragraph("<b>🎨 SHOW YOUR THINKING:</b> Pick any fact from above. In the space below, sketch a <b>rectangular array</b> (rows × columns) to model your answer!", header_style),
                        Spacer(1, 30),
                        Paragraph("<font size='7' color='gray'>Fact chosen: _____ × _____ = _____ | Number of Rows: _____ | Number of Columns: _____</font>", story_style)
                    ]
                    think_card = Table([[think_content]], colWidths=[inner_width])
                    think_card.setStyle(TableStyle([
                        ('BOX', (0,0), (-1,-1), 1, colors.black),
                        ('TOPPADDING', (0,0), (-1,-1), 6),
                        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                        ('LEFTPADDING', (0,0), (-1,-1), 8),
                        ('RIGHTPADDING', (0,0), (-1,-1), 8),
                    ]))
                    f.append(think_card)

        elif ptype == "detective":
            f.append(Paragraph(f"<b>🕵️ DETECTIVE BRIEFING:</b> {p_data.get('mission_brief')}", story_style))
            f.append(Spacer(1, 3 if is_half_page else 6))
            
            probs = p_data.get("problems", [])
            det_rows = [["#", "Pete's Solved Equation", "Your Verdict", "True Product (if wrong)"]]
            for p in probs:
                eq_str = f"{p['factor1']} × {p['factor2']} = {p['displayed_answer']}"
                if p.get("repeated_addition_hint"):
                    eq_str += f"<br/><font size='7' color='gray'>[think: {p['repeated_addition_hint']}]</font>"
                det_rows.append([
                    str(p["id"]),
                    Paragraph(eq_str, story_style),
                    "○ Correct   ○ Mistake",
                    "_________________"
                ])
                
            t_detective = Table(det_rows, colWidths=[20, 160, 150, 180])
            t_detective.setStyle(TableStyle([
                ('BOX', (0,0), (-1,-1), 1.5, colors.black),
                ('GRID', (0,0), (-1,-1), 1, colors.black),
                ('BACKGROUND', (0,0), (-1,0), colors.Color(0.92, 0.92, 0.92)),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,-1), 8 if is_half_page else 9),
                ('TOPPADDING', (0,0), (-1,-1), 2 if is_half_page else 4),
                ('BOTTOMPADDING', (0,0), (-1,-1), 2 if is_half_page else 4),
                ('ALIGN', (0,0), (0,-1), 'CENTER'),
                ('ALIGN', (2,1), (2,-1), 'CENTER'),
            ]))
            f.append(t_detective)

            if not is_half_page:
                f.append(Spacer(1, 8))
                if p_data.get("extension_challenge"):
                    ext = p_data["extension_challenge"]
                    ext_content = [
                        Paragraph(f"{ext['prompt']}", story_style),
                        Spacer(1, 4),
                        Paragraph(f"<b>{ext['equation_blank']}</b>", problem_style)
                    ]
                    ext_card = Table([[ext_content]], colWidths=[inner_width])
                    ext_card.setStyle(TableStyle([
                        ('BOX', (0,0), (-1,-1), 1.5, colors.black),
                        ('BACKGROUND', (0,0), (-1,-1), colors.Color(0.96, 0.96, 0.96)),
                        ('TOPPADDING', (0,0), (-1,-1), 6),
                        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                        ('LEFTPADDING', (0,0), (-1,-1), 8),
                        ('RIGHTPADDING', (0,0), (-1,-1), 8),
                    ]))
                    f.append(ext_card)
                elif p_data.get("case_notes_prompt"):
                    notes_content = [
                        Paragraph("<b>📝 DETECTIVE CASE LOG (SMP 3 Reasoning):</b> Pick one of Pete's mistakes above (Problem #___). In the space below, explain <i>why</i> his answer was incorrect, and show how to solve it correctly:", header_style),
                        Spacer(1, 24),
                        Paragraph("Explanation: ________________________________________________________________________________________________", story_style),
                        Paragraph("Correct Math Strategy: ____________________________________________________________________________________", story_style)
                    ]
                    notes_card = Table([[notes_content]], colWidths=[inner_width])
                    notes_card.setStyle(TableStyle([
                        ('BOX', (0,0), (-1,-1), 1, colors.black),
                        ('TOPPADDING', (0,0), (-1,-1), 6),
                        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                        ('LEFTPADDING', (0,0), (-1,-1), 8),
                        ('RIGHTPADDING', (0,0), (-1,-1), 8),
                    ]))
                    f.append(notes_card)

        elif ptype == "maze":
            f.append(Paragraph(f"<b>🚀 MAZE CHALLENGE:</b> {p_data.get('instructions')}", story_style))
            f.append(Spacer(1, 3 if is_half_page else 6))
            
            grid = p_data.get("grid", [])
            r_count = len(grid)
            c_count = len(grid[0]) if r_count > 0 else 0
            
            cell_size = 40 if is_half_page else 48
            maze_rows = []
            for r in range(r_count):
                row_items = []
                for c in range(c_count):
                    txt = grid[r][c]["text"]
                    if r == 0 and c == 0:
                        txt = f"START\n{txt}"
                    elif r == r_count - 1 and c == c_count - 1:
                        txt = f"{txt}\nFINISH"
                    row_items.append(txt)
                maze_rows.append(row_items)
                
            t_maze = Table(maze_rows, colWidths=[cell_size]*c_count, rowHeights=[cell_size]*r_count, hAlign='CENTER')
            t_maze.setStyle(TableStyle([
                ('BOX', (0,0), (-1,-1), 2, colors.black),
                ('GRID', (0,0), (-1,-1), 1, colors.black),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,-1), 7 if is_half_page else 8),
            ]))
            f.append(t_maze)

            if not is_half_page:
                f.append(Spacer(1, 8))
                if p_data.get("extension_challenge"):
                    ext = p_data["extension_challenge"]
                    ext_content = [
                        Paragraph(f"{ext['prompt']}", story_style),
                        Spacer(1, 4),
                        Paragraph(f"<b>{ext['equation_blank']}</b>", problem_style)
                    ]
                    ext_card = Table([[ext_content]], colWidths=[inner_width])
                    ext_card.setStyle(TableStyle([
                        ('BOX', (0,0), (-1,-1), 1.5, colors.black),
                        ('BACKGROUND', (0,0), (-1,-1), colors.Color(0.96, 0.96, 0.96)),
                        ('TOPPADDING', (0,0), (-1,-1), 6),
                        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                        ('LEFTPADDING', (0,0), (-1,-1), 8),
                        ('RIGHTPADDING', (0,0), (-1,-1), 8),
                    ]))
                    f.append(ext_card)
                elif p_data.get("checkpoint_prompt"):
                    check_content = [
                        Paragraph("<b>🏁 MULTIPLES CHECKPOINT:</b> List 5 multiples you discovered along your path from lowest to highest:", header_style),
                        Spacer(1, 6),
                        Paragraph("1) ________&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;2) ________&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;3) ________&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;4) ________&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;5) ________", problem_style)
                    ]
                    check_card = Table([[check_content]], colWidths=[inner_width])
                    check_card.setStyle(TableStyle([
                        ('BOX', (0,0), (-1,-1), 1, colors.black),
                        ('TOPPADDING', (0,0), (-1,-1), 6),
                        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                        ('LEFTPADDING', (0,0), (-1,-1), 8),
                        ('RIGHTPADDING', (0,0), (-1,-1), 8),
                    ]))
                    f.append(check_card)

        # Outer card box matching preview
        outer_card = Table([[f]], colWidths=[printable_width])
        outer_card.setStyle(TableStyle([
            ('BOX', (0,0), (-1,-1), 1.5, colors.black),
            ('TOPPADDING', (0,0), (-1,-1), 6 if is_half_page else 10),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6 if is_half_page else 10),
            ('LEFTPADDING', (0,0), (-1,-1), 8 if is_half_page else 12),
            ('RIGHTPADDING', (0,0), (-1,-1), 8 if is_half_page else 12),
            ('BACKGROUND', (0,0), (-1,-1), colors.white),
        ]))
        return [outer_card]

    # 2. RENDER OPTION 3: ANNOTATED TEACHER MASTER KEY (1:1 Mirror with Filled Solutions & Coaching Look-Fors)
    def render_annotated_teacher_master(p_data, key_title: str) -> List[Any]:
        f_ak = []
        inner_width = printable_width - (16 if is_half_page else 24)
        
        # Teacher Master Header
        master_header_text = f"<b>TEACHER ANSWER MASTER</b> &nbsp;&nbsp;|&nbsp;&nbsp; <font color='#444'>{key_title}</font>"
        f_ak.append(Paragraph(master_header_text, header_style))
        f_ak.append(Spacer(1, 2))
        
        # Section Standards Annotation (Right on the section, not an abstract table!)
        std_note = "<b>Target Standards:</b> WA CCSS 3.OA.A.1, 3.OA.C.7 &nbsp;|&nbsp; <b>Model:</b> Clear Math CPA Strategic Fluency"
        f_ak.append(Paragraph(std_note, story_style))
        f_ak.append(Spacer(1, 4))

        ptype = p_data.get("type")
        if ptype == "riddle":
            # 1:1 Riddle Question
            f_ak.append(Paragraph(f"<b>MISSION RIDDLE:</b> <i>\"{p_data.get('question')}\"</i>", header_style))
            f_ak.append(Paragraph(f"<b>SOLVED PUNCHLINE ANSWER:</b> <font color='black'><b>{p_data.get('punchline')}</b></font>", problem_style))
            f_ak.append(Spacer(1, 4))
            
            # 1:1 Pre-Filled Equations Grid with Coaching Look-Fors!
            prob_items = p_data.get("problems", [])
            table_rows = []
            for i in range(0, len(prob_items), 2):
                p1 = prob_items[i]
                p2 = prob_items[i+1] if i+1 < len(prob_items) else None
                
                # Filled answer in bold
                f1_solved = f"{p1['factor1']} × {p1['factor2']} = <b><u>{p1['product']}</u></b>"
                look_for1 = get_problem_look_for(p1)
                cell1 = f"<font color='white' backcolor='black'><b>&nbsp;{p1.get('letter')}&nbsp;</b></font>&nbsp;&nbsp;{f1_solved}<br/><font size='7' color='#444'><i>{look_for1}</i></font>"
                
                if p2:
                    f2_solved = f"{p2['factor1']} × {p2['factor2']} = <b><u>{p2['product']}</u></b>"
                    look_for2 = get_problem_look_for(p2)
                    cell2 = f"<font color='white' backcolor='black'><b>&nbsp;{p2.get('letter')}&nbsp;</b></font>&nbsp;&nbsp;{f2_solved}<br/><font size='7' color='#444'><i>{look_for2}</i></font>"
                else:
                    cell2 = ""
                    
                table_rows.append([Paragraph(cell1, story_style), Paragraph(cell2, story_style)])
                
            p_col_w = inner_width / 2
            prob_table = Table(table_rows, colWidths=[p_col_w, p_col_w])
            prob_table.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('BOTTOMPADDING', (0,0), (-1,-1), 2 if is_half_page else 4),
                ('TOPPADDING', (0,0), (-1,-1), 2 if is_half_page else 4),
                ('LEFTPADDING', (0,0), (-1,-1), 4),
                ('RIGHTPADDING', (0,0), (-1,-1), 4),
            ]))
            f_ak.append(prob_table)
            f_ak.append(Spacer(1, 4))
            
            # 1:1 Pre-Filled Punchline Blanks (letters filled above numbers!)
            punchline_box_items = [
                Paragraph("<b>SOLVED PUNCHLINE (LETTERS IN BLANKS):</b>", header_style),
                Spacer(1, 2)
            ]
            ptables = build_punchline_table(p_data.get("punchline_structure", []), inner_width - 20, prefill_letters=True)
            for pt in ptables:
                punchline_box_items.append(pt)
                punchline_box_items.append(Spacer(1, 2))
                
            punch_card = Table([[punchline_box_items]], colWidths=[inner_width])
            punch_card.setStyle(TableStyle([
                ('BOX', (0,0), (-1,-1), 1, colors.black),
                ('BACKGROUND', (0,0), (-1,-1), colors.Color(0.97, 0.97, 0.97)),
                ('TOPPADDING', (0,0), (-1,-1), 3 if is_half_page else 5),
                ('BOTTOMPADDING', (0,0), (-1,-1), 3 if is_half_page else 5),
                ('LEFTPADDING', (0,0), (-1,-1), 8),
                ('RIGHTPADDING', (0,0), (-1,-1), 8),
            ]))
            f_ak.append(punch_card)

            # Bottom Section Exemplars
            if not is_half_page:
                f_ak.append(Spacer(1, 6))
                if p_data.get("extension_challenge"):
                    ext = p_data["extension_challenge"]
                    ext_exemplar = [
                        Paragraph(f"<b>⭐ STAR CHALLENGE SOLUTION:</b> {ext['prompt']}", story_style),
                        Spacer(1, 2),
                        Paragraph(f"<b>Solved Equation:</b> <u>{ext['solution']}</u> &nbsp;&nbsp;|&nbsp;&nbsp; <font size='7' color='#444'>Standard: WA CCSS 4.OA.A.1 (Multiplicative Comparison)</font>", header_style)
                    ]
                    c_ext = Table([[ext_exemplar]], colWidths=[inner_width])
                    c_ext.setStyle(TableStyle([
                        ('BOX', (0,0), (-1,-1), 1.5, colors.black),
                        ('BACKGROUND', (0,0), (-1,-1), colors.Color(0.96, 0.96, 0.96)),
                        ('TOPPADDING', (0,0), (-1,-1), 5),
                        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
                        ('LEFTPADDING', (0,0), (-1,-1), 8),
                        ('RIGHTPADDING', (0,0), (-1,-1), 8),
                    ]))
                    f_ak.append(c_ext)
                elif p_data.get("scaffold_support"):
                    scaf = p_data["scaffold_support"]
                    scaf_exemplar = [
                        Paragraph(f"<b>🌱 VISUAL SUPPORT EXEMPLAR:</b> {scaf['dots_visual']}", story_style),
                        Paragraph(f"<b>Completed Model:</b> {scaf['repeated_addition_example']} &nbsp;|&nbsp; <font size='7' color='#444'>Standard: WA CCSS 2.OA.C.4 (Equal Groups)</font>", story_style)
                    ]
                    c_scaf = Table([[scaf_exemplar]], colWidths=[inner_width])
                    c_scaf.setStyle(TableStyle([
                        ('BOX', (0,0), (-1,-1), 1.5, colors.black),
                        ('BACKGROUND', (0,0), (-1,-1), colors.Color(0.96, 0.96, 0.96)),
                        ('TOPPADDING', (0,0), (-1,-1), 5),
                        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
                        ('LEFTPADDING', (0,0), (-1,-1), 8),
                        ('RIGHTPADDING', (0,0), (-1,-1), 8),
                    ]))
                    f_ak.append(c_scaf)
                elif p_data.get("show_thinking"):
                    # Sample Fact for array
                    sample_fact = p_data["problems"][0] if p_data.get("problems") else {"factor1": 3, "factor2": 4, "product": 12}
                    s_r = min(sample_fact["factor1"], 4) or 3
                    s_c = min(sample_fact["factor2"], 6) or 4
                    dot_row = "  ".join(["●"] * s_c)
                    dot_rows = "<br/>".join([f"&nbsp;&nbsp;{dot_row}&nbsp;&nbsp;&nbsp;&nbsp;(Row: {s_c})" for _ in range(s_r)])
                    
                    think_exemplar = [
                        Paragraph(f"<b>🎨 SHOW YOUR THINKING: EXEMPLAR ARRAY MODEL for {sample_fact['factor1']} × {sample_fact['factor2']} = {sample_fact['product']}</b>", header_style),
                        Spacer(1, 2),
                        Paragraph(f"<font face='Helvetica-Bold' size='9'>{dot_rows}</font>", story_style),
                        Spacer(1, 2),
                        Paragraph(f"<font size='8'><b>Structure:</b> {s_r} Rows × {s_c} Columns = {sample_fact['product']} total &nbsp;&nbsp;|&nbsp;&nbsp; <font color='#444'>WA CCSS 3.OA.A.1, 3.MD.C.7</font></font>", story_style),
                        Paragraph("<font size='7' color='#333'><b>🔍 Teacher Look-For:</b> Verify student drew straight, organized rows and columns (equal groups), not a scattered cluster.</font>", story_style)
                    ]
                    c_think = Table([[think_exemplar]], colWidths=[inner_width])
                    c_think.setStyle(TableStyle([
                        ('BOX', (0,0), (-1,-1), 1.5, colors.black),
                        ('BACKGROUND', (0,0), (-1,-1), colors.Color(0.98, 0.98, 0.98)),
                        ('TOPPADDING', (0,0), (-1,-1), 5),
                        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
                        ('LEFTPADDING', (0,0), (-1,-1), 8),
                        ('RIGHTPADDING', (0,0), (-1,-1), 8),
                    ]))
                    f_ak.append(c_think)

        elif ptype == "detective":
            f_ak.append(Paragraph(f"<b>🕵️ DETECTIVE MASTER KEY:</b> {p_data.get('mission_brief')}", header_style))
            f_ak.append(Spacer(1, 4))
            
            probs = p_data.get("problems", [])
            det_rows = [["#", "Pete's Solved Equation", "Verdict", "True Product", "Misconception / Coaching Look-For"]]
            for p in probs:
                verdict = "<b>✗ MISTAKE</b>" if p["is_error"] else "<b>✓ Correct</b>"
                bg_color = colors.Color(1, 0.9, 0.9) if p["is_error"] else colors.white
                det_rows.append([
                    str(p["id"]),
                    f"{p['factor1']} × {p['factor2']} = {p['displayed_answer']}",
                    Paragraph(verdict, story_style),
                    str(p["correct_answer"]),
                    Paragraph(p["error_reason"], story_style)
                ])
                
            t_det_key = Table(det_rows, colWidths=[20, 100, 65, 75, 230])
            t_det_key.setStyle(TableStyle([
                ('BOX', (0,0), (-1,-1), 1.5, colors.black),
                ('GRID', (0,0), (-1,-1), 1, colors.black),
                ('BACKGROUND', (0,0), (-1,0), colors.Color(0.92, 0.92, 0.92)),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,-1), 7 if is_half_page else 8),
                ('TOPPADDING', (0,0), (-1,-1), 2),
                ('BOTTOMPADDING', (0,0), (-1,-1), 2),
                ('ALIGN', (0,0), (0,-1), 'CENTER'),
                ('ALIGN', (2,1), (2,-1), 'CENTER'),
                ('ALIGN', (3,1), (3,-1), 'CENTER'),
            ]))
            f_ak.append(t_det_key)

            if not is_half_page and p_data.get("case_notes_prompt"):
                f_ak.append(Spacer(1, 6))
                case_exemplar = [
                    Paragraph("<b>📝 CASE LOG EXEMPLAR (SMP 3 Reasoning):</b>", header_style),
                    Paragraph("<i>\"Problem #4: Pete got 6 × 4 wrong because he added the numbers to get 10. To multiply, he needed 4 groups of 6, which equals 24 (double 6 is 12, double 12 is 24).\"</i>", story_style),
                    Paragraph("<font size='7' color='#444'><b>🔍 Teacher Look-For:</b> Student explicitly mentions that Pete added instead of multiplied, and states the correct product (24).</font>", story_style)
                ]
                c_case = Table([[case_exemplar]], colWidths=[inner_width])
                c_case.setStyle(TableStyle([
                    ('BOX', (0,0), (-1,-1), 1, colors.black),
                    ('BACKGROUND', (0,0), (-1,-1), colors.Color(0.98, 0.98, 0.98)),
                    ('TOPPADDING', (0,0), (-1,-1), 5),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 5),
                    ('LEFTPADDING', (0,0), (-1,-1), 8),
                    ('RIGHTPADDING', (0,0), (-1,-1), 8),
                ]))
                f_ak.append(c_case)

        elif ptype == "maze":
            f_ak.append(Paragraph(f"<b>🚀 MAZE SOLUTION KEY:</b> Shaded squares indicate the true path from START to FINISH.", header_style))
            f_ak.append(Spacer(1, 4))
            
            sol_grid = p_data.get("solution_grid", [])
            grid = p_data.get("grid", [])
            disp_rows = []
            for r in range(len(grid)):
                row_items = []
                for c in range(len(grid[0])):
                    if sol_grid[r][c] == 1:
                        row_items.append(f"[PATH]\n{grid[r][c]['text']}")
                    else:
                        row_items.append(grid[r][c]['text'])
                disp_rows.append(row_items)
                
            c_size = 35 if is_half_page else 42
            t_sol = Table(disp_rows, colWidths=[c_size]*len(grid[0]), rowHeights=[c_size]*len(grid), hAlign='CENTER')
            
            maze_styles = [
                ('BOX', (0,0), (-1,-1), 1.5, colors.black),
                ('GRID', (0,0), (-1,-1), 1, colors.black),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('FONTSIZE', (0,0), (-1,-1), 6 if is_half_page else 7),
            ]
            for r in range(len(grid)):
                for c in range(len(grid[0])):
                    if sol_grid[r][c] == 1:
                        maze_styles.append(('BACKGROUND', (c, r), (c, r), colors.Color(0.88, 0.88, 0.88)))
                        maze_styles.append(('FONTNAME', (c, r), (c, r), 'Helvetica-Bold'))
                        
            t_sol.setStyle(TableStyle(maze_styles))
            f_ak.append(t_sol)

            if not is_half_page and p_data.get("checkpoint_prompt"):
                f_ak.append(Spacer(1, 6))
                t_nums = p_data.get("targets_str", "target")
                check_exemplar = [
                    Paragraph(f"<b>🏁 MULTIPLES CHECKPOINT KEY:</b> Any valid multiples of {t_nums} (e.g. 4, 8, 12, 16, 20).", header_style),
                    Paragraph("<font size='7' color='#444'><b>🔍 Teacher Look-For:</b> Multiples are written in ascending order without non-multiples.</font>", story_style)
                ]
                c_chk = Table([[check_exemplar]], colWidths=[inner_width])
                c_chk.setStyle(TableStyle([
                    ('BOX', (0,0), (-1,-1), 1, colors.black),
                    ('BACKGROUND', (0,0), (-1,-1), colors.Color(0.98, 0.98, 0.98)),
                    ('TOPPADDING', (0,0), (-1,-1), 5),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 5),
                    ('LEFTPADDING', (0,0), (-1,-1), 8),
                    ('RIGHTPADDING', (0,0), (-1,-1), 8),
                ]))
                f_ak.append(c_chk)

        # Outer card box for teacher key
        outer_ak_card = Table([[f_ak]], colWidths=[printable_width])
        outer_ak_card.setStyle(TableStyle([
            ('BOX', (0,0), (-1,-1), 1.5, colors.black),
            ('TOPPADDING', (0,0), (-1,-1), 6 if is_half_page else 10),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6 if is_half_page else 10),
            ('LEFTPADDING', (0,0), (-1,-1), 8 if is_half_page else 12),
            ('RIGHTPADDING', (0,0), (-1,-1), 8 if is_half_page else 12),
            ('BACKGROUND', (0,0), (-1,-1), colors.white),
        ]))
        return [outer_ak_card]

    # Assembly
    story = []
    
    if layout_mode == "full_page":
        story.extend(render_single_worksheet_flowables(puzzle_data))
    else:
        label_a = "(FORM A)" if layout_mode == "half_page_ab" else "(COPY 1)"
        label_b = "(FORM B)" if layout_mode == "half_page_ab" else "(COPY 2)"
        data_b = form_b_data if (layout_mode == "half_page_ab" and form_b_data) else puzzle_data
        
        story.extend(render_single_worksheet_flowables(puzzle_data, label_a))
        story.append(Spacer(1, 4))
        
        cut_msg = "✂ CUT HERE (TWIN COPIES) ✂" if layout_mode == "half_page_twin" else "✂ CUT HERE (ANTI-PEEKING FORM A & B) ✂"
        cut_table = Table([[
            Paragraph(f"<font color='black'>- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - &nbsp;&nbsp;<b>{cut_msg}</b>&nbsp;&nbsp; - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -</font>", ParagraphStyle('CutStyle', parent=styles['Normal'], alignment=1, fontSize=7, leading=8))
        ]], colWidths=[printable_width])
        cut_table.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 2),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ]))
        story.append(cut_table)
        story.append(Spacer(1, 4))
        story.extend(render_single_worksheet_flowables(data_b, label_b))

    # Teacher Answer Key Page (Option 3 Annotated Master)
    if include_answer_key:
        story.append(PageBreak())
        
        if layout_mode == "half_page_ab" and form_b_data:
            story.extend(render_annotated_teacher_master(puzzle_data, "FORM A (TOP HALF)"))
            story.append(Spacer(1, 8))
            story.append(Paragraph("<font color='black'>- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -</font>", ParagraphStyle('AKDivider', alignment=1, fontSize=6, leading=6)))
            story.append(Spacer(1, 8))
            story.extend(render_annotated_teacher_master(form_b_data, "FORM B (BOTTOM HALF)"))
        elif layout_mode == "half_page_twin":
            story.extend(render_annotated_teacher_master(puzzle_data, "FORM A (TWIN COPIES 1 & 2)"))
        else:
            story.extend(render_annotated_teacher_master(puzzle_data, "COMPLETE CURRICULUM EXEMPLAR"))

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
