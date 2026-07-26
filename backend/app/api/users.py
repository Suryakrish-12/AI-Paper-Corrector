from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Student, Faculty, Department, Course, Subject
from app.auth import get_current_user, RoleChecker
from typing import List

router = APIRouter(prefix="/users", tags=["Users Management"])

@router.get("/students")
def get_students(db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["SUPER_ADMIN", "ADMIN", "HOD", "FACULTY"]))):
    """
    Returns list of students with academic details.
    """
    students = db.query(Student).all()
    res = []
    for s in students:
        res.append({
            "id": s.id,
            "name": s.user.name if s.user else "Deleted Student",
            "email": s.user.email if s.user else "",
            "register_number": s.register_number,
            "department": s.department.name if s.department else "N/A",
            "course": s.course.name if s.course else "N/A",
            "semester": s.semester
        })
    return res

@router.get("/faculty")
def get_faculty(db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["SUPER_ADMIN", "ADMIN", "HOD"]))):
    """
    Returns list of academic faculty members.
    """
    faculty = db.query(Faculty).all()
    res = []
    for f in faculty:
        res.append({
            "id": f.id,
            "name": f.user.name if f.user else "Deleted Faculty",
            "email": f.user.email if f.user else "",
            "department": f.department.name if f.department else "N/A",
            "designation": f.designation
        })
    return res

@router.get("/departments")
def get_departments(db: Session = Depends(get_db)):
    """
    Returns departments for select options.
    """
    depts = db.query(Department).all()
    return [{"id": d.id, "name": d.name, "code": d.code} for d in depts]

@router.get("/courses")
def get_courses(db: Session = Depends(get_db)):
    """
    Returns course lists for select options.
    """
    courses = db.query(Course).all()
    return [{"id": c.id, "name": c.name, "code": c.code, "department_id": c.department_id} for c in courses]

@router.get("/subjects")
def get_subjects(db: Session = Depends(get_db)):
    """
    Returns list of subjects.
    """
    subjects = db.query(Subject).all()
    return [{"id": s.id, "name": s.name, "code": s.code, "credit": s.credit} for s in subjects]
