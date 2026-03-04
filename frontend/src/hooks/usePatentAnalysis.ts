import { useState } from 'react';
import { analyzeInvention } from '../services/api';
import { AnalysisResponse } from '../types';

export function usePatentAnalysis() {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [results, setResults] = useState<AnalysisResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [step, setStep] = useState<string>('');

  const runAnalysis = async (description: string, diagram?: File) => {
    setIsAnalyzing(true);
    setError(null);
    setResults(null);

    const steps = [
      "Parsing invention description...",
      "Searching patent corpus...",
      "Analyzing claims...",
      "Generating novelty assessment..."
    ];

    try {
      // Simulate step updates
      for (let i = 0; i < steps.length; i++) {
        setStep(steps[i]);
        await new Promise(r => setTimeout(r, 800));
      }

      const data = await analyzeInvention(description, diagram);
      setResults(data);
    } catch (err) {
      setError("Analysis failed. Please try again.");
    } finally {
      setIsAnalyzing(false);
      setStep('');
    }
  };

  return { isAnalyzing, results, error, runAnalysis, step };
}
