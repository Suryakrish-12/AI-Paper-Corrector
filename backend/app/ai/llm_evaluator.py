import json
import time
from typing import Dict, Any, List
from app.config import settings
from app.ai.nlp_engine import NLPEngine

openai_client = None
if not settings.USE_MOCK_AI and settings.OPENAI_API_KEY:
    try:
        from openai import OpenAI
        openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
    except Exception as e:
        print(f"Failed to initialize OpenAI client: {e}. Running rule-based grading.")

class LLMEvaluator:
    def __init__(self):
        self.nlp = NLPEngine()
        self.use_mock = settings.USE_MOCK_AI or (openai_client is None)

    def evaluate_answer(
        self,
        question_text: str,
        model_answer: str,
        student_answer: str,
        max_marks: float,
        mandatory_keywords: List[str],
        optional_keywords: List[str],
        evaluation_mode: str = "STANDARD",
        custom_settings: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Evaluates a single student answer.
        Returns a dict containing:
          - marks_awarded (float)
          - explanation (str)
          - missing_concepts (list[str])
          - missing_keywords (list[str])
          - confidence_score (float)
          - diagram_detected (bool)
          - formula_detected (bool)
        """
        print(f"Evaluating answer with mode: {evaluation_mode}")
        
        # 1. Check if we should use the live LLM
        if not self.use_mock:
            try:
                return self._evaluate_with_openai(
                    question_text, model_answer, student_answer, max_marks,
                    mandatory_keywords, optional_keywords, evaluation_mode, custom_settings
                )
            except Exception as e:
                print(f"OpenAI evaluation failed: {e}. Falling back to rule-based analysis.")

        # 2. Rule-Based grading fallback
        return self._evaluate_rule_based(
            question_text, model_answer, student_answer, max_marks,
            mandatory_keywords, optional_keywords, evaluation_mode, custom_settings
        )

    def _evaluate_with_openai(
        self,
        question_text: str,
        model_answer: str,
        student_answer: str,
        max_marks: float,
        mandatory_keywords: List[str],
        optional_keywords: List[str],
        evaluation_mode: str,
        custom_settings: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        # Formulate strictness details for the system prompt
        strictness_info = ""
        if evaluation_mode == "LIBERAL":
            strictness_info = "Be extremely generous. Ignore minor grammar/spelling errors. Award partial marks even for incomplete definitions if the direction is correct."
        elif evaluation_mode == "STRICT":
            strictness_info = "Be highly strict. Mandatory keywords must be present verbatim. Penalize spelling, incomplete ideas, and bad logic. No soft marks."
        elif evaluation_mode == "CUSTOM" and custom_settings:
            strictness_info = f"Apply these custom weights and thresholds: {json.dumps(custom_settings)}"
        else:
            strictness_info = "Perform standard academic grading. Balanced strictness. Grade based on keyword matches and concept coverage."

        prompt = f"""
        You are an expert academic evaluator. Grade the student's answer based on the Question, Model Answer, and evaluation rules.
        
        Question: {question_text}
        Max Marks: {max_marks}
        Model Answer: {model_answer}
        Mandatory Keywords: {mandatory_keywords}
        Optional Keywords: {optional_keywords}
        
        Student's Answer: {student_answer}
        
        Strictness Rules: {strictness_info}
        
        Evaluate the answer and return a JSON object with the following fields:
        {{
            "marks_awarded": float (from 0 to {max_marks}),
            "explanation": "Detailed professional feedback detailing why these marks were given, referencing parts of the student answer.",
            "missing_concepts": ["concept 1", "concept 2"],
            "missing_keywords": ["keyword 1", "keyword 2"],
            "confidence_score": float (from 0.0 to 1.0 indicating your confidence in the OCR scan quality and matching),
            "diagram_detected": boolean,
            "formula_detected": boolean
        }}
        
        Ensure your response contains ONLY the raw JSON string. Do not wrap it in markdown codeblocks.
        """

        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a professional examination evaluator returning structured JSON output."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.2
        )
        
        result_json = response.choices[0].message.content
        return json.loads(result_json)

    def _evaluate_rule_based(
        self,
        question_text: str,
        model_answer: str,
        student_answer: str,
        max_marks: float,
        mandatory_keywords: List[str],
        optional_keywords: List[str],
        evaluation_mode: str,
        custom_settings: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        # Simulate processing delay
        time.sleep(0.5)

        # 1. Analyze similarity and keywords
        similarity = self.nlp.calculate_similarity(student_answer, model_answer)
        kw_match = self.nlp.check_keywords(student_answer, mandatory_keywords, optional_keywords)
        
        # 2. Check for formulas and diagrams based on textual patterns
        has_formula = any(char in student_answer for char in ["=", "+", "-", "/", "*", "P(", "O(", "O(log"])
        has_diagram = any(word in student_answer.lower() for word in ["diagram", "delineate", "depicts", "flowchart", "[tcp", "client-server"])

        # Determine weight parameters based on mode
        min_similarity_threshold = 0.5
        keyword_weight = 0.5
        similarity_weight = 0.5
        strictness_level = 0.5
        
        if evaluation_mode == "LIBERAL":
            min_similarity_threshold = 0.4
            keyword_weight = 0.3
            similarity_weight = 0.7
            strictness_level = 0.2
        elif evaluation_mode == "STRICT":
            min_similarity_threshold = 0.7
            keyword_weight = 0.7
            similarity_weight = 0.3
            strictness_level = 0.9
        elif evaluation_mode == "CUSTOM" and custom_settings:
            # Custom parsing
            min_similarity_threshold = custom_settings.get("semantic_similarity_threshold", 0.5)
            strictness_level = custom_settings.get("strictness_slider", 0.5)
            # Adjust weights based on spelling tolerances or other custom values
            if custom_settings.get("spelling_tolerance") == "none":
                strictness_level += 0.1
                
        # Calculate grade components
        mand_total = len(mandatory_keywords) if mandatory_keywords else 0
        mand_found = len(kw_match["found_mandatory"])
        mand_ratio = (mand_found / mand_total) if mand_total > 0 else 1.0

        opt_total = len(optional_keywords) if optional_keywords else 0
        opt_found = len(kw_match["found_optional"])
        opt_ratio = (opt_found / opt_total) if opt_total > 0 else 1.0

        # Weighted keyword score
        kw_score = (mand_ratio * 0.7) + (opt_ratio * 0.3)

        # Adjust score based on strictness
        if strictness_level > 0.7:
            # High strictness: require high similarity and keywords
            base_score = (kw_score * 0.8) + (similarity * 0.2)
            if mand_ratio < 1.0:  # Missing mandatory keywords drops score significantly
                base_score *= 0.7
        elif strictness_level < 0.3:
            # Liberal grading: generous semantic credit
            base_score = max(similarity, kw_score) * 1.1
        else:
            base_score = (kw_score * 0.5) + (similarity * 0.5)

        # Cap score between 0.0 and 1.0
        base_score = max(0.0, min(1.0, base_score))
        marks_awarded = round(base_score * max_marks, 1)

        # Generate explanatory texts
        missing_concepts = []
        explanation_parts = []
        
        # Tailored explanations based on the student's answer content
        if "stack" in student_answer.lower() and "fifo" in student_answer.lower() and "lifo" in student_answer.lower():
            if "stack is fifo" in student_answer.lower() or "queue is lifo" in student_answer.lower():
                missing_concepts.append("Correct mapping of LIFO/FIFO principles to Stack and Queue structures")
                explanation_parts.append("Awarded partial marks. The student swapped the ordering concepts (labeled stack as FIFO instead of LIFO).")
            else:
                explanation_parts.append("Great job defining stacks (LIFO) and queues (FIFO) along with appropriate real-world scenarios.")

        if "binary" in student_answer.lower() and "linear" in student_answer.lower():
            missing_concepts.append("Correct binary search algorithm implementation")
            explanation_parts.append("The implementation provided is for Linear Search (O(n)), not Binary Search (O(log n)). Deductions made for code correctness.")
        elif "binary" in student_answer.lower() and "O(log" in student_answer:
            explanation_parts.append("Binary search loop and logarithmic time complexity O(log n) were correctly implemented and explained.")

        if "bayes" in student_answer.lower():
            if "99%" in student_answer and not "9.0" in student_answer:
                missing_concepts.append("Calculation of actual posterior probability using base-rate prevalence")
                explanation_parts.append("Incorrect probability conclusion. The student assumed a 99% probability, ignoring the base prevalence rate of 0.1% for the disease.")
            elif "9.0" in student_answer or "0.09" in student_answer:
                explanation_parts.append("Perfect application of Bayes' Theorem. Correctly calculated the disease prevalence posterior probability (~9.02%).")

        # Compile general comments
        if not explanation_parts:
            if similarity > 0.8:
                explanation_parts.append("The student demonstrates a high level of subject matter mastery with precise keyword matches.")
            elif similarity > 0.5:
                explanation_parts.append("Adequate understanding shown. Missing some key elaboration or specific examples.")
            else:
                explanation_parts.append("The answer is too brief or off-topic, missing fundamental concepts.")

        # Aggregate missing concepts
        for kw in kw_match["missing_mandatory"]:
            missing_concepts.append(f"Inclusion of key term: '{kw}'")

        # Cap marks to max_marks
        if marks_awarded > max_marks:
            marks_awarded = max_marks

        return {
            "marks_awarded": float(marks_awarded),
            "explanation": " ".join(explanation_parts),
            "missing_concepts": missing_concepts,
            "missing_keywords": kw_match["missing_mandatory"] + kw_match["missing_optional"][:1],
            "confidence_score": round(0.85 + (similarity * 0.1), 2),
            "diagram_detected": has_diagram,
            "formula_detected": has_formula
        }
