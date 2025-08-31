from torch import nn
import torch
import numpy as np

def encode_label(label_str, token2id):
    tokens = label_str.split('|')
    ids = []
    for t in tokens:
        if t in token2id:
            ids.append(token2id[t])
    return ids

class DecoderCTC(nn.Module):
    def __init__(self, d_model, num_classes):
        super().__init__()
        self.linear = nn.Linear(d_model, num_classes)

    def forward(self, x):
        return self.linear(x)

def ImgPad(image):
    image = np.array(image)
    image = np.expand_dims(np.expand_dims(image,axis=0),axis=0)
    image = torch.tensor(image,dtype=torch.float32)
    image.shape
    return image