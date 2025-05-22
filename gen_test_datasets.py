#!/usr/bin/env python3
"""
Test Dataset Generator for AI Model Evaluation Platform.
Creates test datasets of various sizes to simulate production usage.
"""

import os
import json
import csv
import random
import argparse
import zipfile
from pathlib import Path
import numpy as np
from datetime import datetime, timedelta

def generate_text_classification_dataset(num_samples=1000, output_file="text_classification_dataset.json"):
    """Generate a text classification dataset in JSON format"""
    
    # Sample categories and texts
    categories = ["sports", "politics", "technology", "entertainment", "business"]
    sample_texts = [
        "Latest news about the upcoming election results",
        "The new smartphone features advanced AI capabilities",
        "The team won their match with a last-minute goal",
        "Stock market trends show a positive outlook for tech companies",
        "Award-winning movie receives critical acclaim at film festival",
        "Updates on the latest software release and features",
        "Analysis of economic policies and their impact",
        "Sports tournament highlights and player statistics",
        "Celebrity interview reveals upcoming project details",
        "Product launch introduces innovative technology solutions"
    ]
    
    # Generate dataset
    dataset = []
    for i in range(num_samples):
        text = random.choice(sample_texts) + f" (Example {i+1})"
        label = random.choice(categories)
        confidence = round(random.uniform(0.6, 0.99), 2)
        
        dataset.append({
            "id": i+1,
            "text": text,
            "label": label,
            "confidence": confidence,
            "metadata": {
                "source": "generated",
                "timestamp": (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat()
            }
        })
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
    
    # Save dataset to file
    with open(output_file, 'w') as f:
        json.dump({"samples": dataset, "dataset_info": {"name": "Text Classification Test Data", "version": "1.0"}}, f, indent=2)
    
    print(f"Generated text classification dataset with {num_samples} samples: {output_file}")
    return output_file

def generate_metrics_dataset(num_models=5, num_epochs=10, output_file="model_metrics_dataset.csv"):
    """Generate a metrics dataset in CSV format"""
    
    # Generate column headers
    headers = ["model_name", "epoch", "accuracy", "precision", "recall", "f1_score", "loss", "timestamp"]
    
    # Generate data rows
    rows = []
    model_names = [f"model_{i+1}" for i in range(num_models)]
    
    for model in model_names:
        # Initialize metrics with random starting values
        accuracy = random.uniform(0.70, 0.80)
        precision = random.uniform(0.65, 0.75)
        recall = random.uniform(0.60, 0.70)
        f1 = random.uniform(0.65, 0.75)
        loss = random.uniform(0.5, 0.7)
        
        for epoch in range(1, num_epochs + 1):
            # Simulate gradual improvement
            improvement = min(epoch * 0.01, 0.1)
            
            # Add some randomness
            accuracy_noise = random.uniform(-0.01, 0.02)
            precision_noise = random.uniform(-0.01, 0.02)
            recall_noise = random.uniform(-0.01, 0.02)
            f1_noise = random.uniform(-0.01, 0.02)
            loss_noise = random.uniform(-0.02, 0.01)
            
            # Calculate values for this epoch
            epoch_accuracy = min(accuracy + improvement + accuracy_noise, 0.99)
            epoch_precision = min(precision + improvement + precision_noise, 0.99)
            epoch_recall = min(recall + improvement + recall_noise, 0.99)
            epoch_f1 = min(f1 + improvement + f1_noise, 0.99)
            epoch_loss = max(loss - improvement + loss_noise, 0.1)
            
            # Generate timestamp
            timestamp = (datetime.now() - timedelta(days=num_epochs - epoch)).isoformat()
            
            # Add row
            rows.append([
                model, 
                epoch, 
                round(epoch_accuracy, 4),
                round(epoch_precision, 4),
                round(epoch_recall, 4),
                round(epoch_f1, 4),
                round(epoch_loss, 4),
                timestamp
            ])
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
    
    # Save dataset to file
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
    
    print(f"Generated metrics dataset with {num_models} models and {num_epochs} epochs: {output_file}")
    return output_file

def generate_image_labels(num_samples=1000, output_file="image_labels.json"):
    """Generate image classification labels in JSON format"""
    
    # Sample categories
    categories = ["cat", "dog", "car", "tree", "building", "person", "flower", "bird", "mountain", "water"]
    
    # Generate dataset
    dataset = []
    for i in range(1, num_samples + 1):
        # Create a realistic filename
        filename = f"img_{i:06d}.jpg"
        
        # Assign random labels with confidence scores
        primary_label = random.choice(categories)
        confidence = round(random.uniform(0.75, 0.99), 3)
        
        # Create additional labels with lower confidence
        additional_labels = {}
        for _ in range(random.randint(0, 3)):
            label = random.choice([l for l in categories if l != primary_label])
            if label not in additional_labels:
                additional_labels[label] = round(random.uniform(0.1, confidence-0.1), 3)
        
        # Create entry
        entry = {
            "id": i,
            "filename": filename,
            "primary_label": primary_label,
            "confidence": confidence,
            "additional_labels": additional_labels,
            "dimension": f"{random.randint(640, 1280)}x{random.randint(480, 720)}",
            "created_at": (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat()
        }
        
        dataset.append(entry)
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
    
    # Save dataset to file
    with open(output_file, 'w') as f:
        json.dump({"images": dataset, "dataset_info": {"name": "Image Classification Test Data", "version": "1.0"}}, f, indent=2)
    
    print(f"Generated image labels dataset with {num_samples} samples: {output_file}")
    return output_file

def create_dataset_bundle(output_dir="test_datasets", num_samples=1000, compress=True):
    """Create a bundle of test datasets with various formats"""
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate datasets
    text_file = os.path.join(output_dir, "text_classification.json")
    metrics_file = os.path.join(output_dir, "model_metrics.csv")
    image_file = os.path.join(output_dir, "image_labels.json")
    
    files = [
        generate_text_classification_dataset(num_samples, text_file),
        generate_metrics_dataset(5, 10, metrics_file),
        generate_image_labels(num_samples, image_file)
    ]
    
    # Optionally create a zip bundle
    if compress:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_filename = os.path.join(output_dir, f"test_datasets_{timestamp}.zip")
        
        with zipfile.ZipFile(zip_filename, 'w') as zipf:
            for file in files:
                zipf.write(file, os.path.basename(file))
        
        print(f"Created dataset bundle: {zip_filename}")
        return zip_filename
    
    return files

def main():
    parser = argparse.ArgumentParser(description="Generate test datasets for AI Model Evaluation Platform")
    parser.add_argument("--output", "-o", default="test_datasets", help="Output directory")
    parser.add_argument("--samples", "-s", type=int, default=1000, help="Number of samples")
    parser.add_argument("--no-zip", action="store_true", help="Don't create a zip bundle")
    parser.add_argument("--size", choices=["small", "medium", "large", "xlarge"], default="medium", 
                        help="Dataset size preset (small=100, medium=1000, large=10000, xlarge=100000)")
    
    args = parser.parse_args()
    
    # Map size presets to sample counts
    size_map = {
        "small": 100,
        "medium": 1000,
        "large": 10000,
        "xlarge": 100000
    }
    
    # Use preset if provided, otherwise use the specific samples count
    num_samples = size_map[args.size] if args.size else args.samples
    
    print(f"Generating {args.size} test datasets with {num_samples} samples...")
    create_dataset_bundle(args.output, num_samples, not args.no_zip)
    print("Generation complete!")

if __name__ == "__main__":
    main() 