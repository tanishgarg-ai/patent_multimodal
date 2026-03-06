export interface Patent {
  id: string;
  title: string;
  year: number;
  similarityScore: number;
  source: 'Patent' | 'Paper';
  abstract: string;
  keyClaims: string[];
  similarityBreakdown: {
    text: number;
    claim: number;
    diagram: number;
  };
  filingDate: string;
  pdfUrl?: string;
}

export interface ClaimMatch {
  component: string;
  priorArtMatch: string;
  similarity: number;
}

export interface NoveltyAssessment {
  riskLevel: 'LOW' | 'MEDIUM' | 'HIGH';
  explanation: string;
  claimComparison: ClaimMatch[];
  decomposition: {
    component: string;
    isMatched: boolean;
  }[];
}

export interface GraphData {
  nodes: { id: string; label: string; type: string }[];
  edges: { source: string; target: string; label: string }[];
}

export interface AnalysisResponse {
  patents: Patent[];
  papers: Patent[];
  noveltyAssessment: NoveltyAssessment;
  graphData: GraphData;
}
