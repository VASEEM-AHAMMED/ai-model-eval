import { useState, useEffect } from 'react';
import { Typography, Grid, Paper, CircularProgress, Alert } from '@mui/material';
import { Bar, Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';
import axios from 'axios';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend
);

interface MetricsVisualizationProps {
  datasetId: string;
}

interface DatasetMetrics {
  accuracy: number;
  precision: number;
  recall: number;
  f1_score: number;
  latency: number[];
  timestamps: string[];
  distribution: {
    categories: string[];
    counts: number[];
  };
}

function MetricsVisualization({ datasetId }: MetricsVisualizationProps) {
  const [metrics, setMetrics] = useState<DatasetMetrics | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchMetrics = async () => {
      setLoading(true);
      setError(null);
      
      try {
        const response = await axios.get(`http://localhost:8000/datasets/${datasetId}/metrics/`);
        setMetrics(response.data);
      } catch (error) {
        console.error('Error fetching metrics:', error);
        setError('Failed to load metrics data. Please try again later.');
      } finally {
        setLoading(false);
      }
    };
    
    fetchMetrics();
  }, [datasetId]);

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', padding: '3rem' }}>
        <CircularProgress />
      </div>
    );
  }

  if (error) {
    return <Alert severity="error">{error}</Alert>;
  }

  if (!metrics) {
    return <Alert severity="info">No metrics data available for this dataset.</Alert>;
  }

  // Performance Metrics Chart
  const performanceData = {
    labels: ['Accuracy', 'Precision', 'Recall', 'F1 Score'],
    datasets: [
      {
        label: 'Performance Metrics',
        data: [
          metrics.accuracy,
          metrics.precision,
          metrics.recall,
          metrics.f1_score
        ],
        backgroundColor: [
          'rgba(54, 162, 235, 0.6)',
          'rgba(75, 192, 192, 0.6)',
          'rgba(255, 206, 86, 0.6)',
          'rgba(153, 102, 255, 0.6)',
        ],
        borderColor: [
          'rgba(54, 162, 235, 1)',
          'rgba(75, 192, 192, 1)',
          'rgba(255, 206, 86, 1)',
          'rgba(153, 102, 255, 1)',
        ],
        borderWidth: 1,
      },
    ],
  };

  // Latency Chart
  const latencyData = {
    labels: metrics.timestamps,
    datasets: [
      {
        label: 'Response Latency (ms)',
        data: metrics.latency,
        fill: false,
        borderColor: 'rgb(75, 192, 192)',
        tension: 0.1,
      },
    ],
  };

  // Distribution Chart
  const distributionData = {
    labels: metrics.distribution.categories,
    datasets: [
      {
        label: 'Distribution',
        data: metrics.distribution.counts,
        backgroundColor: 'rgba(255, 99, 132, 0.6)',
        borderColor: 'rgba(255, 99, 132, 1)',
        borderWidth: 1,
      },
    ],
  };

  return (
    <div>
      <Typography variant="h5" gutterBottom>Dataset Metrics Analysis</Typography>
      
      <Grid container spacing={4}>
        {/* Performance Metrics */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>Performance Metrics</Typography>
            <Bar data={performanceData} options={{ responsive: true }} />
          </Paper>
        </Grid>
        
        {/* Distribution Chart */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>Data Distribution</Typography>
            <Bar data={distributionData} options={{ responsive: true }} />
          </Paper>
        </Grid>
        
        {/* Latency Chart */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>Response Latency Over Time</Typography>
            <Line data={latencyData} options={{ responsive: true }} />
          </Paper>
        </Grid>
        
        {/* Key Metrics Table */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>Key Performance Indicators</Typography>
            <Grid container spacing={2}>
              <Grid item xs={6} sm={3}>
                <Typography variant="body2" color="text.secondary">Accuracy</Typography>
                <Typography variant="h6">{(metrics.accuracy * 100).toFixed(2)}%</Typography>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Typography variant="body2" color="text.secondary">Precision</Typography>
                <Typography variant="h6">{(metrics.precision * 100).toFixed(2)}%</Typography>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Typography variant="body2" color="text.secondary">Recall</Typography>
                <Typography variant="h6">{(metrics.recall * 100).toFixed(2)}%</Typography>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Typography variant="body2" color="text.secondary">F1 Score</Typography>
                <Typography variant="h6">{(metrics.f1_score * 100).toFixed(2)}%</Typography>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </div>
  );
}

export default MetricsVisualization; 