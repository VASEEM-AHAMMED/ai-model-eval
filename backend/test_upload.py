import requests
import json
import os

# Create uploads directory if it doesn't exist
os.makedirs("temp", exist_ok=True)

# First, create a sample JSON file
sample_data = {
    "dataset_name": "Test Dataset",
    "metrics": {
        "accuracy": 0.92,
        "precision": 0.89,
        "recall": 0.94,
        "f1_score": 0.91,
        "latency": [120, 115, 125, 118, 122],
        "timestamps": [
            "2023-12-01T10:00:00", 
            "2023-12-01T10:05:00", 
            "2023-12-01T10:10:00",
            "2023-12-01T10:15:00",
            "2023-12-01T10:20:00"
        ],
        "distribution": {
            "categories": ["Class A", "Class B", "Class C"],
            "counts": [45, 32, 28]
        }
    }
}

# Write to a temporary file
with open("temp/test_data.json", "w") as f:
    json.dump(sample_data, f, indent=2)

print("Created test data file")

# API endpoint
url = "http://localhost:8090/datasets/upload/"

# File and form data
files = {
    'file': ('test_data.json', open('temp/test_data.json', 'rb'), 'application/json')
}
data = {
    'name': 'Test Dataset',
    'description': 'This is a test dataset for API testing',
    'format': 'json'
}

# Send POST request
print("Uploading dataset...")
response = requests.post(url, files=files, data=data)

# Check response
if response.status_code == 200:
    dataset = response.json()
    print("✅ Dataset uploaded successfully!")
    print(f"Dataset ID: {dataset['id']}")
    print(f"Dataset name: {dataset['name']}")
    print(f"File path: {dataset['file_path']}")
    
    # Now let's create metrics for this dataset
    metrics_url = f"http://localhost:8090/datasets/{dataset['id']}/metrics/"
    metrics_data = {
        "dataset_id": dataset['id'],
        "model_name": "Test Model",
        "accuracy": 0.95,
        "precision": 0.92,
        "recall": 0.91,
        "f1_score": 0.93,
        "latency": [120, 115, 125],
        "timestamps": ["2023-12-01T10:00:00", "2023-12-01T10:05:00", "2023-12-01T10:10:00"],
        "distribution": {"categories": ["Class A", "Class B"], "counts": [45, 32]}
    }
    
    print("\nCreating metrics...")
    metrics_response = requests.post(metrics_url, json=metrics_data)
    
    if metrics_response.status_code == 200:
        metrics = metrics_response.json()
        print("✅ Metrics created successfully!")
        print(f"Metrics ID: {metrics['id']}")
        print(f"Accuracy: {metrics['accuracy']}")
        
        # Now let's retrieve the metrics
        get_metrics_url = f"http://localhost:8090/datasets/{dataset['id']}/metrics/"
        get_response = requests.get(get_metrics_url)
        
        if get_response.status_code == 200:
            retrieved_metrics = get_response.json()
            print("\n✅ Retrieved metrics:")
            print(json.dumps(retrieved_metrics, indent=2))
        else:
            print(f"❌ Failed to retrieve metrics: {get_response.status_code}")
            print(get_response.text)
    else:
        print(f"❌ Failed to create metrics: {metrics_response.status_code}")
        print(metrics_response.text)
else:
    print(f"❌ Failed to upload dataset: {response.status_code}")
    print(response.text) 