import React, { useState } from 'react';
import { Upload, FileText, Activity } from 'lucide-react';

interface Props {
  onAnalyze: (data: any, type: 'text' | 'file') => void;
  isLoading: boolean;
}

const GenomeUpload: React.FC<Props> = ({ onAnalyze, isLoading }) => {
  const [activeTab, setActiveTab] = useState<'file' | 'text'>('text');
  const [textInput, setTextInput] = useState('');
  const [fileInput, setFileInput] = useState<File | null>(null);

  const handleSubmit = () => {
    if (activeTab === 'text' && textInput) {
      onAnalyze(textInput, 'text');
    } else if (activeTab === 'file' && fileInput) {
      onAnalyze(fileInput, 'file');
    }
  };

  return (
    <div className="card">
      <div className="flex-row" style={{ marginBottom: '1.5rem' }}>
        <button
          onClick={() => setActiveTab('text')}
          className={`btn btn-toggle ${activeTab === 'text' ? 'active' : ''}`}
        >
          <FileText size={18} /> Raw Sequence
        </button>
        <button
          onClick={() => setActiveTab('file')}
          className={`btn btn-toggle ${activeTab === 'file' ? 'active' : ''}`}
        >
          <Upload size={18} /> Upload FASTA
        </button>
      </div>

      <div style={{ marginBottom: '1rem', minHeight: '200px' }}>
        {activeTab === 'text' ? (
          <textarea
            className="input-area"
            placeholder=">Paste Genome Sequence (ATCG...)"
            value={textInput}
            onChange={(e) => setTextInput(e.target.value)}
          />
        ) : (
          <div className="upload-box">
            <input
              type="file"
              accept=".fasta,.txt"
              onChange={(e) => setFileInput(e.target.files ? e.target.files[0] : null)}
              style={{ display: 'none' }}
              id="file-upload"
            />
            <label htmlFor="file-upload" style={{ textAlign: 'center', cursor: 'pointer' }}>
              <Upload size={32} style={{ margin: '0 auto 0.5rem auto', color: 'var(--primary)' }} />
              <p style={{ color: 'var(--text-muted)' }}>
                {fileInput ? fileInput.name : 'Click to Upload FASTA'}
              </p>
            </label>
          </div>
        )}
      </div>

      <button
        onClick={handleSubmit}
        disabled={isLoading || (activeTab === 'text' && !textInput) || (activeTab === 'file' && !fileInput)}
        className="btn btn-primary"
        style={{ width: '100%' }}
      >
        {isLoading ? (
          <span>Processing Genome...</span>
        ) : (
          <>
            <Activity size={20} /> Run PhazeGEN Analysis
          </>
        )}
      </button>
    </div>
  );
};

export default GenomeUpload;