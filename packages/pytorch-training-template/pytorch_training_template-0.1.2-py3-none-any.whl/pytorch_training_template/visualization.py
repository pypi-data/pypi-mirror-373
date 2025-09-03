import matplotlib.pyplot as plt
import numpy as np

def plot_reses(train_loss, train_metric, val_loss, val_metric, metric_name="Metric"):
    epochs = np.arange(1, len(train_loss) + 1)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5), dpi=100)

    ax1.plot(epochs, train_loss, label='Train Loss', color='#1f77b4', linewidth=2)
    ax1.plot(epochs, val_loss, label='Validation Loss', color='#ff7f0e', linestyle='--', linewidth=2)
    ax1.set_xlabel('Epoch')
    ax1.set_ylabel('Loss')
    ax1.set_title('Training and Validation Loss')
    ax1.grid(True, linestyle='--', alpha=0.7)
    ax1.legend()
    ax1.set_xticks(epochs)
    ax1.tick_params(axis='both', labelsize=10)

    ax2.plot(epochs, train_metric, label=f'Train {metric_name}', color='#1f77b4', linewidth=2)
    ax2.plot(epochs, val_metric, label=f'Validation {metric_name}', color='#ff7f0e', linestyle='--', linewidth=2)
    ax2.set_xlabel('Epoch')
    ax2.set_ylabel(metric_name)
    ax2.set_title(f'Training and Validation {metric_name}')
    ax2.grid(True, linestyle='--', alpha=0.7)
    ax2.legend()
    ax2.set_xticks(epochs)
    ax2.tick_params(axis='both', labelsize=10)

    plt.tight_layout()
    plt.show()