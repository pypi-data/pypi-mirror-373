# Default configurations
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
DEFAULT_ADAPTER = "linear"
