import torch
import torch.nn.functional as F

def accuracy(predictions, target):
    return (predictions.argmax(dim=1) == target).float().mean().item()

def binary_accuracy(predictions, target):
    preds = (torch.sigmoid(predictions) > 0.5).long()
    return (preds == target).float().mean().item()

def mse(predictions, target):
    return F.mse_loss(predictions, target).item()