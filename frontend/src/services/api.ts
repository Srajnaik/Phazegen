import axios from 'axios';

const API_URL = 'http://localhost:8000';

export interface ResistanceGene {
  gene: string;
  class: string;
  confidence: number;
}

export interface ProteinStructure {
  structure_id: string;
  confidence_score: number;
  folding_type: string;
  description: string;
  molecular_weight: string;
}

// --- NEW TYPES START ---
export interface VirulenceData {
  virulenceScore: number;
  factors: string[];
}

export interface HgtData {
  risk: string;
  score: number;
}
// --- NEW TYPES END ---

export interface AnalysisResult {
  metadata: {
    length: number;
    gc_content: number;
    orf_count: number;
  };
  resistance_genes: ResistanceGene[];
  crispr_status: string;
  risk_score: number;
  risk_level: string;
  explanation: string;
  protein_structure: ProteinStructure | null;
  
  // --- NEW FIELDS ---
  advanced_ml?: {
    virulence: VirulenceData;
    hgt_risk: HgtData;
  };
}

export const analyzeText = async (sequence: string) => {
  const response = await axios.post<AnalysisResult>(`${API_URL}/analyze/text`, { sequence });
  return response.data;
};

export const analyzeFile = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await axios.post<AnalysisResult>(`${API_URL}/analyze/file`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};