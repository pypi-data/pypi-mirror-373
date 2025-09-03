from mammoth_commons.datasets.dataset import Dataset


class Text(Dataset):
    def __init__(self, text: str):
        self.text = text
