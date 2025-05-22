# AI Model Evaluation Platform - Backend

This directory contains the backend API for the AI Model Evaluation Platform.

## Setup

1. Create a virtual environment:
```bash
cd backend
python3 -m venv env
source env/bin/activate
```

2. Install dependencies:
```bash
pip install fastapi uvicorn python-multipart
```

## Running the Server

To run the backend server:

```bash
source env/bin/activate
uvicorn simple_backend:app --reload --port 8080
```

The API will be available at http://localhost:8080

## API Endpoints

- `GET /` - Welcome message
- `GET /datasets/` - List all datasets
- `POST /datasets/upload/` - Upload a new dataset
- `GET /datasets/{dataset_id}` - Get dataset details
- `GET /datasets/{dataset_id}/metrics/` - Get metrics for a dataset 