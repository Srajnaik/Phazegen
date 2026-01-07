import { useState } from 'react';
import { Dna } from 'lucide-react';
import GenomeUpload from './components/GenomeUpload';
import ResultsDashboard from './components/ResultsDashboard';
import { analyzeText, analyzeFile, type AnalysisResult } from './services/api';

function App() {
  const [results, setResults] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async (data: any, type: 'text' | 'file') => {
    setLoading(true);
    setError(null);
    setResults(null);

    try {
      let res;
      if (type === 'text') {
        res = await analyzeText(data);
      } else {
        res = await analyzeFile(data);
      }
      setResults(res);
    } catch (err: any) {
      console.error(err);
      setError(err.response?.data?.detail || "An error occurred during analysis");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-wrapper">
      {/* Header */}
      <header className="header">
        <div className="container flex-row space-between">
          <div className="flex-row">
            <div style={{ background: 'var(--primary)', padding: '6px', borderRadius: '6px' }}>
              <Dna size={24} color="white" />
            </div>
            <div>
              <h1 style={{ fontSize: '1.25rem', fontWeight: 'bold' }}>PhazeGEN</h1>
              <p style={{ fontSize: '0.75rem', color: 'var(--primary)' }}>AI-Driven Antimicrobial Analysis</p>
            </div>
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontFamily: 'monospace' }}>
            v1.0.0-beta
          </div>
        </div>
      </header>

      <main className="container">
        <div style={{ marginBottom: '2rem' }}>
          <h2 style={{ fontSize: '1.8rem', marginBottom: '0.5rem' }}>Genome Analysis Platform</h2>
          <p style={{ color: 'var(--text-muted)' }}>
            Upload FASTA sequences to detect antibiotic resistance genes, CRISPR systems, 
            and predict relevant protein structures using our AI pipeline.
          </p>
        </div>

        {/* Input Section */}
        <div style={{ marginBottom: '2.5rem' }}>
          <GenomeUpload onAnalyze={handleAnalyze} isLoading={loading} />
        </div>

        {/* Error State */}
        {error && (
          <div className="card" style={{ borderColor: 'var(--danger)', background: 'var(--danger-bg)', marginBottom: '2rem' }}>
            <p style={{ fontWeight: 'bold', color: 'var(--danger)' }}>Analysis Failed</p>
            <p>{error}</p>
          </div>
        )}

        {/* Results Section */}
        {results && <ResultsDashboard results={results} />}
      </main>
    </div>
  );
}

export default App;