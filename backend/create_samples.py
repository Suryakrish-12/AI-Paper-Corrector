import os
import zipfile

def generate_samples():
    print("Generating sample test datasets...")
    target_dir = "../sample_papers"
    os.makedirs(target_dir, exist_ok=True)

    # Write mock PDF text markers (our mock OCR parser matches these filenames)
    samples = {
        os.path.join(target_dir, "question_paper_algorithms.pdf"): "%PDF-1.4 Mock Question Paper - CS-302 Algorithms",
        os.path.join(target_dir, "student_excellent_algorithms.pdf"): "%PDF-1.4 Mock Student Answer Script (Excellent Score) - CS-302",
        os.path.join(target_dir, "student_average_algorithms.pdf"): "%PDF-1.4 Mock Student Answer Script (Average Score) - CS-302"
    }

    for file_path, content in samples.items():
        with open(file_path, "w") as f:
            f.write(content)
        print(f"Created file: {file_path}")

    # Zip student sheets together to showcase bulk ZIP decompressed uploading
    zip_path = os.path.join(target_dir, "bulk_submissions.zip")
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        zipf.write(os.path.join(target_dir, "student_excellent_algorithms.pdf"), "student_excellent_algorithms.pdf")
        zipf.write(os.path.join(target_dir, "student_average_algorithms.pdf"), "student_average_algorithms.pdf")
    print(f"Created zipped archive bundle: {zip_path}")

if __name__ == "__main__":
    generate_samples()
