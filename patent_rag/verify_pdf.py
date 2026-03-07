import os
import sys
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from patent_rag.pdf_utils import PDFProcessor

def test_pdf_processing():
    processor = PDFProcessor(download_dir="data/pdf_cache")
    
    test_id = "US10345672" # LiDAR patent
    print(f"Testing PDF download for {test_id}...")
    
    local_path = processor.download_google_patent_pdf(test_id)
    print(f"Downloaded to: {local_path}")
    
    if local_path and os.path.exists(local_path):
        print(f"File exists. Size: {os.path.getsize(local_path)} bytes")
        
        description, claims = processor.process_pdf(local_path)
        if not claims or len(description) < 500:
            print("PDF extraction failed to separate claims, trying HTML...")
            description, claims = processor.extract_text_from_html(test_id)
            
        print(f"Extracted description length: {len(description)}")
        print(f"Extracted claims length: {len(claims)}")
        
        if claims:
            print("\nSnippet of claims:")
            print(claims[:200] + "...")
        else:
            print("\nClaims section empty!")
    else:
        print("Download failed or file not found.")

if __name__ == "__main__":
    test_pdf_processing()
