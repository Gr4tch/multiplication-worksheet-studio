"""
ReportLab PDF Generation Engine for Printable Math Worksheets.
Generates vector-crisp, ink-friendly 8.5x11 B&W PDFs for school printing.
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
from reportlab.graphics.shapes import Drawing, Line, Rect, String

def draw_cut_line(canvas, doc):
    """Draws a vertical dashed center line with scissors mark for 2-Up half-page."""
    canvas.saveState()
    canvas.setStrokeColor(colors.black)
    canvas.setLineWidth(1)
    canvas.setDash([4, 4], 0)
    canvas.line(doc.width / 2 + doc.leftMargin, 20, doc.width / 2 + doc.leftMargin, doc.height + doc.bottomMargin + 20)
    canvas.setFont("Helvetica-Bold", 8)
    canvas.drawString(doc.width / 2 + doc.leftMargin - 20, doc.height / 2, "✂ CUT HERE ✂")
    canvas.restoreState()

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
    Generates a print-ready PDF byte stream.
    """
    buffer = io.BytesIO()
    
    # 8.5 x 11 inches: 612 x 792 points
    # Margins: 0.4 inch for maximum usable print area
    margin = 0.4 * inch
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=margin,
        rightMargin=margin,
        topMargin=margin,
        bottomMargin=margin
    )
    
    styles = getSampleStyleSheet()
    
    # Define custom clean styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=16,
        alignment=1, # Center
        spaceAfter=4
    )
    
    header_style = ParagraphStyle(
        'DocHeader',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=11
    )
    
    instruction_style = ParagraphStyle(
        'DocInstruction',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9,
        leading=12,
        spaceAfter=6
    )
    
    problem_style = ParagraphStyle(
        'DocProblem',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14
    )
    
    story_style = ParagraphStyle(
        'DocStory',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12
    )

    story = []
    
    title_text = custom_title or puzzle_data.get("title") or "Multiplication Fact Practice"
    
    def render_single_worksheet_content(p_data, form_label=""):
        flowables = []
        
        # Student Header
        header_text = "<b>Name:</b> ___________________________   <b>Class/Room:</b> _______   <b>Date:</b> _________"
        flowables.append(Paragraph(header_text, header_style))
        flowables.append(Spacer(1, 4))
        
        # Title
        t_str = f"{title_text} {form_label}".strip()
        flowables.append(Paragraph(t_str, title_style))
        flowables.append(Spacer(1, 2))
        
        # Strategy Helper Box (if enabled)
        if include_strategy_box and strategy_info:
            tip = strategy_info.get("student_tip", "")
            hint = strategy_info.get("visual_hint", "")
            strat_table_data = [[
                Paragraph(f"<b>Clear Math Strategy Tip:</b> {tip}<br/><b>Visual Anchor:</b> {hint}", header_style)
            ]]
            strat_table = Table(strat_table_data, colWidths=[doc.width - 10])
            strat_table.setStyle(TableStyle([
                ('BOX', (0,0), (-1,-1), 1.5, colors.black),
                ('TOPPADDING', (0,0), (-1,-1), 3),
                ('BOTTOMPADDING', (0,0), (-1,-1), 3),
                ('LEFTPADDING', (0,0), (-1,-1), 6),
                ('RIGHTPADDING', (0,0), (-1,-1), 6),
                ('BACKGROUND', (0,0), (-1,-1), colors.white),
            ]))
            flowables.append(strat_table)
            flowables.append(Spacer(1, 4))

        # Puzzle-specific elements
        ptype = p_data.get("type")
        
        if ptype == "riddle":
            # Joke Question
            q_text = f"<b>MISSION RIDDLE:</b> <i>\"{p_data.get('question')}\"</i>"
            flowables.append(Paragraph(q_text, story_style))
            flowables.append(Paragraph("Solve the multiplication facts below. Match your answers to the letter codes to crack the punchline!", instruction_style))
            flowables.append(Spacer(1, 4))
            
            # Problems Grid (2 columns)
            prob_items = p_data.get("problems", [])
            table_rows = []
            for i in range(0, len(prob_items), 2):
                p1 = prob_items[i]
                p2 = prob_items[i+1] if i+1 < len(prob_items) else None
                
                c1 = f"<b>[{p1.get('letter')}]</b>  {p1.get('prompt_str')}"
                c2 = f"<b>[{p2.get('letter')}]</b>  {p2.get('prompt_str')}" if p2 else ""
                table_rows.append([Paragraph(c1, problem_style), Paragraph(c2, problem_style)])
                
            col_w = (doc.width - 20) / 2
            prob_table = Table(table_rows, colWidths=[col_w, col_w])
            prob_table.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                ('TOPPADDING', (0,0), (-1,-1), 6),
            ]))
            flowables.append(prob_table)
            flowables.append(Spacer(1, 6))
            
            # Punchline Blanks Table
            flowables.append(Paragraph("<b>SECRET PUNCHLINE:</b>", header_style))
            flowables.append(Spacer(1, 2))
            
            # Render punchline slots
            struct = p_data.get("punchline_structure", [])
            for word_slots in struct:
                row_letters = []
                row_codes = []
                for slot in word_slots:
                    if slot["is_alpha"]:
                        row_letters.append(Paragraph("&nbsp;", problem_style)) # Blank for writing
                        row_codes.append(Paragraph(str(slot["code"]), header_style))
                    else:
                        row_letters.append(Paragraph(slot["char"], problem_style))
                        row_codes.append(Paragraph("&nbsp;", header_style))
                
                slot_w = 20
                if len(row_letters) > 0:
                    word_table = Table([row_letters, row_codes], colWidths=[slot_w]*len(row_letters))
                    word_table.setStyle(TableStyle([
                        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                        ('BOTTOMPADDING', (0,0), (-1,0), 2),
                        ('LINEBELOW', (0,0), (-1,0), 1.5, colors.black),
                        ('TOPPADDING', (0,1), (-1,1), 2),
                    ]))
                    flowables.append(word_table)
                    flowables.append(Spacer(1, 2))

        elif ptype == "detective":
            flowables.append(Paragraph(f"<b>DETECTIVE BRIEFING:</b> {p_data.get('mission_brief')}", story_style))
            flowables.append(Spacer(1, 6))
            
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
                
            t_detective = Table(det_rows, colWidths=[25, 180, 140, 160])
            t_detective.setStyle(TableStyle([
                ('BOX', (0,0), (-1,-1), 1.5, colors.black),
                ('GRID', (0,0), (-1,-1), 1, colors.black),
                ('BACKGROUND', (0,0), (-1,0), colors.Color(0.9, 0.9, 0.9)),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,-1), 10),
                ('TOPPADDING', (0,0), (-1,-1), 5),
                ('BOTTOMPADDING', (0,0), (-1,-1), 5),
                ('ALIGN', (0,0), (0,-1), 'CENTER'),
            ]))
            flowables.append(t_detective)

        elif ptype == "maze":
            flowables.append(Paragraph(f"<b>MAZE CHALLENGE:</b> {p_data.get('instructions')}", story_style))
            flowables.append(Spacer(1, 6))
            
            grid = p_data.get("grid", [])
            r_count = len(grid)
            c_count = len(grid[0]) if r_count > 0 else 0
            
            cell_size = 50
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
                
            t_maze = Table(maze_rows, colWidths=[cell_size]*c_count, rowHeights=[cell_size]*r_count)
            t_maze.setStyle(TableStyle([
                ('BOX', (0,0), (-1,-1), 2, colors.black),
                ('GRID', (0,0), (-1,-1), 1, colors.black),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,-1), 9),
            ]))
            flowables.append(t_maze)
            
        return flowables

    # Construct the PDF document flowables
    if layout_mode == "full_page":
        story.extend(render_single_worksheet_content(puzzle_data))
    else:
        # Half-Page Mode (1 sheet has Form A, and either Twin or Form B)
        # We render compact single page with 2 copies
        f_b = form_b_data if (layout_mode == "half_page_ab" and form_b_data) else puzzle_data
        story.append(Paragraph("<b>--- TOP / LEFT HALF ---</b>", instruction_style))
        story.extend(render_single_worksheet_content(puzzle_data, "(Form A)" if layout_mode == "half_page_ab" else ""))
        story.append(Spacer(1, 10))
        story.append(Paragraph("✂ - - - - - - - - - - - - - - - - - - - - - CUT HERE - - - - - - - - - - - - - - - - - - - - - ✂", title_style))
        story.append(Spacer(1, 10))
        story.append(Paragraph("<b>--- BOTTOM / RIGHT HALF ---</b>", instruction_style))
        story.extend(render_single_worksheet_content(f_b, "(Form B)" if layout_mode == "half_page_ab" else ""))

    # Append Answer Key Page if requested
    if include_answer_key:
        story.append(PageBreak())
        story.append(Paragraph(f"TEACHER ANSWER KEY & PEDAGOGICAL ALIGNMENT", title_style))
        story.append(Paragraph("<b>Curriculum Alignment:</b> WA CCSS-M 3.OA.A.1, 3.OA.A.4, 3.OA.C.7 | Clear Math Instructional Model", header_style))
        story.append(Spacer(1, 8))
        
        ptype = puzzle_data.get("type")
        if ptype == "riddle":
            story.append(Paragraph(f"<b>Riddle Question:</b> {puzzle_data.get('question')}", story_style))
            story.append(Paragraph(f"<b>SOLVED PUNCHLINE:</b> <font color='black'><b>{puzzle_data.get('punchline')}</b></font>", problem_style))
            story.append(Spacer(1, 8))
            
            # Answer Table
            ak_rows = [["Letter", "Equation", "Answer / Code", "Clear Math Strategy"]]
            for p in puzzle_data.get("problems", []):
                ak_rows.append([
                    p.get("letter", ""),
                    f"{p['factor1']} × {p['factor2']} = {p['product']}",
                    str(p.get("answer")),
                    p.get("strategy", "")
                ])
            ak_table = Table(ak_rows, colWidths=[50, 150, 90, 200])
            ak_table.setStyle(TableStyle([
                ('BOX', (0,0), (-1,-1), 1.5, colors.black),
                ('GRID', (0,0), (-1,-1), 1, colors.black),
                ('BACKGROUND', (0,0), (-1,0), colors.Color(0.9, 0.9, 0.9)),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,-1), 9),
                ('TOPPADDING', (0,0), (-1,-1), 3),
                ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ]))
            story.append(ak_table)
            
        elif ptype == "detective":
            story.append(Paragraph("<b>Sneaky Pete Error Key:</b>", problem_style))
            story.append(Spacer(1, 4))
            ak_rows = [["#", "Equation", "Correct?", "True Product", "Misconception Analysis"]]
            for p in puzzle_data.get("problems", []):
                verdict = "MISTAKE" if p["is_error"] else "CORRECT"
                ak_rows.append([
                    str(p["id"]),
                    f"{p['factor1']} × {p['factor2']} = {p['displayed_answer']}",
                    verdict,
                    str(p["correct_answer"]),
                    p["error_reason"]
                ])
            ak_table = Table(ak_rows, colWidths=[25, 110, 70, 75, 220])
            ak_table.setStyle(TableStyle([
                ('BOX', (0,0), (-1,-1), 1.5, colors.black),
                ('GRID', (0,0), (-1,-1), 1, colors.black),
                ('BACKGROUND', (0,0), (-1,0), colors.Color(0.9, 0.9, 0.9)),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,-1), 8),
                ('TOPPADDING', (0,0), (-1,-1), 3),
                ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ]))
            story.append(ak_table)

        elif ptype == "maze":
            story.append(Paragraph(f"<b>Pathfinder Solution Key:</b>", problem_style))
            story.append(Paragraph(f"Path coordinates (row, col): {puzzle_data.get('path_coords')}", story_style))
            story.append(Spacer(1, 6))
            
            sol_grid = puzzle_data.get("solution_grid", [])
            grid = puzzle_data.get("grid", [])
            disp_rows = []
            for r in range(len(grid)):
                row_items = []
                for c in range(len(grid[0])):
                    if sol_grid[r][c] == 1:
                        row_items.append(f"[PATH]\n{grid[r][c]['text']}")
                    else:
                        row_items.append(grid[r][c]['text'])
                disp_rows.append(row_items)
                
            cell_size = 45
            t_sol = Table(disp_rows, colWidths=[cell_size]*len(grid[0]), rowHeights=[cell_size]*len(grid))
            t_sol.setStyle(TableStyle([
                ('BOX', (0,0), (-1,-1), 1.5, colors.black),
                ('GRID', (0,0), (-1,-1), 1, colors.black),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('FONTSIZE', (0,0), (-1,-1), 7),
            ]))
            story.append(t_sol)

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
