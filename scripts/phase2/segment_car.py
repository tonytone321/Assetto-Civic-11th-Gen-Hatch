#!/usr/bin/env python3
"""Car silhouette masks for the Phase 2 photo comparison.

Uses torchvision's COCO-trained Mask R-CNN (maskrcnn_resnet50_fpn_v2, weights
MaskRCNN_ResNet50_FPN_V2_Weights.COCO_V1) and keeps the largest 'car' instance (COCO class 3).
For an RGBA studio render the alpha channel is used instead. Masks go to cache/phase2/masks/
(git-ignored, because they are derived from third-party images).

segment(path) -> dict(mask=np.uint8 HxW 0/255, method=str, score=float|None)
"""
import os

import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_MODEL = None
MODEL_NAME = "torchvision maskrcnn_resnet50_fpn_v2 / MaskRCNN_ResNet50_FPN_V2_Weights.COCO_V1"
COCO_CAR = 3


def _model():
    global _MODEL
    if _MODEL is None:
        import torch
        from torchvision.models.detection import maskrcnn_resnet50_fpn_v2, MaskRCNN_ResNet50_FPN_V2_Weights
        torch.set_num_threads(max(1, os.cpu_count() or 1))
        _MODEL = maskrcnn_resnet50_fpn_v2(weights=MaskRCNN_ResNet50_FPN_V2_Weights.COCO_V1).eval()
    return _MODEL


def segment(path, max_side=1600):
    im = Image.open(path)
    if im.mode == "RGBA":
        a = np.array(im)[:, :, 3]
        if (a < 128).mean() > 0.2:
            return {"mask": np.where(a >= 128, 255, 0).astype(np.uint8), "method": "alpha channel (studio render)",
                    "score": None, "scale": 1.0}
    import torch
    rgb = im.convert("RGB")
    s = min(1.0, max_side / max(rgb.size))
    small = rgb.resize((round(rgb.size[0] * s), round(rgb.size[1] * s)), Image.BILINEAR) if s < 1 else rgb
    t = torch.from_numpy(np.array(small)).permute(2, 0, 1).float() / 255.0
    with torch.no_grad():
        out = _model()([t])[0]
    best, best_area = None, 0
    for lab, sc, m in zip(out["labels"], out["scores"], out["masks"]):
        if int(lab) != COCO_CAR or float(sc) < 0.5:
            continue
        mm = (m[0].numpy() >= 0.5)
        if mm.sum() > best_area:
            best, best_area = (float(sc), mm), mm.sum()
    if best is None:
        return {"mask": None, "method": MODEL_NAME, "score": None, "scale": s}
    mask = Image.fromarray((best[1] * 255).astype(np.uint8)).resize(rgb.size, Image.BILINEAR)
    mask = np.where(np.array(mask) >= 128, 255, 0).astype(np.uint8)
    return {"mask": mask, "method": MODEL_NAME + " (largest 'car' instance, score >= 0.5)", "score": best[0], "scale": s}


if __name__ == "__main__":
    import sys
    os.makedirs(os.path.join(ROOT, "cache", "phase2", "masks"), exist_ok=True)
    for p in sys.argv[1:]:
        r = segment(p)
        name = os.path.splitext(os.path.basename(p))[0][:60]
        if r["mask"] is not None:
            Image.fromarray(r["mask"]).save(os.path.join(ROOT, "cache", "phase2", "masks", name + ".png"))
        print(name, r["method"], r["score"], None if r["mask"] is None else int((r["mask"] > 0).sum()))
