import datetime
from typing import Optional
from sqlalchemy import (
    Column, Integer, String, Boolean, ForeignKey, DateTime, Float, Text, JSON, Table
)
from sqlalchemy.orm import relationship
from app.database import Base

# Association table for Student - Course enrollments
student_subject_association = Table(
    'student_subject',
    Base.metadata,
    Column('student_id', Integer, ForeignKey('students.id', ondelete='CASCADE'), primary_key=True),
    Column('subject_id', Integer, ForeignKey('subjects.id', ondelete='CASCADE'), primary_key=True)
)

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    name = Column(String, nullable=False)
    role = Column(String, nullable=False)  # SUPER_ADMIN, ADMIN, HOD, FACULTY, STUDENT
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    student_profile = relationship("Student", uselist=False, back_populates="user", cascade="all, delete-orphan")
    faculty_profile = relationship("Faculty", uselist=False, back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user")
    notifications = relationship("Notification", back_populates="user")

    @property
    def student_id(self) -> Optional[int]:
        return self.student_profile.id if self.student_profile else None

    @property
    def faculty_id(self) -> Optional[int]:
        return self.faculty_profile.id if self.faculty_profile else None



class Institution(Base):
    __tablename__ = 'institutions'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    code = Column(String, unique=True, nullable=False)
    address = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    departments = relationship("Department", back_populates="institution", cascade="all, delete-orphan")


class Department(Base):
    __tablename__ = 'departments'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    code = Column(String, nullable=False)
    institution_id = Column(Integer, ForeignKey('institutions.id', ondelete='CASCADE'), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    institution = relationship("Institution", back_populates="departments")
    courses = relationship("Course", back_populates="department", cascade="all, delete-orphan")
    faculty = relationship("Faculty", back_populates="department")
    students = relationship("Student", back_populates="department")


class Course(Base):
    __tablename__ = 'courses'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    code = Column(String, nullable=False)
    department_id = Column(Integer, ForeignKey('departments.id', ondelete='CASCADE'), nullable=False)
    semester = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    department = relationship("Department", back_populates="courses")
    subjects = relationship("Subject", back_populates="course", cascade="all, delete-orphan")
    students = relationship("Student", back_populates="course")


class Subject(Base):
    __tablename__ = 'subjects'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    code = Column(String, unique=True, nullable=False)
    course_id = Column(Integer, ForeignKey('courses.id', ondelete='CASCADE'), nullable=False)
    credit = Column(Integer, default=3)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    course = relationship("Course", back_populates="subjects")
    question_papers = relationship("QuestionPaper", back_populates="subject", cascade="all, delete-orphan")
    students = relationship("Student", secondary=student_subject_association, back_populates="subjects")


class Student(Base):
    __tablename__ = 'students'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    register_number = Column(String, unique=True, nullable=False, index=True)
    department_id = Column(Integer, ForeignKey('departments.id'), nullable=False)
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False)
    semester = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="student_profile")
    department = relationship("Department", back_populates="students")
    course = relationship("Course", back_populates="students")
    subjects = relationship("Subject", secondary=student_subject_association, back_populates="students")
    answer_scripts = relationship("AnswerScript", back_populates="student", cascade="all, delete-orphan")


class Faculty(Base):
    __tablename__ = 'faculty'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    department_id = Column(Integer, ForeignKey('departments.id'), nullable=False)
    designation = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="faculty_profile")
    department = relationship("Department", back_populates="faculty")
    question_papers = relationship("QuestionPaper", back_populates="faculty")


