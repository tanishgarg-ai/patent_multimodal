import { AnalysisResponse, Patent, NoveltyAssessment, GraphData } from "../types";

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const analyzeInvention = async (description: string, diagram?: File): Promise<AnalysisResponse> => {
  try {
    const response = await fetch(`${API_URL}/api/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        description,
        diagram: null // File uploading logic can be added here later if needed
      }),
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`);
    }

    const data = await response.json();

    // Helper function to map dynamic backend fields to frontend Patent type
    const mapDocument = (doc: any, defaultSource: 'Patent' | 'Paper'): Patent => ({
      id: doc.id || doc.patent_number || doc.document_id || `DOC-${Math.floor(Math.random() * 10000)}`,
      title: doc.title || 'Unknown Title',
      year: doc.year || (doc.publication_date ? parseInt(doc.publication_date.substring(0, 4)) : new Date().getFullYear()),
      similarityScore: doc.similarity_score || doc.score || 0.0,
      source: defaultSource,
      abstract: doc.abstract || 'No abstract available',
      keyClaims: doc.claims || doc.key_claims || [],
      similarityBreakdown: doc.similarityBreakdown || doc.similarity_breakdown || { text: doc.similarity_score || 0, claim: 0, diagram: 0 },
      filingDate: doc.filing_date || doc.publication_date || "Unknown",
      pdfUrl: doc.pdf_url || doc.pdfUrl || undefined
    });

    const mappedPatents = (data.patents || []).map((p: any) => mapDocument(p, 'Patent'));
    const mappedPapers = (data.papers || []).map((p: any) => mapDocument(p, 'Paper'));

    // Since the backend currently returns a mocked or basic structure for novelty_assessment, 
    // handle fallback mapping to prevent frontend breakage.
    const noveltyAssessment: NoveltyAssessment = {
      riskLevel: data.novelty_assessment?.risk_level === 'UNKNOWN' ? 'MEDIUM' : (data.novelty_assessment?.risk_level || 'MEDIUM'),
      explanation: data.novelty_assessment?.details !== "See analysis_report" ? data.novelty_assessment?.details : (data.analysis_report || "The system analyzed the provided description and evaluated potential risks."),
      claimComparison: data.novelty_assessment?.claim_comparison || [],
      decomposition: data.novelty_assessment?.decomposition || []
    };

    const graphData: GraphData = {
      nodes: data.graph_data?.nodes || [],
      edges: data.graph_data?.edges || []
    };

    return {
      patents: mappedPatents,
      papers: mappedPapers,
      noveltyAssessment,
      graphData
    };
  } catch (error) {
    console.error("Error analyzing invention:", error);
    throw error;
  }
};

