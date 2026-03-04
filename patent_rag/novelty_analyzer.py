import logging
import os
import google.generativeai as genai
from typing import Dict, Any
from dotenv import load_dotenv
import requests

logger = logging.getLogger(__name__)

class NoveltyAnalyzer:
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))
        
        self.provider = os.getenv("LLM_PROVIDER", "gemini").lower()
        self.ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "llama3")
        
        if self.provider == "gemini":
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                logger.warning("GEMINI_API_KEY environment variable not set. LLM calls may fail.")
            else:
                genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(model_name)
        else:
            logger.info(f"Using Ollama local LLM: {self.ollama_model} at {self.ollama_url}")

    def analyze(self, invention_description: str, retrieval_results: Dict[str, list]) -> str:
        """
        Analyze the invention description against retrieved prior art and generate a novelty report.
        """
        logger.info("Generating novelty analysis...")
        
        context_parts = []
        
        if retrieval_results.get("similar_patents"):
            context_parts.append("--- Similar Patent Fragments ---")
            for p in retrieval_results["similar_patents"][:5]:
                meta = p['metadata']
                context_parts.append(f"Patent ID: {meta.get('parent_document_id')} (Section: {meta.get('section')})\nContent: {p['content']}")
                
        if retrieval_results.get("similar_claims"):
            context_parts.append("--- Similar Patent Claims ---")
            for c in retrieval_results["similar_claims"][:5]:
                meta = c['metadata']
                context_parts.append(f"Patent ID: {meta.get('parent_document_id')}\nClaim: {c['content']}\nSimilarity Score: {c.get('similarity_score', 0):.2f}")

        if retrieval_results.get("similar_papers"):
            context_parts.append("--- Similar Academic Papers ---")
            for p in retrieval_results["similar_papers"][:3]:
                meta = p['metadata']
                context_parts.append(f"Paper ID: {meta.get('parent_document_id')}\nContent: {p['content']}")

        full_context = "\n\n".join(context_parts)

        prompt = f"""You are an expert Patent Examiner and IP Analyst.
Analyze whether the following invention description is novel based on the retrieved prior art documents.

Invention Description:
{invention_description}

Retrieved Prior Art:
{full_context}

Please provide a detailed novelty analysis in the following format:
1. Prior Art Matches: (Summarize the closest patents and papers)
2. Claim Similarities: (Compare the core technical ideas, system components, and methods of the invention vs the retrieved claims)
3. Novelty Risk Assessment: (Conclude with a clear risk level: LOW, MEDIUM, or HIGH, accompanied by a concluding sentence)
"""

        try:
            if self.provider == "gemini":
                response = self.model.generate_content(prompt)
                return response.text
            elif self.provider == "ollama":
                payload = {
                    "model": self.ollama_model,
                    "prompt": prompt,
                    "stream": False
                }
                response = requests.post(f"{self.ollama_url}/api/generate", json=payload)
                response.raise_for_status()
                return response.json().get("response", "Error: No response from Ollama")
            else:
                return f"Error: Unknown LLM provider {self.provider}"
        except Exception as e:
            logger.error(f"Error generating novelty analysis: {e}")
            return f"Error during analysis: {e}"
