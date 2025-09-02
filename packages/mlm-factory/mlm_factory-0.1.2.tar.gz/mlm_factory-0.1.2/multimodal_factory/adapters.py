import torch.nn as nn

class LinearAdapter(nn.Module):
    """Linear projection from vision embedding to LLM embedding."""
    def __init__(self, in_dim, out_dim):
        super().__init__()
        self.proj = nn.Linear(in_dim, out_dim)

    def forward(self, x):
        return self.proj(x)
