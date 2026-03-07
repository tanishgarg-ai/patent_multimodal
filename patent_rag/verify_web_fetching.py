import os
import sys
import logging
from dotenv import load_dotenv

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_ingestion import WebDataFetcher

logging.basicConfig(level=logging.INFO)

def test_fetcher():
    load_dotenv()
    fetcher = WebDataFetcher(api_key=os.getenv("SEMANTIC_SCHOLAR_API_KEY"))
    
    query = "LiDAR based navigation for drones"
    
    print(f"\n--- Testing fetch_papers for: {query} ---")
    papers = fetcher.fetch_papers(query, limit=2)
    for p in papers:
        print(f"ID: {p['paper_id']} | Title: {p['title']}")
        
    print(f"\n--- Testing fetch_patents for: {query} ---")
    patents = fetcher.fetch_patents(query, limit=2)
    for p in patents:
        print(f"ID: {p['patent_id']} | Title: {p['title']}")

if __name__ == "__main__":
    test_fetcher()
