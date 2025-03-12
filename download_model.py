from transformers import AutoModelForSequenceClassification

# Download and save the pre-trained model
def download_model():
    model = AutoModelForSequenceClassification.from_pretrained("bert-base-uncased")
    model.save_pretrained("./models/bert_model")
    print("Model saved successfully!")

if __name__ == "__main__":
    download_model()
