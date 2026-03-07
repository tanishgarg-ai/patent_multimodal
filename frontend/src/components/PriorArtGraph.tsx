import React, { useMemo } from 'react';
import { ReactFlow, Background, Controls, Node, Edge, MarkerType } from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { useChatContext } from '../context/ChatContext';
import { Network } from 'lucide-react';

export const PriorArtGraph = () => {
  const { analysisResult } = useChatContext();

  const { nodes, edges } = useMemo(() => {
    if (!analysisResult?.graph_data) {
      return { nodes: [], edges: [] };
    }

    const graphData = analysisResult.graph_data;
    
    const initialNodes: Node[] = [
      {
        id: 'user_invention',
        type: 'default',
        data: { label: 'User Invention' },
        position: { x: 250, y: 50 },
        style: { background: '#0891b2', color: '#fff', border: 'none', borderRadius: '8px', padding: '10px' },
      },
    ];

    const initialEdges: Edge[] = [];

    if (graphData.nodes) {
      graphData.nodes.forEach((node: any, idx: number) => {
        initialNodes.push({
          id: node.id,
          type: 'default',
          data: { label: node.label || `Patent ${idx + 1}` },
          position: { x: 100 + idx * 150, y: 200 + (idx % 2) * 50 },
          style: { background: '#1e293b', color: '#cbd5e1', border: '1px solid #334155', borderRadius: '8px', padding: '10px' },
        });

        initialEdges.push({
          id: `e-user-${node.id}`,
          source: 'user_invention',
          target: node.id,
          animated: true,
          style: { stroke: '#0ea5e9', strokeWidth: 2 },
          markerEnd: { type: MarkerType.ArrowClosed, color: '#0ea5e9' },
        });
      });
    }

    return { nodes: initialNodes, edges: initialEdges };
  }, [analysisResult]);

  if (!analysisResult?.graph_data) {
    return (
      <div className="flex flex-col h-full bg-slate-900 border-t border-slate-800 items-center justify-center text-slate-500">
        <Network className="w-8 h-8 mb-2 opacity-50" />
        <p className="text-sm">Prior art relationship graph will appear here.</p>
      </div>
    );
  }

  return (
    <div className="h-full w-full bg-slate-900 border-t border-slate-800 relative">
      <div className="absolute top-4 left-4 z-10 bg-slate-800/80 backdrop-blur-sm px-3 py-1.5 rounded-md border border-slate-700 flex items-center gap-2">
        <Network className="w-4 h-4 text-cyan-400" />
        <span className="text-xs font-medium text-slate-200 uppercase tracking-wider">Relationship Graph</span>
      </div>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        fitView
        className="bg-slate-900"
        proOptions={{ hideAttribution: true }}
      >
        <Background color="#334155" gap={16} />
        <Controls className="bg-slate-800 border-slate-700 fill-slate-400" />
      </ReactFlow>
    </div>
  );
};
