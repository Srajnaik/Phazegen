import React, { useState } from 'react';
import axios from 'axios';
import {
  Container,
  Paper,
  Typography,
  TextField,
  Button,
  CircularProgress,
  Alert,
  Box,
  Grid,
  Card,
  CardContent,
  LinearProgress,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow
} from '@mui/material';
import { Upload as UploadIcon, Warning as WarningIcon } from '@mui/icons-material';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const HGTAnalyzer = () => {
  const [sequence, setSequence] = useState('');
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  const handleTextSubmit = async () => {
    if (!sequence.trim()) {
      setError('Please enter a FASTA sequence');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await axios.post(`${API_URL}/api/analyze`, {
        sequence: sequence,
        filename: 'manual_input.fasta',
        metadata: {
          source: 'manual_input',
          timestamp: new Date().toISOString()
        }
      });

      setResults(response.data.results);
    } catch (err) {
      setError(err.response?.data?.detail || 'Analysis failed');
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (event) => {
    const uploadedFile = event.target.files[0];
    if (!uploadedFile) return;

    setFile(uploadedFile);
    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', uploadedFile);

    try {
      const response = await axios.post(`${API_URL}/api/analyze/file`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      setResults(response.data.results);
    } catch (err) {
      setError(err.response?.data?.detail || 'File analysis failed');
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (level) => {
    switch (level) {
      case 'Critical': return '#d32f2f';
      case 'High': return '#f57c00';
      case 'Medium': return '#fbc02d';
      case 'Low': return '#388e3c';
      default: return '#757575';
    }
  };

  const renderRiskMeter = () => {
    if (!results) return null;

    return (
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            HGT Risk Assessment
          </Typography>
          
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <Typography variant="h3" sx={{ color: getRiskColor(results.risk_level), mr: 2 }}>
              {results.risk_score}/100
            </Typography>
            <Chip 
              label={results.risk_level} 
              sx={{ 
                backgroundColor: getRiskColor(results.risk_level),
                color: 'white',
                fontWeight: 'bold'
              }}
            />
          </Box>
          
          <LinearProgress 
            variant="determinate" 
            value={results.risk_score} 
            sx={{ 
              height: 20, 
              borderRadius: 1,
              backgroundColor: '#e0e0e0',
              '& .MuiLinearProgress-bar': {
                backgroundColor: getRiskColor(results.risk_level)
              }
            }} 
          />
          
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1 }}>
                      <Typography variant="caption">Minimal</Typography>
                      <Typography variant="caption">Severe</Typography>
                    </Box>
                  </CardContent>
                </Card>
              );
            };
          
            return (
              <Container maxWidth="lg" sx={{ py: 4 }}>
                <Typography variant="h4" gutterBottom sx={{ mb: 4 }}>
                  HGT Analyzer
                </Typography>
          
                {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
          
                <Grid container spacing={3}>
                  <Grid item xs={12} md={6}>
                    <Paper sx={{ p: 3 }}>
                      <Typography variant="h6" gutterBottom>
                        Manual Sequence Input
                      </Typography>
                      <TextField
                        fullWidth
                        multiline
                        rows={8}
                        value={sequence}
                        onChange={(e) => setSequence(e.target.value)}
                        placeholder="Paste FASTA sequence here..."
                        sx={{ mb: 2 }}
                      />
                      <Button
                        variant="contained"
                        onClick={handleTextSubmit}
                        disabled={loading}
                        fullWidth
                      >
                        {loading ? <CircularProgress size={24} /> : 'Analyze Sequence'}
                      </Button>
                    </Paper>
                  </Grid>
          
                  <Grid item xs={12} md={6}>
                    <Paper sx={{ p: 3 }}>
                      <Typography variant="h6" gutterBottom>
                        Upload FASTA File
                      </Typography>
                      <Box
                        sx={{
                          border: '2px dashed #ccc',
                          borderRadius: 1,
                          p: 3,
                          textAlign: 'center',
                          cursor: 'pointer',
                          '&:hover': { backgroundColor: '#f5f5f5' }
                        }}
                      >
                        <input
                          type="file"
                          onChange={handleFileUpload}
                          accept=".fasta,.fa,.fna"
                          style={{ display: 'none' }}
                          id="file-input"
                        />
                        <label htmlFor="file-input" style={{ cursor: 'pointer', display: 'block' }}>
                          <UploadIcon sx={{ fontSize: 48, color: '#999', mb: 1 }} />
                          <Typography>Click to upload or drag and drop</Typography>
                        </label>
                      </Box>
                    </Paper>
                  </Grid>
                </Grid>
          
                {renderRiskMeter()}
          
                {results && (
                  <Card sx={{ mt: 3 }}>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        Detailed Results
                      </Typography>
                      <TableContainer>
                        <Table>
                          <TableHead>
                            <TableRow sx={{ backgroundColor: '#f5f5f5' }}>
                              <TableCell><strong>Metric</strong></TableCell>
                              <TableCell><strong>Value</strong></TableCell>
                            </TableRow>
                          </TableHead>
                          <TableBody>
                            {Object.entries(results).map(([key, value]) => (
                              <TableRow key={key}>
                                <TableCell>{key.replace(/_/g, ' ')}</TableCell>
                                <TableCell>{JSON.stringify(value)}</TableCell>
                              </TableRow>
                            ))}
                          </TableBody>
                        </Table>
                      </TableContainer>
                    </CardContent>
                  </Card>
                )}
              </Container>
            );
          };
          
          export default HGTAnalyzer;