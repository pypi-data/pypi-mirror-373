def get_device() -> str:
    try:
        import torch
    except ImportError:
        return "cpu"

    if torch.cuda.is_available():
        device = f"cuda:{torch.cuda.current_device()}"
    elif torch.backends.mps.is_available():
        device = "mps"
    else:
        device = "cpu"
    return device
