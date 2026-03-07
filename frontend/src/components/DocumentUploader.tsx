import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { UploadCloud, FileText, Loader2 } from 'lucide-react';
import { uploadDocuments } from '../services/api';
import { useChatContext } from '../context/ChatContext';
import { DocumentCard } from './DocumentCard';

export const DocumentUploader = () => {
  const [isUploading, setIsUploading] = useState(false);
  const { documents, setDocuments } = useChatContext();

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return;
    setIsUploading(true);
    try {
      const data = await uploadDocuments(acceptedFiles);
      if (data.results) {
        setDocuments((prev) => [...prev, ...data.results]);
      }
    } catch (error) {
      console.error('Upload failed:', error);
    } finally {
      setIsUploading(false);
    }
  }, [setDocuments]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({ 
    onDrop: onDrop as any, 
    accept: { 'application/pdf': ['.pdf'] } 
  } as any);

  return (
    <div className="flex flex-col h-full bg-slate-900 border-r border-slate-800 p-4 overflow-y-auto">
      <h2 className="text-lg font-semibold text-slate-100 mb-4 flex items-center gap-2">
        <FileText className="w-5 h-5 text-cyan-400" />
        Document Library
      </h2>
      
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-xl p-6 flex flex-col items-center justify-center text-center cursor-pointer transition-colors mb-6 ${
          isDragActive ? 'border-cyan-400 bg-cyan-400/10' : 'border-slate-700 hover:border-slate-500 bg-slate-800/50'
        }`}
      >
        <input {...getInputProps()} />
        {isUploading ? (
          <Loader2 className="w-8 h-8 text-cyan-400 animate-spin mb-2" />
        ) : (
          <UploadCloud className="w-8 h-8 text-slate-400 mb-2" />
        )}
        <p className="text-sm text-slate-300">
          {isUploading ? 'Uploading & Indexing...' : isDragActive ? 'Drop PDFs here' : 'Drag & drop PDFs here, or click to select'}
        </p>
      </div>

      <div className="flex-1 overflow-y-auto space-y-3 pr-2">
        {documents.map((doc, idx) => (
          <DocumentCard key={idx} document={doc} />
        ))}
        {documents.length === 0 && !isUploading && (
          <div className="text-center text-slate-500 text-sm mt-10">
            No documents uploaded yet.
          </div>
        )}
      </div>
    </div>
  );
};
