import os
import torch
def save_model_checkpoint(step, epoch, model, optimizer, best_loss, best_acc, checkpoint_dir, name):
    if not os.path.exists(checkpoint_dir):
        os.makedirs(checkpoint_dir)
    save_path = os.path.join(checkpoint_dir, f"{name}_checkpoint_{step:04d}.pt")
    torch.save({
        "step": step,
        "epoch": epoch,
        "arch": model.__class__.__name__,  
        "state_dict": model.state_dict(),  
        "best_acc": best_acc, 
        "best_loss": best_loss,  
        "optimizer": optimizer.state_dict(), 
    }, save_path)
    return save_path

"""
if valid_loss < best_loss:
    best_loss = valid_loss
    wait = 0  # Reset wait counter
    save_path = save_model_checkpoint(
        step=step,
        epoch=epoch,
        model=model,
        optimizer=optimizer,
        best_loss=best_loss,
        best_acc=best_acc,
        checkpoint_dir=checkpoint_dir,
        name=name
    )
    print(f"Checkpoint saved at: {save_path}")
"""