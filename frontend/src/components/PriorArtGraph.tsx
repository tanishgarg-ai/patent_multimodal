import React, { useMemo } from 'react';
import ReactFlow, { 
  Background, 
  Controls, 
  Node, 
  Edge,
  MarkerType
} from 'reactflow';
import 'reactflow/dist/style.css';
import { GraphData } from '../types';

interface PriorArtGraphProps {
  data: GraphData;
  onNodeClick: (id: string) => void;
}

export const PriorArtGraph: React.FC<PriorArtGraphProps> = ({ data, onNodeClick }) => {
  const nodes: Node[] = useMemo(() => {
    return data.nodes.map((n, i) => ({
      id: n.id,
      data: { label: n.label },
      position: { 
        x: n.type === 'invention' ? 400 : 200 + (i * 150) % 400, 
        y: n.type === 'invention' ? 200 : 100 + (i * 100) % 300 
      },
      style: {
        background: n.type === 'invention' ? '#0891b2' : n.type === 'patent' ? '#1e293b' : '#334155',
        color: '#fff',
        border: n.type === 'invention' ? '2px solid #22d3ee' : '1px solid #475569',
        borderRadius: '8px',
        padding: '10px',
        fontSize: '12px',
        fontFamily: 'monospace',
        width: 120,
        textAlign: 'center',
        boxShadow: n.type === 'invention' ? '0 0 20px rgba(34, 211, 238, 0.3)' : 'none'
      }
    }));
  }, [data]);

  const edges: Edge[] = useMemo(() => {
    return data.edges.map((e, i) => ({
      id: `e-${i}`,
      source: e.source,
      target: e.target,
      label: e.label,
      labelStyle: { fill: '#94a3b8', fontSize: 10, fontFamily: 'monospace' },
      style: { stroke: '#475569', strokeWidth: 2 },
      animated: e.label.includes('Similarity'),
      markerEnd: {
        type: MarkerType.ArrowClosed,
        color: '#475569',
      },
    }));
  }, [data]);

  return (
    <div className="w-full h-full bg-slate-950 rounded-xl border border-slate-800 overflow-hidden">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodeClick={(_, node) => onNodeClick(node.id)}
        fitView
        className="bg-slate-950"
      >
        <Background color="#1e293b" gap={20} />
        <Controls className="bg-slate-900 border-slate-700 fill-slate-400" />
      </ReactFlow>
    </div>
  );
};
