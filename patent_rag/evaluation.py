import logging
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class EvaluationModule:
    """
    Evaluation utilities reused from Advanced RAG pipeline.
    """
    def __init__(self):
        # Set plotting style
        sns.set_theme(style="whitegrid")

    def evaluate_retrieval(self, ground_truths: List[str], retrieved_ids: List[List[str]], k_values: List[int] = [1, 5, 10]) -> Dict[str, float]:
        """
        Calculate Precision@K based on a list of ground truth IDs vs retrieved IDs.
        """
        results = {}
        for k in k_values:
            precisions = []
            for gt, retrieved in zip(ground_truths, retrieved_ids):
                top_k = retrieved[:k]
                if gt in top_k:
                    # Simple hit rate for precision@k
                    precisions.append(1.0)
                else:
                    precisions.append(0.0)
            results[f"precision@{k}"] = sum(precisions) / len(precisions) if precisions else 0.0
            
        logger.info(f"Retrieval evaluation results: {results}")
        return results

    def plot_similarity_distribution(self, similar_results: List[Dict[str, Any]], output_path: str = "similarity_distribution.png"):
        """
        Plot distribution of similarity scores.
        """
        if not similar_results:
            logger.warning("No results to plot.")
            return
            
        scores = [res.get("similarity_score", 0.0) for res in similar_results]
        
        plt.figure(figsize=(10, 6))
        sns.histplot(scores, bins=20, kde=True, color="skyblue")
        plt.title("Distribution of Document Similarity Scores")
        plt.xlabel("Similarity Score")
        plt.ylabel("Frequency")
        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()
        logger.info(f"Saved similarity distribution plot to {output_path}")

    def plot_response_latency(self, latencies: List[float], output_path: str = "latency_plot.png"):
        """
        Plot response latency.
        """
        if not latencies:
            return
            
        plt.figure(figsize=(10, 6))
        plt.plot(latencies, marker='o', linestyle='-', color='coral')
        plt.title("System Response Latency Over Time")
        plt.xlabel("Query Number")
        plt.ylabel("Latency (seconds)")
        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()
        logger.info(f"Saved latency plot to {output_path}")
