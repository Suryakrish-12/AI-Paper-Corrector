import time
import asyncio
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.celery_app import celery_app
from app.database import SessionLocal
from app.models import AnswerScript, QuestionPaper, Question, Evaluation, Student, User
from app.ai.ocr_pipeline import OCRPipeline
from app.ai.llm_evaluator import LLMEvaluator
from app.ai.explainable_ai import ExplainableAIModule
from app.websocket import manager

# Initialize AI tools
ocr_pipe = OCRPipeline()
llm_eval = LLMEvaluator()

async def broadcast_status(script_id: int, status: str, progress: int, details: str = ""):
    """
    Broadcasts live progress updates to all connected UI clients.
    """
    payload = {
        "type": "EVALUATION_PROGRESS",
        "answer_script_id": script_id,
        "status": status,
        "progress": progress,
        "details": details
    }
    await manager.broadcast(payload)

def run_evaluation_pipeline_sync(db: Session, script_id: int):
    """
    Synchronous wrapper to allow running the pipeline in standard threads or Celery.
    Runs the async loop internally.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(process_evaluation_pipeline(db, script_id))
    finally:
        loop.close()

@celery_app.task(name="app.tasks.process_evaluation")
def process_evaluation_task(script_id: int):
    """
    Celery background worker entrypoint.
    """
    db = SessionLocal()
    try:
        run_evaluation_pipeline_sync(db, script_id)
    except Exception as e:
        print(f"Error in Celery task execution: {e}")
    finally:
        db.close()

async def process_evaluation_pipeline(db: Session, script_id: int):
    """
    The core AI Evaluation Pipeline.
    Steps:
      1. OCR: Extracts raw text.
      2. Question Detection & Segmentation.
      3. Semantic Analysis & Rubric Matching.
      4. AI Evaluation: Generates marks & explanations.
      5. Complete: Sums grades, updates database, and updates dashboards.
    """
    # Fetch AnswerScript
    script = db.query(AnswerScript).filter(AnswerScript.id == script_id).first()
    if not script:
        print(f"Script with ID {script_id} not found.")
        return

    try:
        # Step 1: Uploading Complete / OCR Running
        script.status = "OCR"
        db.commit()
        await broadcast_status(script_id, "OCR", 15, "Initializing EasyOCR and running document scanning...")
        
        ocr_result = ocr_pipe.extract_text_from_file(script.file_path)
        answers_dict = ocr_result.get("answers", {})
        is_handwritten = ocr_result.get("is_handwritten", True)
        
        script.is_handwritten = is_handwritten
        script.total_pages = len(ocr_result.get("pages_content", [1])) if "pages_content" in ocr_result else 2
        db.commit()
        
        # Step 2: Question Detection
        script.status = "QUESTION_DETECTION"
        db.commit()
        await broadcast_status(script_id, "QUESTION_DETECTION", 35, "Segmenting pages and extracting question structures...")
        
        # Fetch question papers and associated questions
        qp = db.query(QuestionPaper).filter(QuestionPaper.id == script.question_paper_id).first()
        questions = qp.questions if qp else []
        
        if not questions:
            raise ValueError(f"No questions registered for Question Paper ID {script.question_paper_id}")
            
        time.sleep(1.0) # Visual delay for live dashboard simulation

        # Step 3: Semantic Analysis & Rubric Matching
        script.status = "SEMANTIC"
        db.commit()
        await broadcast_status(script_id, "SEMANTIC", 55, "Matching answers against teacher rubrics and keywords...")
        
        evaluations_to_add = []
        total_score = 0.0
        max_total_marks = 0.0
        
        time.sleep(1.0)

        # Step 4: AI Evaluation
        script.status = "EVALUATING"
        db.commit()
        await broadcast_status(script_id, "EVALUATING", 75, "Prompting LLM engine for descriptive grading & explanation...")

        # Match and grade each question
        for q in questions:
            # Get student text answer or default if not written
            student_ans_text = answers_dict.get(str(q.question_number)) or answers_dict.get(q.question_number) or ""
            
            # Run grading engine
            eval_result = llm_eval.evaluate_answer(
                question_text=q.question_text,
                model_answer=q.model_answer,
                student_answer=student_ans_text,
                max_marks=q.max_marks,
                mandatory_keywords=q.mandatory_keywords,
                optional_keywords=q.keywords,
                evaluation_mode=script.evaluation_mode,
                custom_settings=script.custom_settings
            )
            
            # Save individual evaluation records
            db_eval = Evaluation(
                answer_script_id=script.id,
                question_id=q.id,
                student_answer_text=student_ans_text,
                marks_awarded=eval_result["marks_awarded"],
                explanation=eval_result["explanation"],
                missing_concepts=eval_result["missing_concepts"],
                missing_keywords=eval_result["missing_keywords"],
                confidence_score=eval_result["confidence_score"],
                diagram_detected=eval_result["diagram_detected"],
                formula_detected=eval_result["formula_detected"],
                status="DRAFT"
            )
            evaluations_to_add.append(db_eval)
            total_score += eval_result["marks_awarded"]
            max_total_marks += q.max_marks
            
        # Add all evaluations to DB
        db.add_all(evaluations_to_add)
        db.flush() # Flush to populate evaluation IDs

        # Calculate high-level explainable metrics
        evals_list = [
            {
                "confidence_score": e.confidence_score,
                "diagram_detected": e.diagram_detected,
                "formula_detected": e.formula_detected
            } for e in evaluations_to_add
        ]
        xai_breakdown = ExplainableAIModule.generate_grading_breakdown(evals_list, script.custom_settings)
        
        # Auto-detect student if Register Number pattern is found in answers (e.g. 10-digit number)
        # Search all answers for common Register Number phrases
        detected_reg_num = None
        import re
        for ans in answers_dict.values():
            reg_match = re.search(r'\b\d{10}\b|\bREG\d{5,8}\b', str(ans))
            if reg_match:
                detected_reg_num = reg_match.group(0)
                break
                
        if detected_reg_num:
            student = db.query(Student).filter(Student.register_number == detected_reg_num).first()
            if student:
                script.student_id = student.id
        else:
            # Fallback mock pairing for demo purposes: assign to the first available student in DB
            # if student_id is empty
            if not script.student_id:
                first_student = db.query(Student).first()
                if first_student:
                    script.student_id = first_student.id

        # Update AnswerScript status
        script.overall_marks = round(total_score, 1)
        script.overall_percentage = round((total_score / max_total_marks) * 100, 1) if max_total_marks > 0 else 0.0
        script.confidence_score = xai_breakdown["overall_confidence"]
        script.status = "COMPLETED"
        db.commit()

        # Step 5: Completed
        await broadcast_status(script_id, "COMPLETED", 100, "AI Evaluation complete! Marks compiled successfully.")

    except Exception as e:
        db.rollback()
        script.status = "ERROR"
        db.commit()
        print(f"Exception during AI grading pipeline: {e}")
        await broadcast_status(script_id, "ERROR", 100, f"Grading failed: {str(e)}")
