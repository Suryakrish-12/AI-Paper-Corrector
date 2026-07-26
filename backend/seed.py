from app.database import SessionLocal, Base, engine
from app.models import User, Institution, Department, Course, Subject, Student, Faculty, QuestionPaper, Question, AuditLog, AnswerScript, Evaluation
from app.auth import get_password_hash

def seed_database():
    print("Initializing Database Seeding...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    try:
        # Clear existing entries
        print("Clearing old data...")
        db.query(Student).delete()
        db.query(Faculty).delete()
        db.query(User).delete()
        db.query(Subject).delete()
        db.query(Course).delete()
        db.query(Department).delete()
        db.query(Institution).delete()
        db.commit()

        # 1. Create Institution
        inst = Institution(
            name="SmartEval University",
            code="SEU-01",
            address="Academic Block, Technology Campus"
        )
        db.add(inst)
        db.flush()
        print(f"Created Institution: {inst.name}")

        # 2. Create Departments
        dept = Department(
            name="Computer Science & Engineering",
            code="CSE",
            institution_id=inst.id
        )
        db.add(dept)
        db.flush()
        print(f"Created Department: {dept.name}")

        # 3. Create Course
        course = Course(
            name="Bachelor of Technology in CSE",
            code="BTECH-CSE",
            department_id=dept.id,
            semester=6
        )
        db.add(course)
        db.flush()
        print(f"Created Course: {course.name}")

        # 4. Create Subject
        sub = Subject(
            name="Design and Analysis of Algorithms",
            code="CS-302",
            course_id=course.id,
            credit=4
        )
        db.add(sub)
        db.flush()
        print(f"Created Subject: {sub.name}")

        # 5. Create users
        pw_hash = get_password_hash("password123")

        # Admin
        admin_user = User(
            email="admin@smarteval.ai",
            hashed_password=pw_hash,
            name="Dr. Rajesh Kumar",
            role="ADMIN",
            is_verified=True
        )
        db.add(admin_user)

        # Faculty
        fac_user = User(
            email="faculty@smarteval.ai",
            hashed_password=pw_hash,
            name="Prof. Amit Sharma",
            role="FACULTY",
            is_verified=True
        )
        db.add(fac_user)
        db.flush()

        faculty = Faculty(
            user_id=fac_user.id,
            department_id=dept.id,
            designation="Associate Professor"
        )
        db.add(faculty)
        db.flush()

        # 4b. Pre-seed Question Paper and Questions for CS-302
        qp = QuestionPaper(
            subject_id=sub.id,
            exam_name="Mid-Term Examination",
            academic_year="2025-2026",
            max_marks=40.0,
            passing_marks=16.0,
            status="COMPLETED",
            total_questions=4,
            created_by_faculty_id=faculty.id
        )
        db.add(qp)
        db.flush()
        print(f"Pre-seeded Question Paper: {qp.exam_name}")

        questions_list = [
            {
                "num": "1",
                "text": "Define Stack and Queue. Explain their differences and give real-world applications.",
                "max": 10.0,
                "keywords": ["LIFO", "FIFO", "plates", "ticket counter"],
                "mand": ["LIFO", "FIFO"],
                "ans": "A stack is a linear data structure that follows the LIFO (Last In First Out) principle. Elements are inserted (push) and removed (pop) from the same end, called the top. A queue is a linear data structure following FIFO (First In First Out)."
            },
            {
                "num": "2",
                "text": "What is the difference between TCP and UDP? Explain with neat diagrams.",
                "max": 10.0,
                "keywords": ["handshake", "connectionless", "reliable", "sliding window"],
                "mand": ["connection-oriented", "connectionless"],
                "ans": "TCP (Transmission Control Protocol) is connection-oriented, reliable, and guarantees in-order delivery using a three-way handshake (SYN, SYN-ACK, ACK). UDP (User Datagram Protocol) is connectionless, fast, and lightweight."
            },
            {
                "num": "3",
                "text": "Implement binary search algorithm in Python/C. Explain its time complexity.",
                "max": 10.0,
                "keywords": ["binary", "complexity", "O(log n)", "sorted"],
                "mand": ["sorted", "O(log n)"],
                "ans": "Binary search is an efficient search algorithm on sorted lists. It works by repeatedly dividing the search range in half. Time complexity is O(log n) because the search space is divided by 2 at each step."
            },
            {
                "num": "4",
                "text": "State Bayes' Theorem. Solve: In a test, a patient tests positive for a disease with 99% accuracy. If the disease prevalence is 0.1%, what is the actual probability they have the disease?",
                "max": 10.0,
                "keywords": ["Bayes", "prevalence", "9.02%", "posterior"],
                "mand": ["Bayes", "9.02"],
                "ans": "Bayes' Theorem states: P(A|B) = P(B|A) * P(A) / P(B). Applying Bayes' Formula results in a posterior probability of approximately 9.02%."
            }
        ]

        for q_data in questions_list:
            q = Question(
                question_paper_id=qp.id,
                question_number=q_data["num"],
                question_text=q_data["text"],
                max_marks=q_data["max"],
                keywords=q_data["keywords"],
                mandatory_keywords=q_data["mand"],
                model_answer=q_data["ans"]
            )
            db.add(q)
        print("Pre-seeded Exam Questions list.")

        # Student 1 (Excellent)
        std_user_1 = User(
            email="student1@smarteval.ai",
            hashed_password=pw_hash,
            name="Ananya Sharma",
            role="STUDENT",
            is_verified=True
        )
        db.add(std_user_1)
        db.flush()

        std_1 = Student(
            user_id=std_user_1.id,
            register_number="2026109312",
            department_id=dept.id,
            course_id=course.id,
            semester=6
        )
        db.add(std_1)
        db.flush()

        # Student 2 (Average)
        std_user_2 = User(
            email="student2@smarteval.ai",
            hashed_password=pw_hash,
            name="Rahul Verma",
            role="STUDENT",
            is_verified=True
        )
        db.add(std_user_2)
        db.flush()

        std_2 = Student(
            user_id=std_user_2.id,
            register_number="2026349129",
            department_id=dept.id,
            course_id=course.id,
            semester=6
        )
        db.add(std_2)
        db.flush()

        # 6. Seed AnswerScripts
        script_1 = AnswerScript(
            student_id=std_1.id,
            question_paper_id=qp.id,
            file_path="./uploads/student_excellent_algorithms.pdf",
            status="COMPLETED",
            is_handwritten=True,
            total_pages=2,
            file_type="PDF",
            evaluation_mode="STANDARD",
            overall_marks=34.5,
            overall_percentage=86.25,
            ocr_accuracy=98.5,
            ai_accuracy=96.0,
            confidence_score=0.95
        )
        db.add(script_1)

        script_2 = AnswerScript(
            student_id=std_2.id,
            question_paper_id=qp.id,
            file_path="./uploads/student_average_algorithms.pdf",
            status="COMPLETED",
            is_handwritten=True,
            total_pages=2,
            file_type="PDF",
            evaluation_mode="STANDARD",
            overall_marks=19.5,
            overall_percentage=48.75,
            ocr_accuracy=94.0,
            ai_accuracy=91.5,
            confidence_score=0.91
        )
        db.add(script_2)
        db.flush()

        # 7. Seed Evaluations (rubric feedback links)
        # Fetch seeded questions
        db_qs = db.query(Question).filter(Question.question_paper_id == qp.id).order_by(Question.question_number).all()

        # Script 1 (Excellent) Evaluations
        evals_1 = [
            Evaluation(
                answer_script_id=script_1.id,
                question_id=db_qs[0].id,
                student_answer_text="A stack is a linear data structure that follows the LIFO (Last In First Out) principle. Elements are inserted (push) and removed (pop) from the same end, called the top pointer. Real-world example: A stack of plates or backtracking in maze routing.",
                marks_awarded=9.0,
                explanation="The student correctly defined both Stack LIFO and Queue FIFO concepts and cited standard queue counters and plate stacks.",
                missing_concepts=[],
                missing_keywords=[],
                confidence_score=0.96,
                diagram_detected=True,
                formula_detected=False,
                status="APPROVED"
            ),
            Evaluation(
                answer_script_id=script_1.id,
                question_id=db_qs[1].id,
                student_answer_text="TCP (Transmission Control Protocol) is connection-oriented, reliable, and guarantees in-order delivery using a three-way handshake (SYN, SYN-ACK, ACK). It has flow control and error recovery. UDP (User Datagram Protocol) is connectionless, fast, and lightweight but does not guarantee packet delivery or order. TCP uses sliding window protocol; UDP just blasts packets.",
                marks_awarded=8.5,
                explanation="Properly distinguished TCP synchronization handshake sequences and UDP stream headers with neat summaries.",
                missing_concepts=[],
                missing_keywords=[],
                confidence_score=0.94,
                diagram_detected=True,
                formula_detected=False,
                status="APPROVED"
            ),
            Evaluation(
                answer_script_id=script_1.id,
                question_id=db_qs[2].id,
                student_answer_text="def binary_search(arr, target): low = 0; high = len(arr) - 1; while low <= high: mid = (low + high) // 2; if arr[mid] == target: return mid; elif arr[mid] < target: low = mid + 1; else: high = mid - 1; return -1. Time complexity: O(log n).",
                marks_awarded=9.0,
                explanation="Correct implementation of iterative binary search. Time complexity log n is correctly justified.",
                missing_concepts=[],
                missing_keywords=[],
                confidence_score=0.95,
                diagram_detected=False,
                formula_detected=True,
                status="APPROVED"
            ),
            Evaluation(
                answer_script_id=script_1.id,
                question_id=db_qs[3].id,
                student_answer_text="Bayes' Theorem states: P(A|B) = P(B|A) * P(A) / P(B). P(D|Pos) = (0.99 * 0.001) / [ (0.99 * 0.001) + (0.01 * 0.999) ] = 0.00099 / 0.01098 = 9.02% probability.",
                marks_awarded=9.0,
                explanation="Substituted sensitivity and joint prevalence parameters. Calculated final percentage correctly.",
                missing_concepts=[],
                missing_keywords=[],
                confidence_score=0.96,
                diagram_detected=False,
                formula_detected=True,
                status="APPROVED"
            )
        ]
        db.add_all(evals_1)

        # Script 2 (Average) Evaluations
        evals_2 = [
            Evaluation(
                answer_script_id=script_2.id,
                question_id=db_qs[0].id,
                student_answer_text="Stack is a list where you push elements at the top. Queue is where you enqueue elements at the rear and dequeue them at the front. Stack is FIFO (First In First Out) and Queue is LIFO (Last In First Out). No wait, Stack is LIFO (Last In First Out) and Queue is FIFO. Real-world example: Stack of plates, Queue at supermarket. Stack is used to store function parameters.",
                marks_awarded=6.0,
                explanation="Identified LIFO and FIFO correctly but lacks real-world applications in stack/queue differences.",
                missing_concepts=["Real-world use cases"],
                missing_keywords=["plates", "ticket counter"],
                confidence_score=0.88,
                diagram_detected=False,
                formula_detected=False,
                status="APPROVED"
            ),
            Evaluation(
                answer_script_id=script_2.id,
                question_id=db_qs[1].id,
                student_answer_text="TCP is connection oriented. UDP is connectionless. TCP guarantees packets are delivered, but UDP packages can be lost. TCP is slow because of handshake overhead. UDP is fast for games. TCP works on 3 way handshake. UDP has no handshake.",
                marks_awarded=6.5,
                explanation="Lacks reference to slide windows or detailed synchronization parameters.",
                missing_concepts=["Sliding window mechanism"],
                missing_keywords=["reliable", "sliding window"],
                confidence_score=0.89,
                diagram_detected=False,
                formula_detected=False,
                status="APPROVED"
            ),
            Evaluation(
                answer_script_id=script_2.id,
                question_id=db_qs[2].id,
                student_answer_text="def search(arr, x): for i in range(len(arr)): if arr[i] == x: return i; return -1. Complexity of this search code is O(n) because it checks everything in a loop. So this is linear search. But binary search is O(log n).",
                marks_awarded=3.5,
                explanation="Wrote a linear loop checking all items, which is O(n). This is incorrect for binary search rubric.",
                missing_concepts=["Binary search implementation", "Divide and conquer"],
                missing_keywords=["binary", "O(log n)"],
                confidence_score=0.85,
                diagram_detected=False,
                formula_detected=True,
                status="APPROVED"
            ),
            Evaluation(
                answer_script_id=script_2.id,
                question_id=db_qs[3].id,
                student_answer_text="Bayes theorem formula: P(A|B) = P(B|A)P(A)/P(B). The test accuracy is 99%. Since the patient tests positive and the test accuracy is 99%, the probability that they have the disease is 99% because the test is very accurate.",
                marks_awarded=3.5,
                explanation="Failed to combine joint probabilities. Assumed test accuracy is the final likelihood.",
                missing_concepts=["Prevalence weighting", "Posterior probability calculation"],
                missing_keywords=["prevalence", "9.02%"],
                confidence_score=0.87,
                diagram_detected=False,
                formula_detected=True,
                status="APPROVED"
            )
        ]
        db.add_all(evals_2)

        # 8. Seed Audit Logs
        logs = [
            AuditLog(user_id=admin_user.id, action="SYSTEM_INIT", details="Database seeded and initialized.", ip_address="127.0.0.1"),
            AuditLog(user_id=faculty.user_id, action="RUBRIC_CREATED", details="Registered exam rubric for CS-302.", ip_address="127.0.0.1"),
            AuditLog(user_id=faculty.user_id, action="EVALUATION_COMPLETED", details="Evaluated script for Ananya Sharma (Score: 34.5).", ip_address="127.0.0.1"),
            AuditLog(user_id=faculty.user_id, action="EVALUATION_COMPLETED", details="Evaluated script for Rahul Verma (Score: 19.5).", ip_address="127.0.0.1")
        ]
        db.add_all(logs)

        db.commit()
        print("Database Seed Completed Successfully!")

    except Exception as e:
        db.rollback()
        print(f"Error during seeding: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
