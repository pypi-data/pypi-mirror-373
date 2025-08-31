import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from PIL import Image
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms

class ConvBlock(nn.Module):
    def __init__(self, in_ch, out_ch):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(in_ch, out_ch, 3, padding=1),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_ch, out_ch, 3, padding=1),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2)
        )
    def forward(self, x): return self.conv(x)

class CTClassifier(nn.Module):
    def __init__(self, n_classes=2):
        super().__init__()
        self.block1 = ConvBlock(1, 32)
        self.block2 = ConvBlock(32, 64)
        self.block3 = ConvBlock(64, 128)
        self.gap = nn.AdaptiveAvgPool2d(1)
        self.fc = nn.Linear(128, n_classes)
        self._gradcam_acts = None
        self._gradcam_grads = None
        self.block3.conv[0].register_forward_hook(self._save_acts)
        self.block3.conv[0].register_backward_hook(self._save_grads)

    def _save_acts(self, module, inp, out):
        self._gradcam_acts = out.detach()
    def _save_grads(self, module, grad_in, grad_out):
        self._gradcam_grads = grad_out[0].detach()

    def forward(self, x):
        x = self.block1(x)
        x = self.block2(x)
        x = self.block3(x)
        x = self.gap(x).flatten(1)
        logits = self.fc(x)
        return logits
    
def prepare_ct_model(model_weights):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = CTClassifier(n_classes=2).to(device)

    state = torch.load(model_weights, map_location=device)
    if isinstance(state, dict) and 'model' in state:
        model.load_state_dict(state['model'])
    else:
        model.load_state_dict(state)

    model.eval()
    return model

def display_gradcam(folder, input, model):
    model.eval()
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    img = Image.open(f"{folder}/{input}").convert("L")
    tfm = transforms.Compose([
        transforms.Resize((256,256)),
        transforms.ToTensor()
    ])
    xb = tfm(img).unsqueeze(0)
    xb = xb.to(device).requires_grad_(True)
    logits = model(xb)

    target = torch.argmax(logits, dim=1)
    sel = logits[torch.arange(xb.size(0)), target]
    model.zero_grad()
    sel.sum().backward(retain_graph=True)
    acts = model._gradcam_acts
    grads = model._gradcam_grads
    weights = grads.mean(dim=(2,3), keepdim=True)
    cam = (weights * acts).sum(dim=1, keepdim=True)
    cam = F.relu(cam)
    cams = []
    for i in range(cam.size(0)):
        c = cam[i,0]
        c = c - c.min()
        denom = (c.max() - c.min()).clamp(min=1e-6)
        c = c/denom
        cams.append(c.unsqueeze(0))
    cam = torch.stack(cams, dim=0)
    cam = F.interpolate(cam, size=xb.shape[-2:], mode='bilinear', align_corners=False)
    probs = torch.softmax(logits, dim=1)

    cam = cam.detach().cpu()
    target = target.detach().cpu()
    probs = probs.detach().cpu()

    hm = cam[0,0].cpu().numpy()
    hm = np.sqrt(hm)
    hm = hm / hm.max()

    fig, axs = plt.subplots(1,3,figsize=(12,4))
    axs[0].imshow(img, cmap='gray'); axs[0].set_title("Original"); axs[0].axis("off")
    axs[1].imshow(hm, cmap='jet'); axs[1].set_title("Grad-CAM"); axs[1].axis("off")
    axs[2].imshow(img.resize((256,256)), cmap='gray')
    axs[2].imshow(hm, cmap='jet', alpha=0.5)
    axs[2].set_title(f"P(Tumor)={probs[0,1].item():.2f}")
    axs[2].axis("off")

    plt.savefig("ct_gradcam_grid.png")
    plt.show()