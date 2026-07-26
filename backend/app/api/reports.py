from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Student, Faculty, AnswerScript, Evaluation, Question, Subject, Notification, AuditLog, QuestionPaper
from app.utils.report_generator import ReportGenerator
from app.auth import get_current_user, RoleChecker
from typing import List
import os

router = APIRouter(prefix="/reports", tags=["Reports & Alerts"])

REPORT_DIR = "./generated_reports"
os.makedirs(REPORT_DIR, exist_ok=True)

@router.get("/student-pdf/{script_id}")
def download_student_report(script_id: int, db: Session = Depends(get_db)):
    """
    Triggers generation and downloads a comprehensive PDF evaluation report for a student script.
    """
    script = db.query(AnswerScript).filter(AnswerScript.id == script_id).first()
    if not script:
        raise HTTPException(status_code=404, detail="Answer script not found")

    student_name = "Anonymous Student"
    reg_num = "Auto-detect"
    sub_code = "CS-001"
    
    if script.student:
        reg_num = script.student.register_number
        if script.student.user:
            student_name = script.student.user.name
            
    if script.question_paper and script.question_paper.subject:
        sub_code = script.question_paper.subject.code

    student_info = {
        "name": student_name,
        "register_number": reg_num,
        "subject_code": sub_code,
        "overall_marks": script.overall_marks,
        "max_marks": script.question_paper.max_marks if script.question_paper else 100.0,
        "overall_percentage": script.overall_percentage,
        "evaluation_mode": script.evaluation_mode
    }

    evaluations = db.query(Evaluation).filter(Evaluation.answer_script_id == script_id).all()
    eval_list = []
    
    for ev in evaluations:
        q = db.query(Question).filter(Question.id == ev.question_id).first()
        eval_list.append({
            "question_number": q.question_number if q else "N/A",
            "max_marks": q.max_marks if q else 10.0,
            "marks_awarded": ev.teacher_override_marks if ev.teacher_override_marks is not None else ev.marks_awarded,
            "student_answer_text": ev.student_answer_text,
            "explanation": ev.explanation,
            "missing_keywords": ev.missing_keywords or []
        })

    filename = os.path.join(REPORT_DIR, f"student_report_{script_id}.pdf")
    ReportGenerator.generate_student_pdf(filename, student_info, eval_list)
    
    return FileResponse(filename, media_type="application/pdf", filename=f"report_{reg_num}.pdf")

@router.get("/subject-excel/{qp_id}")
def download_subject_report(qp_id: int, db: Session = Depends(get_db)):
    """
    Compiles grading registers for an exam and exports them to an Excel file.
    """
    qp = db.query(QuestionPaper).filter(QuestionPaper.id == qp_id).first()
    if not qp:
        raise HTTPException(status_code=404, detail="Question paper not found")

    scripts = db.query(AnswerScript).filter(
        AnswerScript.question_paper_id == qp_id,
        AnswerScript.status == "COMPLETED"
    ).all()

    data = []
    for s in scripts:
        student_name = "Anonymous"
        reg_num = "N/A"
        if s.student:
            reg_num = s.student.register_number
            if s.student.user:
                student_name = s.student.user.name
                
        data.append({
            "register_number": reg_num,
            "student_name": student_name,
            "evaluation_mode": s.evaluation_mode,
            "marks": s.overall_marks,
            "percentage": s.overall_percentage,
            "ocr_accuracy": s.ocr_accuracy,
            "confidence_score": s.confidence_score
        })

    headers = ["Register Number", "Student Name", "Evaluation Mode", "Marks", "Percentage", "OCR Accuracy", "Confidence Score"]
    filename = os.path.join(REPORT_DIR, f"subject_marks_{qp_id}.xlsx")
    ReportGenerator.generate_excel(filename, data, headers)

    return FileResponse(
        filename, 
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", 
        filename=f"marks_{qp.exam_name.replace(' ', '_')}.xlsx"
    )

@router.get("/notifications")
def get_notifications(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Returns alerts and notifications targeting the user.
    """
    alerts = db.query(Notification).filter(Notification.user_id == current_user.id).order_by(Notification.created_at.desc()).all()
    return [{"id": a.id, "title": a.title, "message": a.message, "is_read": a.is_read, "type": a.type, "created_at": a.created_at} for a in alerts]

@router.post("/notifications/{alert_id}/read")
def mark_read(alert_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Flags an alert notification as acknowledged.
    """
    alert = db.query(Notification).filter(Notification.id == alert_id, Notification.user_id == current_user.id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Notification not found")
    alert.is_read = True
    db.commit()
    return {"message": "Notification marked read"}

@router.get("/audit-logs")
def get_logs(db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["SUPER_ADMIN", "ADMIN"]))):
    """
    Retrieves system activity logs for administrative tracking.
    """
    logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(100).all()
    res = []
    for l in logs:
        res.append({
            "id": l.id,
            "timestamp": l.timestamp,
            "action": l.action,
            "details": l.details,
            "ip_address": l.ip_address,
            "user_email": l.user.email if l.user else "System"
        })
    return res
