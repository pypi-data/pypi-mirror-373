import os
import torch

def save_checkpoint(model, optimizer, scheduler, epoch, best_score, path="checkpoint.pt"):
    checkpoint = {
        "epoch": epoch,
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "best_score": best_score
    }
    if scheduler is not None:
        checkpoint["scheduler_state"] = scheduler.state_dict()
    torch.save(checkpoint, path)

def load_checkpoint(model, optimizer, scheduler=None, path="checkpoint.pt", device="cpu"):
    checkpoint = torch.load(path, map_location=device)
    model.load_state_dict(checkpoint["model_state"])
    optimizer.load_state_dict(checkpoint["optimizer_state"])
    best_score = checkpoint["best_score"]
    start_epoch = checkpoint["epoch"] + 1
    if scheduler is not None and "scheduler_state" in checkpoint:
        scheduler.load_state_dict(checkpoint["scheduler_state"])
    print(f"Loaded checkpoint from previous epochs: {checkpoint['epoch']}, best_score={best_score:.4f}")
    return start_epoch, best_score