import torch
from math import sqrt, inf


class EncoderDecoderAttention(torch.nn.Module):
    """
    The encoder decoder attention block of a transformer architecture.

    Attributes:
        w_queries (Parameter): Query weights
        w_keys (Parameter): Key weights
        w_values (Parameter): Value weights
        w_agg (Parameter): Aggregation weights
    """
    def __init__(self, token_dim: int, embedding_size: int, num_heads: int, device: str = "cpu"):
        super().__init__()
        self.num_heads = num_heads
        self.w_queries = [
            torch.nn.Parameter(torch.rand(1,token_dim, embedding_size)).to(device)
            for i in range(self.num_heads)
        ]
        self.w_keys = [
            torch.nn.Parameter(torch.rand(1,token_dim, embedding_size)).to(device)
            for i in range(self.num_heads)
        ]
        self.w_values = [
            torch.nn.Parameter(torch.rand(1,token_dim, embedding_size)).to(device)
            for i in range(self.num_heads)
        ]
        self.w_agg = torch.nn.Parameter(torch.rand(embedding_size*self.num_heads, token_dim)).to(device)
        self.embedding_size = embedding_size
        self.token_dim = token_dim
        self.device = device
            
    def forward(self, x, encoder_context, attention_mask, current_index):
        attention_heads = []
        for i in range(self.num_heads):
            mask = torch.zeros(x.shape[0], x.shape[1], x.shape[1], dtype=torch.float).to(self.device)
            for j in range(x.shape[0]):
                min_col = min(current_index+1, x.shape[1]-1)
                mask[j, min_col:,:] = -inf
            # b, s, token_dim -> b, s, embedding_size
            Q = x @ self.w_queries[i] 
            K = encoder_context @ self.w_keys[i] 
            V = encoder_context @ self.w_values[i]
            relations = Q @ K.transpose(2,1) + mask
            attention_heads.append(
                torch.softmax(
                    relations / sqrt(self.embedding_size), 
                    dim=1
                ) @ V)
        multiple_heads = torch.cat(attention_heads, dim=-1)
        return multiple_heads @ self.w_agg