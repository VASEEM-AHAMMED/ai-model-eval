# Performance Testing for AI Model Evaluation Platform

This guide explains how to conduct performance testing for the AI Model Evaluation Platform, especially for testing batch dataset uploads and large dataset handling.

## Prerequisites

- Python 3.8 or higher
- The AI Model Evaluation Platform running
- Python packages: requests, numpy

## Setup

1. Activate your virtual environment:
   ```bash
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install required packages:
   ```bash
   pip install requests numpy
   ```

## Generating Test Datasets

The `gen_test_datasets.py` script generates synthetic datasets of various sizes to test the platform's performance.

### Usage

```bash
python gen_test_datasets.py --size medium --output test_datasets
```

Options:
- `--size`: Size of datasets to generate (small=100, medium=1000, large=10000, xlarge=100000)
- `--output`: Directory to save generated datasets
- `--no-zip`: Don't create a zip bundle of datasets
- `--samples`: Specify exact number of samples (alternative to --size)

The script generates three types of datasets:
1. Text classification data (JSON)
2. Model metrics data (CSV)
3. Image labels data (JSON)

It also creates a ZIP file containing all three datasets for testing the ZIP upload functionality.

## Testing Batch Uploads

The `test_batch_upload.py` script tests various dataset upload methods supported by the platform.

### Usage

```bash
python test_batch_upload.py --api-url http://localhost:8000 --test-type all
```

Options:
- `--api-url`: URL of the API server
- `--datasets-dir`: Directory containing test datasets
- `--username` and `--password`: Credentials for authentication
- `--test-type`: Type of test to run:
  - `single`: Test single file upload
  - `batch`: Test batch upload of multiple files
  - `zip`: Test ZIP file upload
  - `metrics`: Test dataset upload with metrics
  - `all`: Run all tests

## Performance Metrics

The script will report:
- Upload success/failure
- Upload duration
- Number of datasets/metrics processed
- Response data from the server

## Best Practices

1. **Start with small datasets**: Begin testing with small datasets and gradually increase size to identify bottlenecks.

2. **Monitor server resources**: During testing, monitor CPU, memory, and disk usage on the server.

3. **Test with authentication**: Always test with authentication enabled to get realistic performance metrics.

4. **Test concurrent uploads**: For production testing, consider running multiple instances of the test script simultaneously.

## Troubleshooting

If you encounter issues:

1. Check that the server is running and accessible
2. Verify that authentication credentials are correct
3. Check that datasets directory exists and contains the expected files
4. Examine server logs for any errors during upload

## Example Workflow

```bash
# Generate medium-sized test datasets
python gen_test_datasets.py --size medium

# Run all upload tests
python test_batch_upload.py --api-url http://localhost:8000 --test-type all

# Test only ZIP uploads with large datasets
python gen_test_datasets.py --size large
python test_batch_upload.py --api-url http://localhost:8000 --test-type zip
``` 