class QuestionPaper(Base):
    __tablename__ = 'question_papers'
    
    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey('subjects.id', ondelete='CASCADE'), nullable=False)
    exam_name = Column(String, nullable=False)
    academic_year = Column(String, nullable=False)
    max_marks = Column(Float, default=100.0)
    passing_marks = Column(Float, default=40.0)
    file_path = Column(String, nullable=True)
    status = Column(String, default="PENDING")  # PENDING, PROCESSING, COMPLETED, ERROR
    total_questions = Column(Integer, default=0)
    created_by_faculty_id = Column(Integer, ForeignKey('faculty.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    subject = relationship("Subject", back_populates="question_papers")
    faculty = relationship("Faculty", back_populates="question_papers")
    questions = relationship("Question", back_populates="question_paper", cascade="all, delete-orphan")
    answer_scripts = relationship("AnswerScript", back_populates="question_paper")


class Question(Base):
    __tablename__ = 'questions'
    
    id = Column(Integer, primary_key=True, index=True)
    question_paper_id = Column(Integer, ForeignKey('question_papers.id', ondelete='CASCADE'), nullable=False)
    question_number = Column(String, nullable=False)  # 1a, 1b, 2, etc.
    question_text = Column(Text, nullable=False)
    max_marks = Column(Float, nullable=False)
    keywords = Column(JSON, nullable=True)  # List of optional keywords
    mandatory_keywords = Column(JSON, nullable=True)  # List of mandatory keywords
    model_answer = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    question_paper = relationship("QuestionPaper", back_populates="questions")
    rubrics = relationship("Rubric", back_populates="question", cascade="all, delete-orphan")
    evaluations = relationship("Evaluation", back_populates="question", cascade="all, delete-orphan")


class Rubric(Base):
    __tablename__ = 'rubrics'
    
    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey('questions.id', ondelete='CASCADE'), nullable=False)
    criteria_name = Column(String, nullable=False)  # definition, diagram, explanation, formula, grammar
    max_marks = Column(Float, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    question = relationship("Question", back_populates="rubrics")


class AnswerScript(Base):
    __tablename__ = 'answer_scripts'
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey('students.id', ondelete='CASCADE'), nullable=True)  # Can be null if auto-detecting
    question_paper_id = Column(Integer, ForeignKey('question_papers.id', ondelete='CASCADE'), nullable=False)
    file_path = Column(String, nullable=False)
    status = Column(String, default="UPLOADING")  # UPLOADING, OCR, QUESTION_DETECTION, SEMANTIC, EVALUATING, COMPLETED, ERROR
    is_handwritten = Column(Boolean, default=True)
    total_pages = Column(Integer, default=0)
    file_type = Column(String, default="PDF")  # PDF, IMAGE, ZIP, FOLDER
    evaluation_mode = Column(String, default="STANDARD")  # LIBERAL, STANDARD, STRICT, CUSTOM
    custom_settings = Column(JSON, nullable=True)  # Weights for custom evaluation rules
    overall_marks = Column(Float, nullable=True)
    overall_percentage = Column(Float, nullable=True)
    ocr_accuracy = Column(Float, default=95.0)
    ai_accuracy = Column(Float, default=90.0)
    confidence_score = Column(Float, default=1.0)  # Average question confidence
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    student = relationship("Student", back_populates="answer_scripts")
    question_paper = relationship("QuestionPaper", back_populates="answer_scripts")
    evaluations = relationship("Evaluation", back_populates="answer_script", cascade="all, delete-orphan")


class Evaluation(Base):
    __tablename__ = 'evaluations'
    
    id = Column(Integer, primary_key=True, index=True)
    answer_script_id = Column(Integer, ForeignKey('answer_scripts.id', ondelete='CASCADE'), nullable=False)
    question_id = Column(Integer, ForeignKey('questions.id', ondelete='CASCADE'), nullable=False)
    student_answer_text = Column(Text, nullable=True)
    marks_awarded = Column(Float, nullable=True)
    explanation = Column(Text, nullable=True)
    missing_concepts = Column(JSON, nullable=True)  # List of missing ideas
    missing_keywords = Column(JSON, nullable=True)  # List of missing keywords
    confidence_score = Column(Float, default=1.0)
    diagram_detected = Column(Boolean, default=False)
    formula_detected = Column(Boolean, default=False)
    status = Column(String, default="DRAFT")  # DRAFT, APPROVED
    teacher_override_marks = Column(Float, nullable=True)
    teacher_notes = Column(Text, nullable=True)
    evaluated_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    answer_script = relationship("AnswerScript", back_populates="evaluations")
    question = relationship("Question", back_populates="evaluations")


class Report(Base):
    __tablename__ = 'reports'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # STUDENT, CLASS, SUBJECT, DEPARTMENT, INSTITUTION, TOPIC, QUESTION
    target_id = Column(Integer, nullable=False)  # ID of Student, Class/Course, etc.
    file_path = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class Analytics(Base):
    __tablename__ = 'analytics'
    
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False)  # STUDENT, CLASS, SUBJECT, DEPARTMENT, INSTITUTION
    target_id = Column(Integer, nullable=False)
    data = Column(JSON, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class Notification(Base):
    __tablename__ = 'notifications'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    type = Column(String, default="INFO")  # EVALUATION_COMPLETED, REVIEW_REQUIRED, SYSTEM_ALERT, INFO
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="notifications")


class AuditLog(Base):
    __tablename__ = 'audit_logs'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    action = Column(String, nullable=False)
    details = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
