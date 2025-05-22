# AI Model Evaluation Platform - Backend

This is the backend service for the AI Model Evaluation Platform. It provides APIs for uploading datasets, tracking model metrics, and evaluating AI model performance.

## Database Setup

The application uses PostgreSQL as the primary database, with an optional fallback to SQLite.

### PostgreSQL Setup

1. Install PostgreSQL on your system if not already installed.
2. Create a database for the application:

```bash
createdb ai_model_eval
```

3. The application will automatically use your current system username to connect to PostgreSQL. If you need to use different credentials, create a `.env` file in the backend directory with the following content:

```
DB_USER=your_username
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ai_model_eval
SECRET_KEY=your_secure_secret_key_for_authentication
```

### Database Management

You can use the `manage_db.py` script to check your database connection and manage datasets:

```bash
# Check database connection
python manage_db.py check

# List all datasets
python manage_db.py list-datasets

# List metrics for a specific dataset
python manage_db.py list-metrics --dataset-id 1

# Initialize database schema
python manage_db.py init
```

## Running the Application

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

2. Start the FastAPI server:

```bash
uvicorn main:app --reload --port 8091 --host 0.0.0.0
```

3. The API will be available at http://localhost:8091

4. Access the API documentation at http://localhost:8091/docs

## Features

### Authentication

The API includes OAuth2 authentication. To access protected endpoints, you need to:

1. Obtain an access token using the `/token` endpoint:

```bash
curl -X POST "http://localhost:8091/token" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=admin&password=adminpassword"
```

2. Use the token in the Authorization header:

```bash
curl -X GET "http://localhost:8091/datasets/" \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Data Export

The API allows exporting datasets and metrics in different formats:

- Export dataset with metrics to JSON: `/datasets/{dataset_id}/export/json`
- Export metrics to CSV: `/datasets/{dataset_id}/export/metrics/csv`

### Search and Filtering

You can search and filter datasets and metrics:

- Dataset search: `/datasets/search`
- Metrics search: `/metrics/search`

### Batch Operations

The API supports batch operations:

- Upload multiple datasets: `/datasets/batch-upload`
- Upload a zip archive of datasets: `/datasets/upload-zip`
- Create multiple metrics entries: `/datasets/{dataset_id}/metrics/batch`

### Visualization Data

The API provides endpoints to get data for visualizations:

- Accuracy comparison: `/visualizations/accuracy-comparison`
- Latency data: `/visualizations/latency-data`
- Distribution data: `/visualizations/distribution`
- Model performance over time: `/visualizations/models-over-time`

## API Endpoints

### Dataset Operations
- `GET /datasets/`: List all datasets
- `POST /datasets/upload/`: Upload a new dataset
- `POST /datasets/batch-upload`: Upload multiple datasets
- `POST /datasets/upload-zip`: Upload a zip file with datasets
- `GET /datasets/{dataset_id}`: Get a specific dataset
- `DELETE /datasets/{dataset_id}`: Delete a dataset
- `POST /datasets/search`: Search datasets with filters

### Metrics Operations
- `POST /datasets/{dataset_id}/metrics/`: Create metrics for a dataset
- `POST /datasets/{dataset_id}/metrics/batch`: Create multiple metrics entries
- `GET /datasets/{dataset_id}/metrics/`: Get all metrics for a dataset
- `GET /metrics/search`: Search metrics with filters
- `GET /metrics/{metrics_id}`: Get specific metrics
- `DELETE /metrics/{metrics_id}`: Delete specific metrics

### Export Operations
- `GET /datasets/{dataset_id}/export/json`: Export dataset and metrics to JSON
- `GET /datasets/{dataset_id}/export/metrics/csv`: Export metrics to CSV

### Visualization Data
- `GET /visualizations/accuracy-comparison`: Get accuracy comparison data
- `GET /visualizations/latency-data`: Get latency data
- `GET /visualizations/distribution`: Get distribution data
- `GET /visualizations/models-over-time`: Get model performance over time

### Authentication
- `POST /token`: Get access token
- `GET /users/me`: Get current user info 