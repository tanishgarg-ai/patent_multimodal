import os
import re
import logging
import requests
import fitz  # PyMuPDF
from bs4 import BeautifulSoup
from typing import Tuple

logger = logging.getLogger(__name__)

class PDFProcessor:
    def __init__(self, download_dir: str = "data/pdf_cache"):
        self.download_dir = download_dir
        os.makedirs(self.download_dir, exist_ok=True)

    def download_google_patent_pdf(self, patent_id: str) -> str:
        """Downloads the PDF for a given patent ID from Google Patents and returns the local file path."""
        # Clean the patent_id to remove hyphens or slashes if necessary
        clean_id = re.sub(r'[^a-zA-Z0-9]', '', patent_id)
        
        page_url = f"https://patents.google.com/patent/{clean_id}/en"
        logger.info(f"Fetching Google Patents page for {clean_id}: {page_url}")
        
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(page_url, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            pdf_link_tag = soup.find('a', {'itemprop': 'pdfLink'})
            if not pdf_link_tag or 'href' not in pdf_link_tag.attrs:
                # Fallback to storage URL if pdfLink not found
                logger.warning(f"Could not find pdfLink in HTML for {clean_id}, trying fallback URL pattern.")
                pdf_url = f"https://patentimages.storage.googleapis.com/{clean_id[:2]}/{clean_id[2:5]}/{clean_id[5:8]}/{clean_id}.pdf"
            else:
                pdf_url = pdf_link_tag['href']
                if not pdf_url.startswith('http'):
                    pdf_url = "https:" + pdf_url if pdf_url.startswith('//') else page_url + pdf_url
            
            logger.info(f"Downloading PDF from {pdf_url}")
            
            pdf_response = requests.get(pdf_url, headers=headers, stream=True)
            pdf_response.raise_for_status()
            
            local_path = os.path.join(self.download_dir, f"{clean_id}.pdf")
            with open(local_path, 'wb') as f:
                for chunk in pdf_response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.info(f"Successfully downloaded PDF to {local_path}")
            return local_path
            
        except Exception as e:
            logger.error(f"Failed to download PDF for {clean_id}: {e}")
            return ""

    def process_pdf(self, pdf_path: str) -> Tuple[str, str]:
        """Extracts text from PDF and attempts to separate Description and Claims."""
        if not pdf_path or not os.path.exists(pdf_path):
            return "", ""
            
        try:
            doc = fitz.open(pdf_path)
            full_text = ""
            for page in doc:
                full_text += page.get_text() + "\n"
                
            doc.close()
            
            # If PDF is just images, text will be very short
            if len(full_text.strip()) < 500:
                logger.warning(f"PDF text extraction yielded < 500 chars for {pdf_path}. It might be an image-only PDF.")
                return "", ""
                
            # Common headers for claims
            claims_start = -1
            description = full_text
            claims = ""
            
            claim_headers = [
                r"\nCLAIMS\n", r"\nWhat is claimed is[:]*", 
                r"\nWe claim:", r"\nI claim:", r"CLAIMS\s*\n"
            ]
            
            for header in claim_headers:
                match = re.search(header, full_text, re.IGNORECASE)
                if match:
                    claims_start = match.start()
                    break
                    
            if claims_start != -1:
                description = full_text[:claims_start].strip()
                claims = full_text[claims_start:].strip()
            else:
                logger.warning(f"Could not cleanly separate claims in {pdf_path}. Returning full text as description.")
                
            return description, claims
            
        except Exception as e:
            logger.error(f"Failed to extract text from {pdf_path}: {e}")
            return "", ""

    def extract_text_from_html(self, patent_id: str) -> Tuple[str, str]:
        """Extracts claims and description directly from Google Patents HTML for reliability."""
        clean_id = re.sub(r'[^a-zA-Z0-9]', '', patent_id)
        url = f"https://patents.google.com/patent/{clean_id}/en"
        
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            claims_tag = soup.find('section', itemprop='claims')
            claims_text = claims_tag.get_text(separator='\n').strip() if claims_tag else ""
            
            desc_tag = soup.find('section', itemprop='description')
            if not desc_tag:
                desc_tag = soup.find('div', class_='description')
                
            desc_text = desc_tag.get_text(separator='\n').strip() if desc_tag else ""
            
            logger.info(f"HTML Extraction for {clean_id}: Claims({len(claims_text)}), Desc({len(desc_text)})")
            return desc_text, claims_text
            
        except Exception as e:
            logger.error(f"Failed to extract HTML text for {clean_id}: {e}")
            return "", ""
