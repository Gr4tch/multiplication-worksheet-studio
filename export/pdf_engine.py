"""
ReportLab PDF Generation Engine for Printable Math Worksheets.
Generates vector-crisp, ink-friendly 8.5x11 B&W PDFs for school printing.
Matches preview canvas layout 1:1 and guarantees multi-form answer keys.
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

def create_worksheet_pdf(
    puzzle_data: Dict[str, Any],
    form_b_data: Optional[Dict[str, Any]] = None,
    custom_title: Optional[str] = None,
    layout_mode: str = "full_page", # 'full_page', 'half_page_twin', 'half_page_ab'
    include_strategy_box: bool = True,
    strategy_info: Optional[Dict[str, Any]] = None,
    include_answer_key: bool = True,
    font_choice: str = "Helvetica"
) -> bytes:
    """
    Generates a print-ready PDF byte stream matching preview styling 1:1.
    """
    buffer = io.BytesIO()
    
    # 8.5 x 11 inches: 612 x 792 points
    # 0.35 inch margins (25.2 pt) maximize usable printable space
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
    
    # Dynamic styles based on layout mode (compact for half-page)
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
        alignment=1, # Center
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

    def build_punchline_table(struct: List[List[Dict[str, Any]]], max_width: float) -> List[Table]:
        """
        Builds horizontal word lines for the punchline cipher.
        Guarantees numbers never wrap vertically and words flow horizontally side-by-side.
        """
        slot_w = 20 if is_half_page else 24
        gap_w = 12 if is_half_page else 16
        
        # Split words into lines that fit within max_width
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
                        row_letters.append("") # Student writes letter here
                        row_codes.append(str(slot["code"]))
                        underline_styles.append(('LINEBELOW', (col_idx, 0), (col_idx, 0), 1.5, colors.black))
                    else:
                        row_letters.append(slot["char"])
                        row_codes.append("")
                    col_idx += 1

                # Add word gap if not last word in line
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

    def render_single_worksheet_flowables(p_data, form_label="") -> List[Any]:
        """Renders all elements of a single worksheet inside a clean card."""
        f = []
        
        # 1. Student Header
        hdr_table_data = [[
            Paragraph("<b>Name:</b> ___________________________", header_style),
            Paragraph("<b>Class/Room:</b> _______", header_style),
            Paragraph("<b>Date:</b> _________", header_style)
        ]]
        inner_width = printable_width - (16 if is_half_page else 24)
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
        
        # 2. Title
        full_title = f"{title_text} {form_label}".strip()
        f.append(Paragraph(full_title, title_style))
        f.append(Spacer(1, 2 if is_half_page else 4))
        
        # 3. Clear Math Strategy Box (if enabled)
        if include_strategy_box and strategy_info:
            tip = strategy_info.get("student_tip", "")
            hint = strategy_info.get("visual_hint", "")
            strat_table_data = [[
                Paragraph(f"<b>💡 Clear Math Strategy Tip:</b> {tip}<br/><b>📐 Visual Anchor:</b> {hint}", story_style)
            ]]
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

        # 4. Puzzle Specific Content
        ptype = p_data.get("type")
        
        if ptype == "riddle":
            # Riddle Prompt
            q_text = f"<b>MISSION RIDDLE:</b> <i>\"{p_data.get('question')}\"</i>"
            f.append(Paragraph(q_text, header_style))
            f.append(Paragraph("Solve the multiplication facts below. Match your answers to the letter codes to decode the secret punchline!", story_style))
            f.append(Spacer(1, 3 if is_half_page else 5))
            
            # Problems Grid (2 columns)
            prob_items = p_data.get("problems", [])
            table_rows = []
            for i in range(0, len(prob_items), 2):
                p1 = prob_items[i]
                p2 = prob_items[i+1] if i+1 < len(prob_items) else None
                
                # Inverted badge formatting matching the preview canvas
                badge1 = f"<font color='white' backcolor='black'><b>&nbsp;{p1.get('letter')}&nbsp;</b></font>&nbsp;&nbsp;{p1.get('prompt_str')}"
                badge2 = f"<font color='white' backcolor='black'><b>&nbsp;{p2.get('letter')}&nbsp;</b></font>&nbsp;&nbsp;{p2.get('prompt_str')}" if p2 else ""
                table_rows.append([Paragraph(badge1, problem_style), Paragraph(badge2, problem_style)])
                
            p_col_w = inner_width / 2
            prob_table = Table(table_rows, colWidths=[p_col_w, p_col_w])
            prob_table.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('BOTTOMPADDING', (0,0), (-1,-1), 2 if is_half_page else 5),
                ('TOPPADDING', (0,0), (-1,-1), 2 if is_half_page else 5),
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
            ptables = build_punchline_table(p_data.get("punchline_structure", []), inner_width - 20)
            for pt in ptables:
                punchline_box_items.append(pt)
                punchline_box_items.append(Spacer(1, 2))
                
            punch_card = Table([[punchline_box_items]], colWidths=[inner_width])
            punch_card.setStyle(TableStyle([
                ('BOX', (0,0), (-1,-1), 1, colors.black),
                ('LINEBEFORE', (0,0), (-1,-1), 1, colors.black),
                ('TOPPADDING', (0,0), (-1,-1), 3 if is_half_page else 6),
                ('BOTTOMPADDING', (0,0), (-1,-1), 3 if is_half_page else 6),
                ('LEFTPADDING', (0,0), (-1,-1), 8),
                ('RIGHTPADDING', (0,0), (-1,-1), 8),
                ('BACKGROUND', (0,0), (-1,-1), colors.Color(0.99, 0.99, 0.99)),
            ]))
            f.append(punch_card)

        elif ptype == "detective":
            f.append(Paragraph(f"<b>🕵️ DETECTIVE BRIEFING:</b> {p_data.get('mission_brief')}", story_style))
            f.append(Spacer(1, 3 if is_half_page else 6))
            
            probs = p_data.get("problems", [])
            det_rows = [["#", "Pete's Solved Equation", "Your Verdict", "True Product (if wrong)"]]
            for p in probs:
                eq_str = f"{p['factor1']} × {p['factor2']} = {p['displayed_answer']}"
                det_rows.append([
                    str(p["id"]),
                    eq_str,
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

        elif ptype == "maze":
            f.append(Paragraph(f"<b>🚀 MAZE CHALLENGE:</b> {p_data.get('instructions')}", story_style))
            f.append(Spacer(1, 3 if is_half_page else 6))
            
            grid = p_data.get("grid", [])
            r_count = len(grid)
            c_count = len(grid[0]) if r_count > 0 else 0
            
            cell_size = 40 if is_half_page else 52
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
                ('FONTSIZE', (0,0), (-1,-1), 7 if is_half_page else 9),
            ]))
            f.append(t_maze)
            
        # Wrap all flowables into an outer card matching preview
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

    # --- DOCUMENT ASSEMBLY ---
    story = []
    
    if layout_mode == "full_page":
        story.extend(render_single_worksheet_flowables(puzzle_data))
    else:
        # Paper-Saver 2-Up Mode (Twin or Form A & B)
        label_a = "(FORM A)" if layout_mode == "half_page_ab" else "(COPY 1)"
        label_b = "(FORM B)" if layout_mode == "half_page_ab" else "(COPY 2)"
        data_b = form_b_data if (layout_mode == "half_page_ab" and form_b_data) else puzzle_data
        
        # 1. Top Card
        story.extend(render_single_worksheet_flowables(puzzle_data, label_a))
        story.append(Spacer(1, 4))
        
        # 2. Clean Center Cut Line Table
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
        
        # 3. Bottom Card
        story.extend(render_single_worksheet_flowables(data_b, label_b))

    # --- TEACHER ANSWER KEY PAGE ---
    if include_answer_key:
        story.append(PageBreak())
        story.append(Paragraph("TEACHER ANSWER KEY & PEDAGOGICAL ALIGNMENT", title_style))
        story.append(Paragraph("<b>Curriculum Alignment:</b> WA CCSS-M 3.OA.A.1, 3.OA.A.4, 3.OA.B.5, 3.OA.C.7 | Clear Math Instructional Model", header_style))
        story.append(Spacer(1, 6))

        def render_answer_key_content(p_data, key_title: str):
            f_ak = []
            f_ak.append(Paragraph(f"<b>{key_title}</b>", header_style))
            f_ak.append(Spacer(1, 3))
            
            ptype = p_data.get("type")
            if ptype == "riddle":
                f_ak.append(Paragraph(f"<b>Riddle Question:</b> {p_data.get('question')}", story_style))
                f_ak.append(Paragraph(f"<b>SOLVED PUNCHLINE:</b> <b>{p_data.get('punchline')}</b>", header_style))
                f_ak.append(Spacer(1, 4))
                
                ak_rows = [["Letter", "Equation", "Answer / Code", "Clear Math Strategy"]]
                for p in p_data.get("problems", []):
                    ak_rows.append([
                        p.get("letter", ""),
                        f"{p['factor1']} × {p['factor2']} = {p['product']}",
                        str(p.get("answer")),
                        p.get("strategy", "")
                    ])
                ak_table = Table(ak_rows, colWidths=[40, 130, 80, 240])
                ak_table.setStyle(TableStyle([
                    ('BOX', (0,0), (-1,-1), 1.5, colors.black),
                    ('GRID', (0,0), (-1,-1), 1, colors.black),
                    ('BACKGROUND', (0,0), (-1,0), colors.Color(0.92, 0.92, 0.92)),
                    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0,0), (-1,-1), 7 if is_half_page else 8),
                    ('TOPPADDING', (0,0), (-1,-1), 2),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 2),
                ]))
                f_ak.append(ak_table)

            elif ptype == "detective":
                f_ak.append(Paragraph("<b>Sneaky Pete Error Analysis:</b>", header_style))
                f_ak.append(Spacer(1, 3))
                ak_rows = [["#", "Pete's Equation", "Verdict", "True Product", "Misconception Analysis"]]
                for p in p_data.get("problems", []):
                    verdict = "MISTAKE" if p["is_error"] else "CORRECT"
                    ak_rows.append([
                        str(p["id"]),
                        f"{p['factor1']} × {p['factor2']} = {p['displayed_answer']}",
                        verdict,
                        str(p["correct_answer"]),
                        p["error_reason"]
                    ])
                ak_table = Table(ak_rows, colWidths=[20, 100, 65, 75, 230])
                ak_table.setStyle(TableStyle([
                    ('BOX', (0,0), (-1,-1), 1.5, colors.black),
                    ('GRID', (0,0), (-1,-1), 1, colors.black),
                    ('BACKGROUND', (0,0), (-1,0), colors.Color(0.92, 0.92, 0.92)),
                    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0,0), (-1,-1), 7 if is_half_page else 8),
                    ('TOPPADDING', (0,0), (-1,-1), 2),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 2),
                ]))
                f_ak.append(ak_table)

            elif ptype == "maze":
                f_ak.append(Paragraph(f"<b>Pathfinder Solution Key:</b>", header_style))
                f_ak.append(Paragraph(f"Path coordinates (row, col): {p_data.get('path_coords')}", story_style))
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
                    
                c_size = 38 if is_half_page else 45
                t_sol = Table(disp_rows, colWidths=[c_size]*len(grid[0]), rowHeights=[c_size]*len(grid), hAlign='CENTER')
                t_sol.setStyle(TableStyle([
                    ('BOX', (0,0), (-1,-1), 1.5, colors.black),
                    ('GRID', (0,0), (-1,-1), 1, colors.black),
                    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ('FONTSIZE', (0,0), (-1,-1), 6 if is_half_page else 7),
                ]))
                f_ak.append(t_sol)

            return f_ak

        if layout_mode == "half_page_ab" and form_b_data:
            # Render BOTH Form A and Form B Keys
            story.extend(render_answer_key_content(puzzle_data, "FORM A (TOP HALF) ANSWER KEY"))
            story.append(Spacer(1, 8))
            story.append(Paragraph("<font color='black'>- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -</font>", ParagraphStyle('AKDivider', alignment=1, fontSize=6, leading=6)))
            story.append(Spacer(1, 8))
            story.extend(render_answer_key_content(form_b_data, "FORM B (BOTTOM HALF) ANSWER KEY"))
        elif layout_mode == "half_page_twin":
            story.extend(render_answer_key_content(puzzle_data, "FORM A (TWIN COPIES 1 & 2) ANSWER KEY"))
        else:
            story.extend(render_answer_key_content(puzzle_data, "COMPLETE SOLUTION & REASONING KEY"))

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
