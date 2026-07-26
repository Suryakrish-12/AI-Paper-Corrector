from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
import zipfile

def create_pdf(filepath, header_title, content_blocks):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    c = canvas.Canvas(filepath, pagesize=letter)
    width, height = letter
    
    # Draw premium header band
    c.setFillColorRGB(0.08, 0.09, 0.15)
    c.rect(0, height - 70, width, 70, fill=True, stroke=False)
    
    c.setFillColorRGB(1.0, 1.0, 1.0)
    c.setFont("Helvetica-Bold", 15)
    c.drawString(40, height - 40, header_title)
    
    y = height - 100
    for block in content_blocks:
        if y < 80:
            c.showPage()
            y = height - 70
            
        c.setFillColorRGB(0.1, 0.1, 0.1)
        if block.get("type") == "heading":
            c.setFont("Helvetica-Bold", 12)
            c.drawString(40, y, block["text"])
            y -= 22
        elif block.get("type") == "subheading":
            c.setFont("Helvetica-Bold", 10)
            c.drawString(50, y, block["text"])
            y -= 18
        elif block.get("type") == "paragraph":
            c.setFont("Helvetica", 9)
            text = block["text"]
            # Simple text wrap logic
            words = text.split()
            line = []
            for word in words:
                line.append(word)
                if len(" ".join(line)) > 85:
                    c.drawString(55, y, " ".join(line[:-1]))
                    y -= 14
                    line = [word]
                    if y < 80:
                        c.showPage()
                        y = height - 70
                        c.setFont("Helvetica", 9)
            if line:
                c.drawString(55, y, " ".join(line))
                y -= 16
            y -= 2
            
    c.save()
    print(f"Generated PDF: {filepath}")

