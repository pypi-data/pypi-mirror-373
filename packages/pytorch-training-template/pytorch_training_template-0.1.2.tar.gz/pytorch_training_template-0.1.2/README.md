# PyTorch Training Template

A flexible and modular PyTorch training template for deep learning tasks, designed to streamline model training, evaluation, and visualization. This template supports mixed precision training, checkpointing, early stopping, and customizable metrics, making it suitable for a variety of machine learning projects.

## Features

* Modular Data Handling: Move data (tensors, lists, or dictionaries) to GPU/CPU with a single move_to_device function.
* Checkpointing: Save and load model, optimizer, and scheduler states for resuming training.
* Mixed Precision Training: Support for Automatic Mixed Precision (AMP) to optimize training on GPUs.
* Flexible Training Loop: Customizable loss functions, metrics, and improvement criteria.
* Early Stopping: Stop training if the model stops improving after a specified number of epochs.
* Visualization: Plot training and validation loss/metric curves using Matplotlib.
* Example Included: A simple Convolutional Neural Network (CNN) trained on the MNIST dataset.

## API Reference

### Device Management
- **`move_to_device(batch, device)`**  
  Move data to the specified device (CPU/GPU).

- **`get_autocast(use_amp, device)`**  
  Returns a context manager for mixed precision training.

- **`get_grad_scaler(use_amp)`**  
  Returns a gradient scaler for mixed precision training.

---

### Checkpointing
- **`save_checkpoint(model, optimizer, scheduler, epoch, best_score, path)`**  
  Save a model checkpoint.

- **`load_checkpoint(model, optimizer, scheduler, path, device)`**  
  Load a model checkpoint.

---

### Training
- **`train(model, optimizer, n_epochs, train_loader, val_loader, ...)`**  
  Train the model with customizable options.

- **`train_epoch(model, optimizer, loader, loss_fn, device, ...)`**  
  Train the model for one epoch.

- **`evaluate(model, loader, loss_fn, device, metric_fn)`**  
  Evaluate the model on a dataset.

---

### Metrics (basic ones)
- **`accuracy(predictions, target)`**  
  Compute classification accuracy.

- **`binary_accuracy(predictions, target)`**  
  Compute binary classification accuracy.

- **`mse(predictions, target)`**  
  Compute mean squared error.

---

### Visualization
- **`plot_reses(train_loss, train_metric, val_loss, val_metric, metric_name)`**  
  Plot training and validation curves.
