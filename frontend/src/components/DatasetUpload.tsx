import { useState } from 'react';
import { 
  Button, Card, CardContent, Typography, 
  TextField, FormControl, InputLabel, Select,
  MenuItem, LinearProgress, Alert
} from '@mui/material';
import axios from 'axios';

interface DatasetUploadProps {
  onUploadSuccess: () => void;
}

function DatasetUpload({ onUploadSuccess }: DatasetUploadProps) {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [format, setFormat] = useState('json');
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!file) {
      setError('Please select a file to upload');
      return;
    }
    
    setUploading(true);
    setError(null);
    setSuccess(null);
    
    const formData = new FormData();
    formData.append('name', name);
    formData.append('description', description);
    formData.append('format', format);
    formData.append('file', file);
    
    try {
      await axios.post('http://localhost:8000/datasets/upload/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      setSuccess('Dataset uploaded successfully');
      setName('');
      setDescription('');
      setFormat('json');
      setFile(null);
      onUploadSuccess();
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Error uploading dataset');
    } finally {
      setUploading(false);
    }
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>Upload Dataset</Typography>
        
        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
        {success && <Alert severity="success" sx={{ mb: 2 }}>{success}</Alert>}
        
        <form onSubmit={handleSubmit}>
          <TextField
            fullWidth
            label="Dataset Name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
            margin="normal"
          />
          
          <TextField
            fullWidth
            label="Description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            multiline
            rows={2}
            margin="normal"
          />
          
          <FormControl fullWidth margin="normal">
            <InputLabel id="format-label">Format</InputLabel>
            <Select
              labelId="format-label"
              value={format}
              label="Format"
              onChange={(e) => setFormat(e.target.value)}
            >
              <MenuItem value="json">JSON</MenuItem>
              <MenuItem value="csv">CSV</MenuItem>
              <MenuItem value="jsonl">JSONL</MenuItem>
            </Select>
          </FormControl>
          
          <Button
            variant="contained"
            component="label"
            fullWidth
            sx={{ mt: 2, mb: 2 }}
          >
            {file ? file.name : 'Select File'}
            <input
              type="file"
              hidden
              onChange={handleFileChange}
            />
          </Button>
          
          {uploading && <LinearProgress sx={{ mt: 2, mb: 2 }} />}
          
          <Button
            type="submit"
            variant="contained"
            color="primary"
            fullWidth
            disabled={uploading || !name || !file}
          >
            Upload Dataset
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}

export default DatasetUpload; 