import os
import json
import logging
import requests
import time
from typing import List, Dict, Any, Optional
from semanticscholar import SemanticScholar
from pdf_utils import PDFProcessor

try:
    from google.cloud import bigquery
except ImportError:
    bigquery = None

logger = logging.getLogger(__name__)


class WebDataFetcher:
    """Fetcher for real-time patent and academic paper data from the web."""

    def __init__(self, semantic_scholar_api_key: Optional[str] = None, google_project_id: Optional[str] = None):
        self.sch = SemanticScholar(api_key=semantic_scholar_api_key)
        self.google_project_id = google_project_id

        # We keep PDFProcessor initialized in case you want to use it elsewhere,
        # but it is no longer used for the main BigQuery fetching.
        self.pdf_processor = PDFProcessor()

        if bigquery and google_project_id and google_project_id != "your_google_cloud_project_id_here":
            try:
                self.bq_client = bigquery.Client(project=google_project_id)
                logger.info(f"Initialized BigQuery client for project: {google_project_id}")
            except Exception as e:
                logger.warning(
                    f"Failed to initialize BigQuery client: {e}. Ensure you run 'gcloud auth application-default login'")
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
                    logger.warning(
                        f"Rate limited by Semantic Scholar. Retrying in {retry_delay}s... (Attempt {attempt + 1}/{max_retries})")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    logger.error(f"Error fetching papers from Semantic Scholar: {e}")
                return []
        return []

    def fetch_patents(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Fetch patents from Google Patents (BigQuery)."""
        if self.bq_client:
            return self._fetch_patents_google(query, limit)
        else:
            logger.error("BigQuery client is not initialized. Cannot fetch patents.")
            return []

    def _fetch_patents_google(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Fetch FULL patents from Google Patents Public Dataset using BigQuery."""
        logger.info(f"Fetching full patents from Google Patents (BigQuery) for query: {query}")
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

            # Prepare safe query that grabs all text fields
            sql = f"""
            SELECT 
                publication_number, 
                (SELECT text FROM UNNEST(title_localized) WHERE language = 'en' LIMIT 1) as title,
                (SELECT text FROM UNNEST(abstract_localized) WHERE language = 'en' LIMIT 1) as abstract,
                (SELECT text FROM UNNEST(claims_localized) WHERE language = 'en' LIMIT 1) as claims,
                (SELECT text FROM UNNEST(description_localized) WHERE language = 'en' LIMIT 1) as description,
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

                # Using directly extracted text from BigQuery instead of scraping
                abstract_text = row.abstract or "No abstract available."
                description_text = row.description or abstract_text
                claims_text = row.claims or ""

                patents.append({
                    "doc_type": "patent",
                    "patent_id": pub_num,
                    "title": row.title or "No title available.",
                    "abstract": abstract_text,
                    "claims": claims_text,
                    "description": description_text,
                    "publication_date": str(row.publication_date),
                    "classification": row.country_code,
                    "pdf_url": pdf_url,
                    "image_paths": []
                })

            logger.info(f"Google BigQuery returned {len(patents)} patents with full text.")
            return patents
        except Exception as e:
            logger.error(f"Error fetching patents from Google BigQuery: {e}")
            return []


class PatentCorpusLoader:
    """Loader for patent datasets (e.g., USPTO, Google Patents)"""

    def __init__(self, data_dir: str):
        self.data_dir = data_dir

    def load_from_directory(self) -> List[Dict[str, Any]]:
        """Load from JSON files in the data directory."""
        if not os.path.exists(self.data_dir):
            return []

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
        return patents


class AcademicPaperLoader:
    """Loader for academic papers (e.g., Semantic Scholar)"""

    def __init__(self, data_dir: str):
        self.data_dir = data_dir

    def load_from_directory(self) -> List[Dict[str, Any]]:
        """Load from JSON files in the data directory."""
        if not os.path.exists(self.data_dir):
            return []

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
        return papers


class DataIngestionPipeline:
    def __init__(self, data_dir: str = "data", semantic_scholar_api_key: Optional[str] = None,
                 google_project_id: Optional[str] = None):
        self.data_dir = data_dir
        self.patent_loader = PatentCorpusLoader(data_dir)
        self.paper_loader = AcademicPaperLoader(data_dir)
        self.web_fetcher = WebDataFetcher(
            semantic_scholar_api_key=semantic_scholar_api_key,
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