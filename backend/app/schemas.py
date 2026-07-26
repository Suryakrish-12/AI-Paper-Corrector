from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime

# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    name: str
    role: str  # SUPER_ADMIN, ADMIN, HOD, FACULTY, STUDENT

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    password: Optional[str] = None

class UserResponse(UserBase):
    id: int
    is_verified: bool
    created_at: datetime
    student_id: Optional[int] = None
    faculty_id: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)

# Profile Details
class StudentProfileResponse(BaseModel):
    id: int
    register_number: str
    department_id: int
    course_id: int
    semester: int
    
    model_config = ConfigDict(from_attributes=True)

class FacultyProfileResponse(BaseModel):
    id: int
    department_id: int
    designation: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

# Subject & Course Schemas
class SubjectBase(BaseModel):
    name: str
    code: str
    credit: int = 3

class SubjectCreate(SubjectBase):
    course_id: int

class SubjectResponse(SubjectBase):
    id: int
    course_id: int
    
    model_config = ConfigDict(from_attributes=True)

# Question Schemas
class QuestionBase(BaseModel):
    question_number: str
    question_text: str
    max_marks: float
    keywords: Optional[List[str]] = []
    mandatory_keywords: Optional[List[str]] = []
    model_answer: Optional[str] = None

class QuestionCreate(QuestionBase):
    pass

class QuestionResponse(QuestionBase):
    id: int
    question_paper_id: int
    
    model_config = ConfigDict(from_attributes=True)

# Question Paper Schemas
class QuestionPaperBase(BaseModel):
    exam_name: str
    academic_year: str
    max_marks: float = 100.0
    passing_marks: float = 40.0

class QuestionPaperCreate(QuestionPaperBase):
    subject_code: str
    questions: List[QuestionBase]

class QuestionPaperResponse(QuestionPaperBase):
    id: int
    subject_id: int
    status: str
    total_questions: int
    created_by_faculty_id: int
    created_at: datetime
    questions: List[QuestionResponse] = []
    
    model_config = ConfigDict(from_attributes=True)

# Evaluation settings
class CustomEvaluationSettings(BaseModel):
    definition_marks: Optional[float] = 1.0
    formula_marks: Optional[float] = 1.0
    diagram_marks: Optional[float] = 1.0
    example_marks: Optional[float] = 1.0
    conclusion_marks: Optional[float] = 1.0
    grammar_weight: Optional[float] = 0.1
    negative_marking: Optional[bool] = False
    partial_marking: Optional[bool] = True
    semantic_similarity_threshold: Optional[float] = 0.6
    diagram_mandatory: Optional[bool] = False
    word_limit: Optional[int] = 500
    spelling_tolerance: Optional[str] = "moderate" # none, moderate, high
    strictness_slider: Optional[float] = 0.5 # 0.0 to 1.0
    confidence_threshold: Optional[float] = 0.7
    passing_criteria: Optional[float] = 40.0

# Answer Script Schemas
class AnswerScriptUpload(BaseModel):
    question_paper_id: int
    evaluation_mode: str = "STANDARD" # LIBERAL, STANDARD, STRICT, CUSTOM
    custom_settings: Optional[CustomEvaluationSettings] = None
    is_handwritten: Optional[bool] = True

class AnswerScriptResponse(BaseModel):
    id: int
    student_id: Optional[int] = None
    question_paper_id: int
    file_path: str
    status: str
    is_handwritten: bool
    total_pages: int
    file_type: str
    evaluation_mode: str
    overall_marks: Optional[float] = None
    overall_percentage: Optional[float] = None
    ocr_accuracy: float
    ai_accuracy: float
    confidence_score: float
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# Evaluation Schemas
class EvaluationResponse(BaseModel):
    id: int
    answer_script_id: int
    question_id: int
    student_answer_text: Optional[str] = None
    marks_awarded: Optional[float] = None
    explanation: Optional[str] = None
    missing_concepts: Optional[List[str]] = []
    missing_keywords: Optional[List[str]] = []
    confidence_score: float
    diagram_detected: bool
    formula_detected: bool
    status: str
    teacher_override_marks: Optional[float] = None
    teacher_notes: Optional[str] = None
    evaluated_at: datetime
    question: Optional[QuestionResponse] = None
    
    model_config = ConfigDict(from_attributes=True)

class EvaluationOverride(BaseModel):
    teacher_override_marks: float
    teacher_notes: Optional[str] = None

# Dashboard Analytics Schemas
class DashboardStatsResponse(BaseModel):
    total_students: int
    processed: int
    remaining: int
    average_marks: float
    highest_marks: float
    lowest_marks: float
    ocr_accuracy: float
    ai_accuracy: float
    review_queue_count: int
    low_confidence_count: int

# Report Schemas
class ReportResponse(BaseModel):
    id: int
    name: str
    type: str
    target_id: int
    file_path: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# Notification Schemas
class NotificationResponse(BaseModel):
    id: int
    title: str
    message: str
    is_read: bool
    type: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# Audit Log Schemas
class AuditLogResponse(BaseModel):
    id: int
    action: str
    details: Optional[str] = None
    ip_address: Optional[str] = None
    timestamp: datetime
    user_email: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)