def main():
    target_dir = "../sample_papers"
    os.makedirs(target_dir, exist_ok=True)

    # 1. Generate Question Paper PDF
    qp_content = [
        {"type": "heading", "text": "SmartEval University - Mid-Term Examination"},
        {"type": "subheading", "text": "Subject: Design & Analysis of Algorithms (CS-302)"},
        {"type": "subheading", "text": "Max Marks: 40.0 | Time Allowed: 2 Hours"},
        {"type": "paragraph", "text": "Instructions: Answer all descriptive questions in detail. Scanned papers should clearly print register numbers at the header."},
        {"type": "heading", "text": "Q1. Define Stack and Queue. Explain their differences and give real-world applications. [10 Marks]"},
        {"type": "heading", "text": "Q2. What is the difference between TCP and UDP? Explain with neat diagrams. [10 Marks]"},
        {"type": "heading", "text": "Q3. Implement binary search algorithm in Python/C. Explain its time complexity. [10 Marks]"},
        {"type": "heading", "text": "Q4. State Bayes' Theorem. Solve: In a test, a patient tests positive for a disease with 99% accuracy. If the disease prevalence is 0.1%, what is the actual probability they have the disease? [10 Marks]"}
    ]
    create_pdf(
        os.path.join(target_dir, "question_paper_algorithms.pdf"),
        "EXAM QUESTION SCHEME - CS-302",
        qp_content
    )

    # 2. Generate Student 1 (Excellent) Answer Script PDF
    s1_content = [
        {"type": "heading", "text": "ANSWER BOOKLET - DESCRIPTIVE GRADING"},
        {"type": "subheading", "text": "Register Number: 2026109312"},
        {"type": "subheading", "text": "Student Name: Ananya Sharma"},
        {"type": "heading", "text": "Answer 1:"},
        {"type": "paragraph", "text": "A stack is a linear data structure that follows the LIFO (Last In First Out) principle. Elements are inserted (push) and removed (pop) from the same end, called the top pointer. Real-world example: A stack of plates or backtracking in maze routing."},
        {"type": "paragraph", "text": "A queue is a linear data structure following FIFO (First In First Out). Insertion (enqueue) happens at the rear, and removal (dequeue) happens at the front pointer. Example: A queue of people waiting at a movie ticket counter."},
        {"type": "paragraph", "text": "Differences: Stack uses one end for insertion/deletion (LIFO), whereas queue uses two distinct ends (FIFO). Stacks are used in function calls, while queues are used in CPU scheduling."},
        {"type": "heading", "text": "Answer 2:"},
        {"type": "paragraph", "text": "TCP (Transmission Control Protocol) is connection-oriented, reliable, and guarantees in-order delivery using a three-way handshake (SYN, SYN-ACK, ACK). It has flow control and error recovery. UDP (User Datagram Protocol) is connectionless, fast, and lightweight but does not guarantee packet delivery or order. TCP uses sliding window protocol; UDP just blasts packets."},
        {"type": "paragraph", "text": "TCP is used for Web (HTTP), Email (SMTP); UDP is used for live streaming, DNS, and online gaming. Diagram depicts TCP handshake client-server exchange and UDP single-packet dispatch."},
        {"type": "heading", "text": "Answer 3:"},
        {"type": "paragraph", "text": "Binary search is an efficient search algorithm on sorted lists. It works by repeatedly dividing the search range in half. If the target value is less than the middle element, it narrows the search to the lower half; otherwise, it narrows to the upper half. Here is the implementation in Python:"},
        {"type": "paragraph", "text": "def binary_search(arr, target):"},
        {"type": "paragraph", "text": "    low = 0"},
        {"type": "paragraph", "text": "    high = len(arr) - 1"},
        {"type": "paragraph", "text": "    while low <= high:"},
        {"type": "paragraph", "text": "        mid = (low + high) // 2"},
        {"type": "paragraph", "text": "        if arr[mid] == target: return mid"},
        {"type": "paragraph", "text": "        elif arr[mid] < target: low = mid + 1"},
        {"type": "paragraph", "text": "        else: high = mid - 1"},
        {"type": "paragraph", "text": "    return -1"},
        {"type": "paragraph", "text": "Time complexity: Best case is O(1) if target is at middle. Average and worst-case time complexity is O(log n) because the search space is divided by 2 at each step."},
        {"type": "heading", "text": "Answer 4:"},
        {"type": "paragraph", "text": "Bayes' Theorem states: P(A|B) = P(B|A) * P(A) / P(B). Let D = Patient has the disease, and Pos = Patient tests positive."},
        {"type": "paragraph", "text": "Given: Prevalence of disease, P(D) = 0.1% = 0.001. Therefore, P(not D) = 1 - 0.001 = 0.999. Test accuracy for disease positive (sensitivity), P(Pos|D) = 99% = 0.99. False positive rate (assuming test is 99% accurate overall, false positive is 1%), P(Pos|not D) = 1% = 0.01. We need to find P(D|Pos)."},
        {"type": "paragraph", "text": "Using Bayes' Formula: P(D|Pos) = P(Pos|D) * P(D) / [ P(Pos|D) * P(D) + P(Pos|not D) * P(not D) ] = (0.99 * 0.001) / [ (0.99 * 0.001) + (0.01 * 0.999) ] = 0.00099 / [ 0.00099 + 0.00999 ] = 0.00099 / 0.01098 = 0.09016, which is approximately 9.02% probability."}
    ]
    create_pdf(
        os.path.join(target_dir, "student_excellent_algorithms.pdf"),
        "STUDENT RESPONSE SHEET - ANANYA SHARMA",
        s1_content
    )

    # 3. Generate Student 2 (Average) Answer Script PDF
    s2_content = [
        {"type": "heading", "text": "ANSWER BOOKLET - DESCRIPTIVE GRADING"},
        {"type": "subheading", "text": "Register Number: 2026349129"},
        {"type": "subheading", "text": "Student Name: Rahul Verma"},
        {"type": "heading", "text": "Answer 1:"},
        {"type": "paragraph", "text": "Stack is a list where you push elements at the top. Queue is where you enqueue elements at the rear and dequeue them at the front. Stack is FIFO (First In First Out) and Queue is LIFO (Last In First Out). No wait, Stack is LIFO (Last In First Out) and Queue is FIFO. Real-world example: Stack of plates, Queue at supermarket. Stack is used to store function parameters."},
        {"type": "heading", "text": "Answer 2:"},
        {"type": "paragraph", "text": "TCP is connection oriented. UDP is connectionless. TCP guarantees packets are delivered, but UDP packages can be lost. TCP is slow because of handshake overhead. UDP is fast for games. TCP works on 3 way handshake. UDP has no handshake."},
        {"type": "heading", "text": "Answer 3:"},
        {"type": "paragraph", "text": "Binary search is a method to find an element in a sorted list. It goes to the middle item, if it matches it returns. If not, it searches recursively. Python code:"},
        {"type": "paragraph", "text": "def search(arr, x):"},
        {"type": "paragraph", "text": "    for i in range(len(arr)):"},
        {"type": "paragraph", "text": "        if arr[i] == x: return i"},
        {"type": "paragraph", "text": "    return -1"},
        {"type": "paragraph", "text": "Complexity of this search code is O(n) because it checks everything in a loop. So this is linear search. But binary search is O(log n)."},
        {"type": "heading", "text": "Answer 4:"},
        {"type": "paragraph", "text": "Bayes theorem formula: P(A|B) = P(B|A)P(A)/P(B). The test accuracy is 99%. Since the patient tests positive and the test accuracy is 99%, the probability that they have the disease is 99% because the test is very accurate."}
    ]
    create_pdf(
        os.path.join(target_dir, "student_average_algorithms.pdf"),
        "STUDENT RESPONSE SHEET - RAHUL VERMA",
        s2_content
    )

    # 4. Re-create ZIP submissions package
    zip_path = os.path.join(target_dir, "bulk_submissions.zip")
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        zipf.write(os.path.join(target_dir, "student_excellent_algorithms.pdf"), "student_excellent_algorithms.pdf")
        zipf.write(os.path.join(target_dir, "student_average_algorithms.pdf"), "student_average_algorithms.pdf")
    print(f"Re-created bulk submissions archive package: {zip_path}")

if __name__ == "__main__":
    main()
