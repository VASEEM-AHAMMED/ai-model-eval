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

## API Endpoints

- `GET /datasets/`: List all datasets
- `POST /datasets/upload/`: Upload a new dataset
- `GET /datasets/{dataset_id}`: Get a specific dataset
- `DELETE /datasets/{dataset_id}`: Delete a dataset
- `POST /datasets/{dataset_id}/metrics/`: Create metrics for a dataset
- `GET /datasets/{dataset_id}/metrics/`: Get all metrics for a dataset
- `GET /metrics/{metrics_id}`: Get specific metrics
- `DELETE /metrics/{metrics_id}`: Delete specific metrics 