import os
import json
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

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
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.patent_loader = PatentCorpusLoader(data_dir)
        self.paper_loader = AcademicPaperLoader(data_dir)
        
    def ingest_all(self) -> List[Dict[str, Any]]:
        """Ingest both patents and academic papers."""
        documents = []
        documents.extend(self.patent_loader.load_from_directory())
        documents.extend(self.paper_loader.load_from_directory())
        logger.info(f"Ingested {len(documents)} documents total.")
        return documents

