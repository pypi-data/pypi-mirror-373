import os
import torch.nn as nn
import torch
import torchvision.transforms as transforms
import onnxruntime as ort
import tempfile


class TransformWrapper(nn.Module):
    def __init__(self, transform):
        super(TransformWrapper, self).__init__()
        self.transform = transform
        self.input_size = self._get_input_size()
        self.transforms_dict = {}

        for t in self.transform.transforms:
            transform_name = t.__class__.__name__.lower()
            self.transforms_dict[transform_name] = t

    def _get_input_size(self):
        for t in self.transform.transforms:
            if isinstance(t, transforms.Resize):
                return t.size
        return (224, 224)

    def forward(self, x):
        # Apply each transform in sequence
        for name, transform in self.transforms_dict.items():
            if name != "totensor":
                x = transform(x)
        return x


def torch2onnx(transforms):
    transform_model = TransformWrapper(transforms)
    transform_model.eval()
    dummy_input = torch.randn(1, 3, 891, 891)

    with tempfile.NamedTemporaryFile(suffix=".onnx", delete=False) as temp_file:
        onnx_model_path = temp_file.name
        torch.onnx.export(
            transform_model,
            dummy_input,
            onnx_model_path,
            do_constant_folding=True,
            input_names=["input"],
            output_names=["output"],
            dynamic_axes={
                "input": {0: "batch_size", 2: "height", 3: "width"},
                "output": {0: "batch_size"},
            },
        )

    onnx_transforms = ort.InferenceSession(onnx_model_path)
    os.remove(onnx_model_path)
    return onnx_transforms
