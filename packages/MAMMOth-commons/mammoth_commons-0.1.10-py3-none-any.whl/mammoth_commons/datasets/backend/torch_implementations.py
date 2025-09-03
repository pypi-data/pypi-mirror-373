from PIL import Image as PILImage
from torch.utils.data import Dataset
import torchvision.transforms as transforms
from typing import List
import os
from mammoth_commons.integration_callback import notify_progress


class PytorchImageDataset(Dataset):
    def __init__(
        self,
        csv_path: str,
        root_dir: str,
        target: str,
        sensitive: List[str],
        data_transform: transforms.Compose,
    ):
        """
        PyTorch dataset for image data.

        Args:
            csv_path (str): The path to the CSV file containing information about the dataset.
            root_dir (str): The root directory where the actual image files are stored.
            target (str): The name of the column in the CSV file containing the target variable.
            sensitive (List[str]): A list of strings representing columns in the CSV file containing sensitive information.
            transforms (transforms.Compose): A composition of image transformations.
        """
        from mammoth_commons.externals import pd_read_csv

        self.data = pd_read_csv(csv_path)
        self.root_dir = root_dir
        self.target = target
        self.sensitive = sensitive
        self.data_transform = data_transform

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        img_name = self.data.iloc[idx, 0]
        img_path = os.path.join(self.root_dir, img_name)

        target = self.data.iloc[idx][self.target]
        protected = [self.data.iloc[idx][attr] for attr in self.sensitive]
        if self.data_transform is not None:
            image = self.data_transform(img_path)
        else:
            image = PILImage.open(img_path).convert("RGB")
        notify_progress(
            (idx + 1) / len(self), f"Processing image {int(idx)+1}/{len(self)}"
        )
        return image, target, protected


class PytorchImagePairsDataset(Dataset):
    def __init__(
        self,
        csv_path: str,
        root_dir: str,
        target: str,
        sensitive: List[str],
        data_transform: transforms.Compose,
    ):
        """
        PyTorch dataset for image data.

        Args:
            csv_path (str): The path to the CSV file containing information about the dataset.
            root_dir (str): The root directory where the actual image files are stored.
            target (str): The name of the column in the CSV file containing the target variable.
            sensitive (List[str]): A list of strings representing columns in the CSV file containing sensitive information.
            transforms (transforms.Compose): A composition of image transformations.
        """
        from mammoth_commons.externals import pd_read_csv

        self.data = pd_read_csv(csv_path)
        self.root_dir = root_dir
        self.target = target
        self.sensitive = sensitive
        self.data_transform = data_transform

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        img1_name = self.data.iloc[idx, 0]  # ref
        img2_name = self.data.iloc[idx, 1]  # motion

        id1_image_path = os.path.join(self.root_dir, str(img1_name))
        id2_image_path = os.path.join(self.root_dir, str(img2_name))

        target = self.data.iloc[idx][self.target]
        protected = [self.data.iloc[idx][attr] for attr in self.sensitive]
        if self.data_transform is not None:
            image1 = self.data_transform(id1_image_path)
            image2 = self.data_transform(id2_image_path)
        else:
            image1 = PILImage.open(id1_image_path).convert("RGB")
            image2 = PILImage.open(id2_image_path).convert("RGB")
        notify_progress(
            (idx + 1) / len(self), f"Processing image pair {int(idx)+1}/{len(self)}"
        )
        return image1, image2, target, protected
