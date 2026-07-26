import os
import datetime
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from typing import List, Dict, Any

class ReportGenerator:
    @staticmethod
    def generate_excel(filename: str, data: List[Dict[str, Any]], headers: List[str]) -> str:
        """
        Creates a custom formatted Excel sheet containing students' grading results.
        """
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "SmartEval AI Results"
        
        # Design system header fonts (Navy Blue primary)
        header_font = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="1A365D", end_color="1A365D", fill_type="solid")
        center_align = Alignment(horizontal="center", vertical="center")
        
        # Set headers
        for col_idx, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_idx)
            cell.value = header
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = center_align
            
        # Set row data
        for row_idx, record in enumerate(data, 2):
            for col_idx, header in enumerate(headers, 1):
                cell = ws.cell(row=row_idx, column=col_idx)
                # Lookup property by lowercasing headers
                key = header.lower().replace(" ", "_")
                cell.value = record.get(key, "")
                cell.alignment = Alignment(horizontal="left" if col_idx <= 2 else "center")
                
        # Auto-adjust column width boundaries
        for col in ws.columns:
            max_len = 0
            for cell in col:
                val = str(cell.value or '')
                if len(val) > max_len:
                    max_len = len(val)
            ws.column_dimensions[col[0].column_letter].width = max(max_len + 3, 12)
            
        wb.save(filename)
        return filename

    @staticmethod
    def generate_student_pdf(filename: str, student_info: Dict[str, Any], evaluations: List[Dict[str, Any]]) -> str:
        """
        Generates a professional PDF report containing question scores, OCR text, and Explainable AI feedback.
        """
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        c = canvas.Canvas(filename, pagesize=letter)
        width, height = letter
        
        # Report Header
        c.setFillColorRGB(0.06, 0.09, 0.16)  # Dark slate
        c.rect(0, height - 80, width, 80, fill=True, stroke=False)
        
        c.setFillColorRGB(1.0, 1.0, 1.0)
        c.setFont("Helvetica-Bold", 20)
        c.drawString(40, height - 40, "SMARTEVAL AI - STUDENT REPORT CARD")
        
        c.setFont("Helvetica", 9)
        c.setFillColorRGB(0.8, 0.8, 0.8)
        now_str = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        c.drawString(40, height - 60, f"Generated: {now_str}")
        
        # Reset color to black
        c.setFillColorRGB(0.0, 0.0, 0.0)
        
        # Metadata section
        c.setFont("Helvetica-Bold", 11)
        c.drawString(40, height - 110, "Student Profile")
        c.setFont("Helvetica", 10)
        c.drawString(40, height - 130, f"Name: {student_info.get('name', 'N/A')}")
        c.drawString(40, height - 145, f"Register Number: {student_info.get('register_number', 'N/A')}")
        c.drawString(40, height - 160, f"Subject Code: {student_info.get('subject_code', 'N/A')}")
        
        # Grade statistics box
        c.setFillColorRGB(0.96, 0.96, 0.98)
        c.rect(340, height - 165, 230, 65, fill=True, stroke=True)
        c.setFillColorRGB(0.0, 0.0, 0.0)
        
        c.setFont("Helvetica-Bold", 10)
        c.drawString(350, height - 120, "Evaluation Statistics")
        c.setFont("Helvetica", 9)
        c.drawString(350, height - 138, f"Score: {student_info.get('overall_marks', 0.0)} / {student_info.get('max_marks', 100.0)}")
        c.drawString(350, height - 152, f"Percentage: {student_info.get('overall_percentage', 0.0)}%  (Evaluation: {student_info.get('evaluation_mode', 'STANDARD')})")
        
        c.setStrokeColorRGB(0.8, 0.8, 0.8)
        c.line(40, height - 180, width - 40, height - 180)
        
        # Loop over individual answers
        y = height - 205
        c.setFont("Helvetica-Bold", 12)
        c.drawString(40, y, "Question Breakdown & AI Feedback")
        y -= 25
        
        for ev in evaluations:
            if y < 120:
                c.showPage()
                # Redraw basic header boundary on subsequent pages
                c.setFillColorRGB(0.06, 0.09, 0.16)
                c.rect(0, height - 40, width, 40, fill=True, stroke=False)
                c.setFillColorRGB(1.0, 1.0, 1.0)
                c.setFont("Helvetica-Bold", 12)
                c.drawString(40, height - 25, "Question Breakdown (Continued)")
                c.setFillColorRGB(0.0, 0.0, 0.0)
                y = height - 70
                
            c.setFont("Helvetica-Bold", 10)
            c.drawString(40, y, f"Question {ev.get('question_number')}: Score {ev.get('marks_awarded', 0.0)} / {ev.get('max_marks', 10.0)}")
            y -= 15
            
            # Show snippet of answer
            c.setFont("Helvetica-Bold", 9)
            c.drawString(55, y, "OCR Scanned Answer:")
            y -= 12
            c.setFont("Helvetica", 9)
            ans = ev.get('student_answer_text', '') or ''
            # Simple text wrap
            ans_snippet = (ans[:110] + "...") if len(ans) > 110 else ans
            c.drawString(65, y, ans_snippet)
            y -= 16
            
            # Show explanation feedback
            c.setFont("Helvetica-Bold", 9)
            c.drawString(55, y, "AI Explanatory Reasoning:")
            y -= 12
            c.setFont("Helvetica", 9)
            exp = ev.get('explanation', '') or 'No explanation provided.'
            exp_snippet = (exp[:110] + "...") if len(exp) > 110 else exp
            c.drawString(65, y, exp_snippet)
            y -= 18
            
            # Show keywords feedback
            missing_kw = ev.get('missing_keywords', []) or []
            if missing_kw:
                c.setFont("Helvetica-Oblique", 9)
                c.setFillColorRGB(0.7, 0.1, 0.1)
                c.drawString(55, y, f"Missing Concepts/Keywords: {', '.join(missing_kw)}")
                c.setFillColorRGB(0.0, 0.0, 0.0)
                y -= 15
                
            # Horizontal spacer between items
            c.setStrokeColorRGB(0.9, 0.9, 0.9)
            c.line(40, y, width - 40, y)
            y -= 15
            
        c.save()
        return filename
