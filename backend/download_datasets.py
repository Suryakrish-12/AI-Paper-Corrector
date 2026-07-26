import os
import urllib.request
import zipfile

def download_images():
    target_dir = "../sample_papers"
    os.makedirs(target_dir, exist_ok=True)
    
    # Raw public domain sample image hosted on GitHub for OCR API testing
    urls = {
        "https://raw.githubusercontent.com/aimlapi/api-docs/main/reference-files/handwriting.jpg": "handwriting_sample.jpg"
    }
    
    print("Downloading sample handwriting image datasets from GitHub...")
    for url, filename in urls.items():
        dest = os.path.join(target_dir, filename)
        try:
            print(f"Retrieving: {url}")
            
            # Setup a browser Request header to bypass scrapers blocking
            req = urllib.request.Request(
                url, 
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
            )
            
            with urllib.request.urlopen(req) as response, open(dest, 'wb') as out_file:
                out_file.write(response.read())
            print(f"Successfully saved to: {dest}")
        except Exception as e:
            print(f"Error downloading {filename}: {e}")
            
    # Package into a submissions zip to verify ZIP script uploads
    zip_path = os.path.join(target_dir, "image_submissions.zip")
    try:
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for filename in urls.values():
                file_p = os.path.join(target_dir, filename)
                if os.path.exists(file_p):
                    zipf.write(file_p, filename)
        print(f"Created zipped image collection: {zip_path}")
    except Exception as e:
        print(f"Failed to create ZIP package: {e}")

if __name__ == "__main__":
    download_images()
