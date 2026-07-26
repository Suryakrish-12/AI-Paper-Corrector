import os
import sys

# Ensure backend folder is in PATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from app.ai.ocr_pipeline import OCRPipeline
from app.ai.nlp_engine import NLPEngine
from app.ai.llm_evaluator import LLMEvaluator

def test_ocr_pipeline():
    """
    Checks that OCR parsing outputs mapped student response segments based on filename patterns.
    """
    pipe = OCRPipeline()
    res = pipe.extract_text_from_file("student_excellent_algorithms.pdf")
    assert res["type"] == "answer_script"
    assert "1" in res["answers"]
    assert "stack" in res["answers"]["1"].lower()

def test_nlp_similarity():
    """
    Verifies cosine semantic similarity thresholds return scoring differentials.
    """
    nlp = NLPEngine()
    sim = nlp.calculate_similarity(
        "A stack is a linear LIFO structure where elements are pushed/popped from top pointer.",
        "Stack is LIFO structure. Plates stack is an example."
    )
    assert sim >= 0.4
    
    # Verify exact match
    assert nlp.calculate_similarity("TCP handshake", "TCP handshake") == 1.0

def test_llm_evaluator():
    """
    Asserts that the LLM engine grades student submissions and provides feedback explanations.
    """
    evaluator = LLMEvaluator()
    res = evaluator.evaluate_answer(
        question_text="Define stack and queue.",
        model_answer="Stack LIFO, Queue FIFO.",
        student_answer="Stack is LIFO. Queue is FIFO.",
        max_marks=10.0,
        mandatory_keywords=["LIFO", "FIFO"],
        optional_keywords=["plates"]
    )
    assert "marks_awarded" in res
    assert "explanation" in res
    assert "missing_concepts" in res
    assert res["marks_awarded"] > 5.0
