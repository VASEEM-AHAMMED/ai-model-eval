# AI Model Evaluation Platform

A comprehensive platform for evaluating and benchmarking AI models with PostgreSQL integration and advanced data processing capabilities.

## Features

- **Model Evaluation**: Compare and benchmark different AI models against various datasets
- **PostgreSQL Integration**: Robust database solution for storing evaluation metrics and datasets
- **Data Export**: Export datasets and metrics in multiple formats (JSON, CSV)
- **Advanced Search**: Filter and search through datasets and metrics with complex queries
- **Authentication**: Secure JWT-based authentication with OAuth2 password flow
- **Visualization**: Generate insights through interactive charts and graphs
- **Batch Processing**: Upload and process multiple datasets simultaneously

## Project Structure

```
ai-model-eval/
├── backend/                  # FastAPI backend
│   ├── auth.py              # Authentication services
│   ├── batch.py             # Batch processing functionality
│   ├── db/                  # Database components
│   │   ├── config.py        # Database configuration
│   │   ├── database.py      # Database connection
│   │   ├── models.py        # SQLAlchemy models
│   │   └── schemas.py       # Pydantic schemas
│   ├── exporters.py         # Data export utilities
│   ├── main.py              # API entrypoint
│   ├── reset_db.py          # Database reset utility
│   ├── search.py            # Search and filtering functionality
│   ├── setup.py             # Environment setup script
│   └── visualization.py     # Data visualization utilities
├── frontend/                 # React.js frontend
└── gen_test_datasets.py     # Test dataset generator
```

## Installation

### Requirements

- Python 3.8+ (3.10 recommended, avoid 3.13 due to compatibility issues)
- PostgreSQL 12+
- Node.js 14+ (for the frontend)

### Backend Setup

1. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. Configure database:
   - Create a PostgreSQL database named `ai_model_eval`
   - Create a `.env` file in the `backend` directory:
     ```
     DB_USER=your_username
     DB_PASSWORD=your_password
     DB_HOST=localhost
     DB_PORT=5432
     DB_NAME=ai_model_eval
     SECRET_KEY=your_secret_key_here
     ```

4. Run the setup script:
   ```bash
   python setup.py
   ```

5. Start the backend server:
   ```bash
   uvicorn main:app --reload --port 8000
   ```
   
### Frontend Setup

1. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. Start the development server:
   ```bash
   npm start
   ```

## Docker Deployment

The platform can also be deployed using Docker:

1. Build and start the containers:
   ```bash
   cd backend
   docker-compose up -d
   ```

2. Access the API at `http://localhost:8000`

## Testing

1. Generate test datasets:
   ```bash
   python gen_test_datasets.py --size medium --output test_datasets
   ```

2. Run performance tests:
   ```bash
   python test_batch_upload.py --api-url http://localhost:8000
   ```

## API Documentation

Once the server is running, you can access:
- Interactive API documentation at `/docs`
- Alternative API documentation at `/redoc`

## Database Management

- Reset database: `python backend/reset_db.py`
- Manage database: `python backend/manage_db.py --help`

## License

[MIT License](LICENSE)

## Contributors

- AI Model Evaluation Team 