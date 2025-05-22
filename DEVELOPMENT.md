# Development Guide for AI Model Evaluation Platform

This guide is intended for developers who want to contribute to the AI Model Evaluation Platform.

## Development Environment Setup

### Prerequisites

- Python 3.10 (recommended)
- PostgreSQL 12+
- Node.js 14+
- Git

### Setting Up the Development Environment

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ai-model-eval.git
   cd ai-model-eval
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install development dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # If available
   ```

4. Set up PostgreSQL database:
   ```bash
   createdb ai_model_eval
   ```

5. Create a `.env` file for development:
   ```ini
   DB_USER=your_username
   DB_PASSWORD=your_password
   DB_HOST=127.0.0.1
   DB_PORT=5432
   DB_NAME=ai_model_eval
   SECRET_KEY=development_secret_key
   DEBUG=true
   ```

## Project Structure

The project follows a modular architecture:

- `backend/` - FastAPI backend
  - `db/` - Database models and connection logic
  - `main.py` - API entry point
  - `auth.py` - Authentication services
  - `exporters.py` - Data export functionality
  - `search.py` - Search and filtering functionality
  - `visualization.py` - Data visualization utilities
  - `batch.py` - Batch processing functionality
- `frontend/` - React.js frontend (if applicable)

## Development Workflow

### Running the Development Server

```bash
cd backend
uvicorn main:app --reload --port 8000
```

### Creating Database Migrations

We use Alembic for database migrations:

```bash
# Generate a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head
```

### Testing

Run the test suite:

```bash
cd backend
pytest
```

Generate test coverage report:

```bash
pytest --cov=. --cov-report=html
```

## Coding Standards

### Python Code Style

- Follow PEP 8 guidelines
- Use type hints
- Document functions and classes with docstrings
- Maximum line length: 88 characters

### Commit Guidelines

- Use descriptive commit messages
- Reference issue numbers when applicable
- Keep commits focused on a single task

## Pull Request Process

1. Create a new branch for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and commit them with clear messages

3. Push your branch to the repository:
   ```bash
   git push origin feature/your-feature-name
   ```

4. Create a pull request against the `dev` branch
   - Include a description of changes
   - Reference any related issues
   - Ensure tests pass

5. Address any feedback from code reviews

## Documentation

When adding new features, be sure to:

- Update API documentation
- Add code comments
- Update README.md if necessary
- Document configuration options

## Performance Considerations

- Use database indexes for frequently queried fields
- Consider pagination for large dataset queries
- Use async handlers for I/O-bound operations
- Profile code using tools like cProfile or py-spy

## Security Best Practices

- Never commit sensitive credentials
- Use environment variables for configuration
- Validate all user inputs
- Follow OAuth2 best practices for authentication
- Apply proper rate limiting

## Release Process

1. Merge changes to the `dev` branch
2. Run full test suite
3. Update version numbers
4. Create a release candidate branch
5. Perform final testing
6. Merge to `main`
7. Tag the release with version number
8. Update documentation 