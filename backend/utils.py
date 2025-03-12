import torch
from typing import List

async def load_model(model_id: str):
    model = torch.load(f"models/{model_id}.pth")
    model.eval()
    return model

async def evaluate_model(model, test_data: List[float]):
    inputs = torch.tensor(test_data)
    outputs = model(inputs)
    evaluation_result = outputs.detach().numpy().tolist()
    return evaluation_result
