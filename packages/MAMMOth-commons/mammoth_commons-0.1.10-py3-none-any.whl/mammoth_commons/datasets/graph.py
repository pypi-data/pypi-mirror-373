from mammoth_commons.datasets.dataset import Dataset


class Graph(Dataset):
    def __init__(self, graph, communities: dict):
        super().__init__(None)
        import pygrank as pg

        self.graph = graph
        self.communities = {
            str(k): pg.to_signal(graph, v) for k, v in communities.items()
        }
        self.labels = None
        self.categorical = set(self.communities.keys())

    def to_numpy(self, sensitive: list[str] | None = None):
        return [self.communities[attr] for attr in sensitive]

    @property
    def df(self):
        return {k: v.np for k, v in self.communities.items()}

    def to_csv(self, sensitive: list[str]):
        return self
