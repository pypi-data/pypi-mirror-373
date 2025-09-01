import torch
import torch.nn as nn
import torchvision.models as models

class AryadCNN(nn.Module):
    def __init__(self):
        super().__init__()
        resnet = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V1)
        self.cnn = nn.Sequential(*list(resnet.children())[:-2])
        # Adapter pour images 1 canal (grayscale)
        original_conv1 = self.cnn[0]
        self.cnn[0] = nn.Conv2d(1, original_conv1.out_channels,
                                kernel_size=original_conv1.kernel_size,
                                stride=original_conv1.stride,
                                padding=original_conv1.padding,
                                bias=False)
        with torch.no_grad():
            self.cnn[0].weight.copy_(original_conv1.weight.sum(dim=1, keepdim=True))

    def forward(self, x):
        features = self.cnn(x)  # (B, C, H', W')
        B, C, H, W = features.shape
        features = features.permute(0, 3, 1, 2)  # (B, W', C, H')
        features = features.contiguous().view(B, W, -1)  # (B, W', C*H')
        return features  # (batch_size, seq_len, feature_dim)