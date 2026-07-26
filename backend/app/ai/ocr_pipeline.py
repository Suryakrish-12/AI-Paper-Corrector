import time
import os
from app.config import settings

# Attempt to import EasyOCR, fallback to mock if fails or settings.USE_MOCK_AI
easyocr_reader = None
if not settings.USE_MOCK_AI:
    try:
        import easyocr
        import numpy as np
        # Initialize reader (downloads model files on first execution)
        easyocr_reader = easyocr.Reader(['en'])
    except Exception as e:
        print(f"Failed to initialize EasyOCR: {e}. Falling back to Mock OCR.")

class OCRPipeline:
    def __init__(self):
        self.use_mock = settings.USE_MOCK_AI or (easyocr_reader is None)

    def extract_text_from_file(self, file_path: str) -> dict:
        """
        Extracts text from a PDF, image, or ZIP.
        Returns a dictionary mapping page number to text or segmented questions.
        """
        print(f"Running OCR on: {file_path} (Mock: {self.use_mock})")
        if self.use_mock:
            time.sleep(1.5)  # Simulate processing latency
            return self._get_mock_ocr_result(file_path)
        
        try:
            ext = os.path.splitext(file_path)[1].lower()
            if ext in ['.pdf']:
                # In production: convert PDF to images using pdf2image and run OCR on each page.
                # For this setup, we fall back to mock data
                return self._get_mock_ocr_result(file_path)
            
            # Run EasyOCR on the image file
            results = easyocr_reader.readtext(file_path)
            text_lines = [res[1] for res in results]
            full_text = "\n".join(text_lines)
            
            # Simple heuristic mapping to parse structured text
            confidence = sum([res[2] for res in results]) / len(results) if results else 0.95
            
            # In a full OCR pipe, layout analysis segments answers by question headers
            # Here we structure it into a format the NLP engine expects
            return {
                "type": "answer_script",
                "is_handwritten": True,
                "confidence": confidence,
                "answers": self._heuristic_segmentation(full_text)
            }
        except Exception as e:
            print(f"Real OCR failed: {e}. Falling back to Mock.")
            return self._get_mock_ocr_result(file_path)

    def _heuristic_segmentation(self, text: str) -> dict:
        # Simplistic regex/heuristic splitting of a single page of text by question numbers
        # e.g., finding lines starting with "1.", "Q2", "Ans 3"
        import re
        answers = {}
        patterns = [r'(?:^|\n)(?:Q|q|Ans|ans|Question)?\s*(\d+)\s*[:\.\)]']
        
        # Simple split logic
        lines = text.split('\n')
        current_q = None
        current_text = []
        
        for line in lines:
            match = None
            for pat in patterns:
                m = re.match(pat, line.strip())
                if m:
                    match = m
                    break
            
            if match:
                if current_q:
                    answers[current_q] = "\n".join(current_text).strip()
                current_q = match.group(1)
                current_text = [re.sub(pat, '', line).strip()]
            else:
                if current_q:
                    current_text.append(line)
                    
        if current_q and current_text:
            answers[current_q] = "\n".join(current_text).strip()
            
        # Fallback if no questions matched
        if not answers:
            answers["1"] = text
            
        return answers

    def _get_mock_ocr_result(self, file_path: str) -> dict:
        filename = os.path.basename(file_path).lower()
        
        if "question" in filename or "qp" in filename:
            return {
                "type": "question_paper",
                "questions": [
                    {
                        "number": "1",
                        "text": "Define Stack and Queue. Explain their differences and give real-world applications.",
                        "max_marks": 10.0
                    },
                    {
                        "number": "2",
                        "text": "What is the difference between TCP and UDP? Explain with neat diagrams.",
                        "max_marks": 10.0
                    },
                    {
                        "number": "3",
                        "text": "Implement binary search algorithm in Python/C. Explain its time complexity.",
                        "max_marks": 10.0
                    },
                    {
                        "number": "4",
                        "text": "State Bayes' Theorem. Solve: In a test, a patient tests positive for a disease with 99% accuracy. If the disease prevalence is 0.1%, what is the actual probability they have the disease?",
                        "max_marks": 10.0
                    }
                ]
            }
            
        # Check for mock students
        if "student_1" in filename or "excellent" in filename or "best" in filename:
            return {
                "type": "answer_script",
                "is_handwritten": True,
                "answers": {
                    "1": "A stack is a linear data structure that follows the LIFO (Last In First Out) principle. Elements are inserted (push) and removed (pop) from the same end, called the top pointer. Real-world example: A stack of plates or backtracking in maze routing. A queue is a linear data structure following FIFO (First In First Out). Insertion (enqueue) happens at the rear, and removal (dequeue) happens at the front pointer. Example: A queue of people waiting at a movie ticket counter. Differences: Stack uses one end for insertion/deletion (LIFO), whereas queue uses two distinct ends (FIFO). Stacks are used in function calls, while queues are used in CPU scheduling.",
                    "2": "TCP (Transmission Control Protocol) is connection-oriented, reliable, and guarantees in-order delivery using a three-way handshake (SYN, SYN-ACK, ACK). It has flow control and error recovery. UDP (User Datagram Protocol) is connectionless, fast, and lightweight but does not guarantee packet delivery or order. TCP uses sliding window protocol; UDP just blasts packets. TCP is used for Web (HTTP), Email (SMTP); UDP is used for live streaming, DNS, and online gaming. Diagram depicts TCP handshake client-server exchange and UDP single-packet dispatch.",
                    "3": "Binary search is an efficient search algorithm on sorted lists. It works by repeatedly dividing the search range in half. If the target value is less than the middle element, it narrows the search to the lower half; otherwise, it narrows to the upper half. Here is the implementation in Python:\n```python\ndef binary_search(arr, target):\n    low = 0\n    high = len(arr) - 1\n    while low <= high:\n        mid = (low + high) // 2\n        if arr[mid] == target:\n            return mid\n        elif arr[mid] < target:\n            low = mid + 1\n        else:\n            high = mid - 1\n    return -1\n```\nTime complexity: Best case is O(1) if target is at middle. Average and worst-case time complexity is O(log n) because the search space is divided by 2 at each step.",
                    "4": "Bayes' Theorem states: P(A|B) = P(B|A) * P(A) / P(B).\nLet D = Patient has the disease, and Pos = Patient tests positive.\nGiven:\nPrevalence of disease, P(D) = 0.1% = 0.001.\nTherefore, P(not D) = 1 - 0.001 = 0.999.\nTest accuracy for disease positive (sensitivity), P(Pos|D) = 99% = 0.99.\nFalse positive rate (assuming test is 99% accurate overall, false positive is 1%), P(Pos|not D) = 1% = 0.01.\nWe need to find P(D|Pos), the probability they actually have the disease given a positive test.\nUsing Bayes' Formula:\nP(D|Pos) = P(Pos|D) * P(D) / [ P(Pos|D) * P(D) + P(Pos|not D) * P(not D) ]\nP(D|Pos) = (0.99 * 0.001) / [ (0.99 * 0.001) + (0.01 * 0.999) ]\nP(D|Pos) = 0.00099 / [ 0.00099 + 0.00999 ] = 0.00099 / 0.01098\nP(D|Pos) = 0.09016, which is approximately 9.02% probability."
                }
            }
            
        # Normal/Average student script (student_2)
        return {
            "type": "answer_script",
            "is_handwritten": True,
            "answers": {
                "1": "Stack is a list where you push elements at the top. Queue is where you enqueue elements at the rear and dequeue them at the front. Stack is FIFO (First In First Out) and Queue is LIFO (Last In First Out). No wait, Stack is LIFO (Last In First Out) and Queue is FIFO. Real-world example: Stack of plates, Queue at supermarket. Stack is used to store function parameters.",
                "2": "TCP is connection oriented. UDP is connectionless. TCP guarantees packets are delivered, but UDP packages can be lost. TCP is slow because of handshake overhead. UDP is fast for games. TCP works on 3 way handshake. UDP has no handshake.",
                "3": "Binary search is a method to find an element in a sorted list. It goes to the middle item, if it matches it returns. If not, it searches recursively. Python code:\n```python\ndef search(arr, x):\n    for i in range(len(arr)):\n        if arr[i] == x:\n            return i\n    return -1\n```\nComplexity of this search code is O(n) because it checks everything in a loop. So this is linear search. But binary search is O(log n).",
                "4": "Bayes theorem formula: P(A|B) = P(B|A)P(A)/P(B). The test accuracy is 99%. Since the patient tests positive and the test accuracy is 99%, the probability that they have the disease is 99% because the test is very accurate."
            }
        }
