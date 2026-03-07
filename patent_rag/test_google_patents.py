import os
import json
import logging
from dotenv import load_dotenv
try:
    from google.cloud import bigquery
except ImportError:
    bigquery = None

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_google_patents():
    if not bigquery:
        print("Error: google-cloud-bigquery library not installed.")
        return

    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    if not project_id or project_id == "your_google_cloud_project_id_here":
        print("Error: GOOGLE_CLOUD_PROJECT not set in .env")
        return

    query_str = "LiDAR navigation drone" # Removed "based", "for", and "s" from drones for broader matching
    logger.info(f"Testing Google Patents BigQuery for query: {query_str}")
    
    # Break query into keywords
    keywords = [word.lower() for word in query_str.split()]
    
    # Dynamically build the AND conditions for the SQL query
    title_conditions = " AND ".join([f"LOWER(t.text) LIKE '%{kw}%'" for kw in keywords])
    abstract_conditions = " AND ".join([f"LOWER(a.text) LIKE '%{kw}%'" for kw in keywords])
    
    try:
        client = bigquery.Client(project=project_id)
        
        # SQL query searching for independent keywords anywhere in the text
        sql = f"""
        SELECT publication_number, 
               (SELECT text FROM UNNEST(title_localized) WHERE language = 'en' LIMIT 1) as title,
               (SELECT text FROM UNNEST(abstract_localized) WHERE language = 'en' LIMIT 1) as abstract,
               publication_date,
               country_code
        FROM `patents-public-data.patents.publications`
        WHERE (EXISTS (SELECT 1 FROM UNNEST(title_localized) t WHERE t.language = 'en' AND {title_conditions}))
           OR (EXISTS (SELECT 1 FROM UNNEST(abstract_localized) a WHERE a.language = 'en' AND {abstract_conditions}))
        LIMIT 5
        """
        
        print(f"Executing query on project: {project_id}...")
        query_job = client.query(sql)
        results = query_job.result()
        
        count = 0
        for row in results:
            count += 1
            print(f"\nResult {count}:")
            print(f"Publication Number: {row.publication_number}")
            print(f"Title: {row.title}")
            print(f"Date: {row.publication_date}")
            print(f"Country: {row.country_code}")
            
        if count == 0:
            print("No results found.")
            
    except Exception as e:
        print(f"Error executing BigQuery: {e}")
        print("\nNote: Ensure you are authenticated via 'gcloud auth application-default login'")

if __name__ == "__main__":
    test_google_patents()