import os
import json
import logging
import requests
import time
from typing import List, Dict, Any, Optional
from semanticscholar import SemanticScholar
try:
    from google.cloud import bigquery
except ImportError:
    bigquery = None

logger = logging.getLogger(__name__)

class WebDataFetcher:
    """Fetcher for real-time patent and academic paper data from the web."""
    
    def __init__(self, semantic_scholar_api_key: Optional[str] = None, uspto_api_key: Optional[str] = None, google_project_id: Optional[str] = None):
        self.sch = SemanticScholar(api_key=semantic_scholar_api_key)
        self.uspto_api_url = "https://api.uspto.gov/api/v1/patent/applications/search"
        self.uspto_api_key = uspto_api_key
        self.google_project_id = google_project_id
        if bigquery and google_project_id and google_project_id != "your_google_cloud_project_id_here":
            try:
                self.bq_client = bigquery.Client(project=google_project_id)
                logger.info(f"Initialized BigQuery client for project: {google_project_id}")
            except Exception as e:
                logger.warning(f"Failed to initialize BigQuery client: {e}. Ensure you run 'gcloud auth application-default login'")
                self.bq_client = None
        else:
            if not google_project_id or google_project_id == "your_google_cloud_project_id_here":
                logger.warning("Google Cloud Project ID not configured. BigQuery retrieval disabled.")
            self.bq_client = None

    def fetch_papers(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Fetch academic papers from Semantic Scholar with simple retry for rate limits."""
        logger.info(f"Fetching papers from Semantic Scholar for query: {query}")
        max_retries = 3
        retry_delay = 2
        for attempt in range(max_retries):
            try:
                results = self.sch.search_paper(query, limit=limit)
                papers = []
                for item in results[:limit]:
                    papers.append({
                        "doc_type": "paper",
                        "paper_id": item.paperId,
                        "title": item.title,
                        "abstract": item.abstract if item.abstract else "No abstract available.",
                        "authors": [author.name for author in item.authors] if item.authors else [],
                        "year": item.year if item.year else 0,
                        "url": item.url,
                        "image_paths": []
                    })
                return papers
            except Exception as e:
                if "429" in str(e) and attempt < max_retries - 1:
                    logger.warning(f"Rate limited by Semantic Scholar. Retrying in {retry_delay}s... (Attempt {attempt + 1}/{max_retries})")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    logger.error(f"Error fetching papers from Semantic Scholar: {e}")
                    return []
        return []

    def fetch_patents(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Fetch patents from Google Patents (BigQuery) or fallback to USPTO."""
        if self.bq_client:
            return self._fetch_patents_google(query, limit)
        else:
            return self._fetch_patents_uspto(query, limit)

    def _fetch_patents_google(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Fetch patents from Google Patents Public Dataset using BigQuery."""
        logger.info(f"Fetching patents from Google Patents (BigQuery) for query: {query}")
        try:
            # Prepare independent keywords for broader matching
            import re
            # Split by non-alphanumeric characters to handle hyphens etc.
            keywords = [kw.lower() for kw in re.split(r'[^a-zA-Z0-9]', query) if len(kw) > 3]
            
            if not keywords:
                keywords = [query.lower()]
            
            logger.info(f"Using keywords for BigQuery: {keywords}")
                
            title_conditions = " AND ".join([f"LOWER(t.text) LIKE '%{kw}%'" for kw in keywords])
            abstract_conditions = " AND ".join([f"LOWER(a.text) LIKE '%{kw}%'" for kw in keywords])

            # Prepare safe query
            sql = f"""
            SELECT publication_number, 
                   (SELECT text FROM UNNEST(title_localized) WHERE language = 'en' LIMIT 1) as title,
                   (SELECT text FROM UNNEST(abstract_localized) WHERE language = 'en' LIMIT 1) as abstract,
                   publication_date,
                   country_code
            FROM `patents-public-data.patents.publications`
            WHERE (EXISTS (SELECT 1 FROM UNNEST(title_localized) t WHERE t.language = 'en' AND {title_conditions}))
               OR (EXISTS (SELECT 1 FROM UNNEST(abstract_localized) a WHERE a.language = 'en' AND {abstract_conditions}))
            LIMIT {limit}
            """
            
            logger.debug(f"Executing BigQuery SQL: {sql}")
            query_job = self.bq_client.query(sql)
            results = query_job.result()
            
            patents = []
            for row in results:
                pub_num = row.publication_number
                pdf_url = f"https://patents.google.com/patent/{pub_num}/en"
                
                patents.append({
                    "doc_type": "patent",
                    "patent_id": pub_num,
                    "title": row.title or "No title available.",
                    "abstract": row.abstract or "No abstract available.",
                    "claims": "", 
                    "description": row.abstract or "", 
                    "publication_date": str(row.publication_date),
                    "classification": row.country_code,
                    "pdf_url": pdf_url, 
                    "image_paths": []
                })
            
            logger.info(f"Google BigQuery returned {len(patents)} patents.")
            return patents
        except Exception as e:
            logger.error(f"Error fetching patents from Google BigQuery: {e}")
            # Fallback to USPTO if BigQuery fails
            return self._fetch_patents_uspto(query, limit)

    def _fetch_patents_uspto(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Existing USPTO fetch logic as a secondary source or fallback."""
        logger.info(f"Fetching patents from USPTO for query: {query}")
        try:
            headers = {"X-Api-Key": self.uspto_api_key} if self.uspto_api_key else {}
            params = {
                "q": f"applicationMetaData.inventionTitle:{query} OR applicationMetaData.abstractText:{query}",
                "limit": limit
            }
            response = requests.get(self.uspto_api_url, params=params, headers=headers)
            if response.status_code == 401:
                logger.error("USPTO API Error: Unauthorized.")
                return []
            response.raise_for_status()
            data = response.json()
            patents = []
            results = data.get("results", [])
            for item in results:
                meta = item.get("applicationMetaData", {})
                patents.append({
                    "doc_type": "patent",
                    "patent_id": meta.get("applicationNumberText") or meta.get("patentNumber"),
                    "title": meta.get("inventionTitle"),
                    "abstract": meta.get("abstractText") or "No abstract available.",
                    "claims": "", 
                    "description": meta.get("abstractText") or "", 
                    "publication_date": meta.get("filingDate"),
                    "classification": meta.get("applicationType", "Unknown"),
                    "image_paths": []
                })
            return patents
        except Exception as e:
            logger.error(f"Error fetching patents from USPTO: {e}")
            return []

class PatentCorpusLoader:
    """Loader for patent datasets (e.g., USPTO, Google Patents)"""
    
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        
    def load_sample_patents(self) -> List[Dict[str, Any]]:
        """Mock loader that returns a list of sample patent dictionaries."""
        logger.info("Loading sample patents...")
        return [
            {
                "doc_type": "patent",
                "patent_id": "US10345672",
                "title": "LiDAR based navigation system for autonomous drones",
                "abstract": "A system and method for navigating an autonomous drone using a LiDAR sensor and a machine learning algorithm for real-time obstacle avoidance.",
                "claims": "1. A system comprising: a LiDAR sensor configured to capture 3D point cloud data; a processor; and a navigation algorithm executing on the processor to perform obstacle avoidance.",
                "description": "Detailed description of the LiDAR drone navigation system. It uses point clouds to map the environment and deep learning to avoid obstacles.",
                "publication_date": "2019-07-09",
                "classification": "G05D1/02",
                "image_paths": [] # Optional Multimodal
            },
            {
                "doc_type": "patent",
                "patent_id": "US2020111222",
                "title": "Method for avoiding objects using ultrasonic sensors",
                "abstract": "A method for navigating robots using ultrasonic sensors rather than optical means.",
                "claims": "1. A robot navigation method comprising: emitting ultrasonic pulses; receiving echoes; and determining a collision free path.",
                "description": "Uses sound waves to determine distances to obstacles and plan paths around them.",
                "publication_date": "2020-05-15",
                "classification": "G05D1/02",
                "image_paths": []
            }
        ]
        
    def load_from_directory(self) -> List[Dict[str, Any]]:
        """Load from JSON files in the data directory."""
        if not os.path.exists(self.data_dir):
            return self.load_sample_patents()
            
        patents = []
        for filename in os.listdir(self.data_dir):
            if filename.endswith(".json"):
                filepath = os.path.join(self.data_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if data.get("doc_type") == "patent":
                            patents.append(data)
                except Exception as e:
                    logger.error(f"Error loading {filepath}: {e}")
        return patents if patents else self.load_sample_patents()


class AcademicPaperLoader:
    """Loader for academic papers (e.g., Semantic Scholar)"""
    
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        
    def load_sample_papers(self) -> List[Dict[str, Any]]:
        logger.info("Loading sample academic papers...")
        return [
            {
                "doc_type": "paper",
                "paper_id": "IEEE2019-DL",
                "title": "Deep Learning for Obstacle Avoidance in UAVs",
                "abstract": "This paper presents a novel deep learning architecture for Unmanned Aerial Vehicles (UAVs) to avoid obstacles in real-time. Experimental results using LiDAR data demonstrate high reliability.",
                "authors": ["John Doe", "Jane Smith"],
                "year": 2019,
                "image_paths": []
            }
        ]
        
    def load_from_directory(self) -> List[Dict[str, Any]]:
        """Load from JSON files in the data directory."""
        if not os.path.exists(self.data_dir):
            return self.load_sample_papers()
            
        papers = []
        for filename in os.listdir(self.data_dir):
            if filename.endswith(".json"):
                filepath = os.path.join(self.data_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if data.get("doc_type") == "paper":
                            papers.append(data)
                except Exception as e:
                    logger.error(f"Error loading {filepath}: {e}")
        return papers if papers else self.load_sample_papers()


class DataIngestionPipeline:
    def __init__(self, data_dir: str = "data", semantic_scholar_api_key: Optional[str] = None, uspto_api_key: Optional[str] = None, google_project_id: Optional[str] = None):
        self.data_dir = data_dir
        self.patent_loader = PatentCorpusLoader(data_dir)
        self.paper_loader = AcademicPaperLoader(data_dir)
        self.web_fetcher = WebDataFetcher(
            semantic_scholar_api_key=semantic_scholar_api_key, 
            uspto_api_key=uspto_api_key,
            google_project_id=google_project_id
        )
        
    def ingest_all(self) -> List[Dict[str, Any]]:
        """Ingest both patents and academic papers from local directory."""
        documents = []
        documents.extend(self.patent_loader.load_from_directory())
        documents.extend(self.paper_loader.load_from_directory())
        logger.info(f"Ingested {len(documents)} documents total from local.")
        return documents

    def ingest_from_web(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Ingest both patents and academic papers from web APIs."""
        documents = []
        documents.extend(self.web_fetcher.fetch_patents(query, limit=limit))
        documents.extend(self.web_fetcher.fetch_papers(query, limit=limit))
        logger.info(f"Ingested {len(documents)} documents total from web.")
        return documents

