from tqdm import tqdm
import torch
import torch.nn.functional as F
from .device import get_autocast, get_grad_scaler

def train_epoch(model, optimizer, loader, loss_fn, device, grad_clip=None, metric_fn=None, scaler=None, use_amp=False):
    model.train()
    total_loss, metric_sum, total = 0.0, 0, 0

    for data, target in tqdm(loader, desc="Training", leave=False):
        data, target = move_to_device(data, device), move_to_device(target, device)

        with get_autocast(use_amp, device.type):
            predictions = model(data)
            loss = loss_fn(predictions, target)

        if scaler is not None:
            scaler.scale(loss).backward()
            if grad_clip is not None:
                scaler.unscale_(optimizer)
                torch.nn.utils.clip_grad_norm_(model.parameters(), grad_clip)
            scaler.step(optimizer)
            scaler.update()
        else:
            loss.backward()
            if grad_clip is not None:
                torch.nn.utils.clip_grad_norm_(model.parameters(), grad_clip)
            optimizer.step()

        optimizer.zero_grad()
        total_loss += loss.item() * target.size(0)
        if metric_fn is not None:
            metric_sum += metric_fn(predictions, target) * target.size(0)
        total += target.size(0)

    avg_loss = total_loss / total
    avg_metric = metric_sum / total if metric_fn is not None else None
    return avg_loss, avg_metric

def train(model, optimizer, n_epochs, train_loader, val_loader, device,
          loss_fn=F.cross_entropy, scheduler=None, grad_clip=None, checkpoint_path="best_model.pt",
          resume=False, metric="val_loss", save_last=True, metric_fn=None, use_amp=False,
          save_every=None, improvement_fn=None, early_stopping_patience=None, warmup_scheduler=None):
    scaler = get_grad_scaler(use_amp)

    if improvement_fn is None:
        if metric_fn is None or metric == "val_loss":
            improvement_fn = lambda current, best: current < best
            best_score = float("inf")
        else:
            improvement_fn = lambda current, best: current > best
            best_score = 0.0

    if resume and os.path.exists(checkpoint_path):
        start_epoch, best_score = load_checkpoint(model, optimizer, scheduler, checkpoint_path, device)
    else:
        start_epoch, best_score = 1, (float("inf") if metric == "val_loss" else 0.0)

    train_loss_log, train_metric_log, val_loss_log, val_metric_log = [], [], [], []

    patience_counter = 0

    for epoch in range(start_epoch, start_epoch + n_epochs):
        print(f"\nEpoch {epoch}/{n_epochs}")

        train_loss, train_metric = train_epoch(model, optimizer, train_loader, loss_fn, device, grad_clip, metric_fn, scaler, use_amp)
        val_loss, val_metric = evaluate(model, val_loader, loss_fn, device, metric_fn)

        train_loss_log.append(train_loss)
        train_metric_log.append(train_metric)
        val_loss_log.append(val_loss)
        val_metric_log.append(val_metric)

        print(f" train loss: {train_loss:.4f}, train acc: {train_metric:.4f}")
        print(f" val loss: {val_loss:.4f}, val acc: {val_metric:.4f}")

        if warmup_scheduler is not None:
            warmup_scheduler.step()

        if scheduler is not None:
            scheduler.step()

        current_score = val_loss if (metric_fn is None or metric == "val_loss") else val_metric

        if improvement_fn(current_score, best_score):
            patience_counter = 0
            best_score = current_score
            save_checkpoint(model, optimizer, scheduler, epoch, best_score, checkpoint_path)
            print(f"Saved new best model ({metric}={best_score:.4f})")
        else:
            patience_counter += 1
            if save_last:
                save_checkpoint(model, optimizer, scheduler, epoch, best_score, "last_model.pt")

        if save_every is not None and epoch % save_every == 0:
            save_checkpoint(model, optimizer, scheduler, epoch, best_score, f"checkpoint_epoch_{epoch}.pt")

        if early_stopping_patience is not None and patience_counter >= early_stopping_patience:
            print("Early stopping triggered!")
            break

    return train_loss_log, train_metric_log, val_loss_log, val_metric_log

def evaluate(model, loader, loss_fn, device, metric_fn=None):
    model.eval()
    total_loss, metric_sum, total = 0.0, 0, 0

    with torch.no_grad():
        for data, target in loader:
            data, target = move_to_device(data, device), move_to_device(target, device)
            predictions = model(data)
            loss = loss_fn(predictions, target)
            total_loss += loss.item() * target.size(0)

            if metric_fn is not None:
                metric_sum += metric_fn(predictions, target) * target.size(0)

            total += target.size(0)

    avg_loss = total_loss / total
    avg_metric = metric_sum / total if metric_fn is not None else None
    return avg_loss, avg_metric