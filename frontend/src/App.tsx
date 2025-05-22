import { CssBaseline, ThemeProvider, createTheme } from '@mui/material';
import DatasetManagement from './views/DatasetManagement';
import './App.css';

const theme = createTheme();

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <div className="app">
        <DatasetManagement />
      </div>
    </ThemeProvider>
  );
}

export default App;
