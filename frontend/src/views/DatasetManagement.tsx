import { useState, useEffect } from 'react';
import { 
  Typography, Card, CardContent, TextField, 
  Button, Dialog, AppBar, Toolbar, IconButton, 
  Table, TableBody, TableCell, TableHead, TableRow, TableContainer, Paper
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import DatasetUpload from '../components/DatasetUpload';
import MetricsVisualization from '../components/MetricsVisualization';
import axios from 'axios';

interface Dataset {
  id: string;
  name: string;
  description: string;
  format: string;
  size: string;
  created_at: string;
}

function DatasetManagement() {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [search, setSearch] = useState<string>('');
  const [metricsDialog, setMetricsDialog] = useState<boolean>(false);
  const [selectedDataset, setSelectedDataset] = useState<Dataset | null>(null);

  const fetchDatasets = async () => {
    setLoading(true);
    try {
      const response = await axios.get('http://localhost:8000/datasets/');
      setDatasets(response.data);
    } catch (error) {
      console.error('Error fetching datasets:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleUploadSuccess = () => {
    fetchDatasets();
  };

  const viewMetrics = (dataset: Dataset) => {
    setSelectedDataset(dataset);
    setMetricsDialog(true);
  };

  useEffect(() => {
    fetchDatasets();
  }, []);

  const filteredDatasets = datasets.filter((dataset) => {
    return Object.values(dataset).some((value) => 
      value?.toString().toLowerCase().includes(search.toLowerCase())
    );
  });

  return (
    <div className="dataset-management">
      <Typography variant="h4" sx={{ mb: 6 }}>Dataset Management</Typography>
      
      {/* Dataset Upload Section */}
      <section style={{ marginBottom: '2rem' }}>
        <DatasetUpload onUploadSuccess={handleUploadSuccess} />
      </section>
      
      {/* Dataset List and Metrics */}
      <section>
        <Card>
          <CardContent sx={{ padding: '0 1rem 1rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '1rem 0' }}>
              <Typography variant="h6">Datasets</Typography>
              <TextField
                label="Search"
                variant="outlined"
                size="small"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>
            
            <TableContainer component={Paper}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Name</TableCell>
                    <TableCell>Description</TableCell>
                    <TableCell>Format</TableCell>
                    <TableCell>Size</TableCell>
                    <TableCell>Created At</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {loading ? (
                    <TableRow>
                      <TableCell colSpan={6} align="center">Loading...</TableCell>
                    </TableRow>
                  ) : filteredDatasets.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={6} align="center">No datasets found</TableCell>
                    </TableRow>
                  ) : (
                    filteredDatasets.map((dataset) => (
                      <TableRow key={dataset.id}>
                        <TableCell>{dataset.name}</TableCell>
                        <TableCell>{dataset.description}</TableCell>
                        <TableCell>{dataset.format}</TableCell>
                        <TableCell>{dataset.size}</TableCell>
                        <TableCell>{dataset.created_at}</TableCell>
                        <TableCell>
                          <Button
                            color="primary"
                            onClick={() => viewMetrics(dataset)}
                          >
                            View Metrics
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>
      </section>
      
      {/* Metrics Dialog */}
      <Dialog
        fullScreen
        open={metricsDialog}
        onClose={() => setMetricsDialog(false)}
      >
        <AppBar sx={{ position: 'relative' }}>
          <Toolbar>
            <IconButton
              edge="start"
              color="inherit"
              onClick={() => setMetricsDialog(false)}
              aria-label="close"
            >
              <CloseIcon />
            </IconButton>
            <Typography sx={{ ml: 2, flex: 1 }} variant="h6">
              Dataset Metrics
            </Typography>
          </Toolbar>
        </AppBar>
        <div style={{ padding: '2rem' }}>
          {selectedDataset && (
            <MetricsVisualization datasetId={selectedDataset.id} />
          )}
        </div>
      </Dialog>
    </div>
  );
}

export default DatasetManagement; 