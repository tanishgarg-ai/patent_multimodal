import { AnalysisResponse } from "../types";

export const analyzeInvention = async (description: string, diagram?: File): Promise<AnalysisResponse> => {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 3000));

  return {
    patents: [
      {
        id: "US10345672",
        title: "Autonomous Drone Navigation with Obstacle Avoidance",
        year: 2019,
        similarityScore: 0.87,
        source: 'Patent',
        abstract: "A system for autonomous drone flight using multiple sensors to detect and avoid obstacles in real-time.",
        keyClaims: ["A method for navigating a drone using LiDAR data...", "A neural network trained on obstacle datasets..."],
        similarityBreakdown: { text: 0.85, claim: 0.92, diagram: 0.75 },
        filingDate: "2019-05-12"
      },
      {
        id: "US9876543",
        title: "Deep Learning for Real-time Object Detection",
        year: 2017,
        similarityScore: 0.72,
        source: 'Patent',
        abstract: "Methods for processing high-speed video streams to identify objects using convolutional neural networks.",
        keyClaims: ["An architecture for low-latency inference...", "A training pipeline for edge devices..."],
        similarityBreakdown: { text: 0.70, claim: 0.75, diagram: 0.60 },
        filingDate: "2017-08-20"
      }
    ],
    papers: [
      {
        id: "PAPER-2023-01",
        title: "LiDAR-based SLAM in Dynamic Environments",
        year: 2023,
        similarityScore: 0.65,
        source: 'Paper',
        abstract: "Recent advances in simultaneous localization and mapping using high-frequency LiDAR scanners.",
        keyClaims: ["Novel algorithm for dynamic point cloud filtering...", "Performance benchmarks on mobile platforms..."],
        similarityBreakdown: { text: 0.68, claim: 0.60, diagram: 0.55 },
        filingDate: "2023-01-15"
      }
    ],
    noveltyAssessment: {
      riskLevel: 'HIGH',
      explanation: "The core components of LiDAR-based navigation and deep learning for obstacle avoidance are heavily documented in US10345672.",
      claimComparison: [
        { component: "LiDAR navigation", priorArtMatch: "Patent US10345672", similarity: 0.87 },
        { component: "Deep learning model", priorArtMatch: "Patent US9876543", similarity: 0.72 },
        { component: "Real-time avoidance", priorArtMatch: "Patent US10345672", similarity: 0.91 }
      ],
      decomposition: [
        { component: "Drone navigation", isMatched: true },
        { component: "LiDAR sensing", isMatched: true },
        { component: "Deep learning model", isMatched: true },
        { component: "Real-time obstacle avoidance", isMatched: true },
        { component: "Quantum-encrypted telemetry", isMatched: false }
      ]
    },
    graphData: {
      nodes: [
        { id: 'invention', label: 'Your Invention', type: 'invention' },
        { id: 'US10345672', label: 'US10345672', type: 'patent' },
        { id: 'US9876543', label: 'US9876543', type: 'patent' },
        { id: 'PAPER-2023-01', label: 'SLAM Paper', type: 'paper' }
      ],
      edges: [
        { source: 'invention', target: 'US10345672', label: 'High Similarity' },
        { source: 'invention', target: 'US9876543', label: 'Moderate Similarity' },
        { source: 'invention', target: 'PAPER-2023-01', label: 'Contextual' },
        { source: 'US10345672', target: 'US9876543', label: 'Cites' }
      ]
    }
  };
};
