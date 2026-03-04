import logging
from typing import List, Dict, Any

from vector_store import PatentVectorStore

logger = logging.getLogger(__name__)

class PatentRetrievalEngine:
    def __init__(self, vector_store: PatentVectorStore):
        self.vector_store = vector_store

    def retrieve_similar_documents(self, invention_description: str, top_k: int = 10) -> Dict[str, List[Dict]]:
        """
        Retrieve similar patents and papers based on the invention description.
        Returns a dictionary separating patents, papers, and specifically claim matches.
        """
        logger.info(f"Retrieving top {top_k} documents for description...")
        
        # General retrieval across all docs
        all_results = self.vector_store.similarity_search(
            query=invention_description,
            n_results=top_k * 2  # get extra to distribute
        )
        
        patents = []
        papers = []
        claims = []
        
        for res in all_results:
            doc_type = res["metadata"].get("doc_type")
            section = res["metadata"].get("section")
            
            if doc_type == "patent":
                if section == "claims":
                    if len(claims) < top_k:
                        claims.append(res)
                else:
                    if len(patents) < top_k:
                        patents.append(res)
            elif doc_type == "paper":
                if len(papers) < top_k:
                    papers.append(res)
                    
        logger.info(f"Retrieved {len(patents)} patent chunks, {len(papers)} paper chunks, {len(claims)} claim chunks.")
        
        return {
            "similar_patents": patents,
            "similar_papers": papers,
            "similar_claims": claims
        }
