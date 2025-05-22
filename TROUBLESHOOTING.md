# Troubleshooting Guide for AI Model Evaluation Platform

This guide addresses common issues that users may encounter when setting up and running the AI Model Evaluation Platform.

## Environment Issues

### Python Version Compatibility

- **Issue**: Errors with Python 3.13
- **Solution**: Use Python 3.10 or 3.11 instead. Python 3.13 has compatibility issues with some dependencies.

```bash
# Check your Python version
python --version

# Create a virtual environment with a specific Python version (if available)
python3.10 -m venv venv
```

### Module Not Found Errors

- **Issue**: "No module named 'fastapi'" or similar errors
- **Solution**: Ensure you're using the correct virtual environment and all dependencies are installed

```bash
# Activate your virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Verify installation
pip list

# Reinstall dependencies if needed
pip install -r backend/requirements.txt
```

## Database Issues

### Database Connection Errors

- **Issue**: "could not translate host name" or "connection refused" errors
- **Solution**: 
  1. Ensure PostgreSQL is running
  2. Check your `.env` file configuration
  3. Use IP address (127.0.0.1) instead of 'localhost'
  
```bash
# Check if PostgreSQL is running
pg_isready

# Create the database if needed
createdb ai_model_eval
```

### Database Initialization Errors

- **Issue**: "table already exists" or schema errors
- **Solution**: Reset the database using the provided utility

```bash
python backend/reset_db.py
```

## Server Issues

### Port Already in Use

- **Issue**: "Address already in use" error when starting the server
- **Solution**: Kill the process using the port or change the port number

```bash
# Find the process
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use a different port
uvicorn main:app --reload --port 8080
```

### Server Crashes

- **Issue**: Server unexpectedly stops or crashes
- **Solution**: Check logs for errors and verify database connection

## Authentication Issues

- **Issue**: Authentication failures or JWT errors
- **Solution**: 
  1. Ensure SECRET_KEY is properly set in the `.env` file
  2. Check that passwords meet the minimum requirements
  3. Verify user exists in the database

## Docker Issues

- **Issue**: Docker containers failing to start
- **Solution**: 
  1. Check Docker logs with `docker logs <container_id>`
  2. Ensure ports are not already in use
  3. Verify environment variables in `docker-compose.yml`

## Performance Issues

- **Issue**: Slow response times with large datasets
- **Solution**:
  1. Optimize database queries
  2. Increase server resources
  3. Use batch processing for large uploads

## Still Having Problems?

If you continue experiencing issues:

1. Check the application logs
2. Search for similar issues in the GitHub repository
3. Create a detailed bug report including:
   - Operating system
   - Python version
   - Database details
   - Stack trace or error message
   - Steps to reproduce 