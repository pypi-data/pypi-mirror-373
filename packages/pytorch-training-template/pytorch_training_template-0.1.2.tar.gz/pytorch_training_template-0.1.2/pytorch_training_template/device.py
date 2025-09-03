from contextlib import nullcontext
import torch

def move_to_device(batch, device):
    if isinstance(batch, (list, tuple)):
        return [move_to_device(x, device) for x in batch]
    elif isinstance(batch, dict):
        return {k: move_to_device(v, device) for k, v in batch.items()}
    return batch.to(device)

def get_grad_scaler(use_amp):
    if not use_amp:
        return None
    try:
        return torch.amp.GradScaler(device_type="cuda")
    except TypeError:
        return torch.cuda.amp.GradScaler()

def get_autocast(use_amp, device):
    if not use_amp:
        return nullcontext()
    try:
        return torch.amp.autocast(device_type=device)
    except TypeError:
        return torch.cuda.amp.autocast()