from amberflow.artifacts import BaseArtifactFile, fileartifact
from amberflow.primitives import filepath_t


@fileartifact
class TarZstd(BaseArtifactFile):
    prefix: str = ""
    suffix: str = ".zst"
    tags: tuple = tuple()

    def __init__(self, filepath: filepath_t, *args, **kwargs) -> None:
        super().__init__(filepath, *args, prefix=self.prefix, suffix=self.suffix, **kwargs)
