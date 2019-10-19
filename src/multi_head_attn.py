#/usr/bin/env python
import torch
import torch.nn as nn
import torch.nn.functional as F

import math

class MultiHeadAttn(nn.Module):
    def __init__(self, d_model, num_heads=8):
        super(MultiHeadAttn, self).__init__()
        self.num_heads = num_heads
        d_k = d_v = d_model // self.num_heads
        self.query_project = nn.Linear(d_model, d_k, bias=False)
        self.key_project = nn.Linear(d_model, d_k, bias=False)
        self.value_project = nn.Linear(d_model, d_v, bias=False)
        self.out_project = nn.Linear(self.num_heads * d_v, d_model, bias=False)

    def forward(self, query, key, value, mask):
        query_mapped = self.query_project(query)
        key_mapped = self.key_project(key)
        value_mapped = self.value_project(value)
        attn_outs = []
        for _ in range(self.num_heads):
            attn_outs.append(self.attn(query_mapped, key_mapped, value_mapped, mask))
        out = torch.cat([attn_out for attn_out in attn_outs], dim=-1).to(query.device)
        return self.out_project(out)

    def attn(self, query, key, value, mask):
        d_k = key.shape[-1]
        assert d_k == query.shape[-1]
        scores = torch.bmm(query, key.permute(0, 2, 1)) / math.sqrt(d_k) #(b, Q, K)
        if mask is not None: scores = scores.masked_fill(mask == 0, -float('inf'))
        p_attn = F.softmax(scores, dim=-1)
        return torch.bmm(p_attn, value) #(b, Q, d_v)
