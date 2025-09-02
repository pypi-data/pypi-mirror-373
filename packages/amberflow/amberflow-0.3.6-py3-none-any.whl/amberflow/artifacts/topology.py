from logging import Logger
from pathlib import Path
from typing import Union, Optional

from amberflow.artifacts import fileartifact
from amberflow.artifacts.baseartifact import BaseArtifact
from amberflow.primitives.primitives import FileHandle, filepath_t

__all__ = (
    "BaseParameter",
    "BaseTopology",
    "BaseParameterFile",
    "BaseTopologyFile",
    "BaseParameterFile",
    "BaseTargetTopologyFile",
    "BaseBinderTopologyFile",
    "BaseComplexTopologyFile",
    "LigandLib",
    "LigandFrcmod",
    "BinderLigandTopology",
    "ComplexProteinLigandTopology",
    "Charge",
    "ChargeFile",
)


class BaseParameter(BaseArtifact):
    pass


class BaseTopology(BaseArtifact):
    pass


class BaseParameterFile(BaseParameter):
    # noinspection PyUnusedLocal
    def __init__(self, filepath: filepath_t, *args, prefix, suffix, **kwargs) -> None:
        self.filepath = Path(FileHandle(filepath))
        self.name: str = self.filepath.stem[len(prefix) :]
        super()._check_file(self.filepath, prefix, suffix)

    def __fspath__(self) -> Union[str, bytes, Path]:
        return str(self.filepath)


class BaseTopologyFile(BaseTopology):
    # noinspection PyUnusedLocal
    def __init__(self, filepath: filepath_t, *args, prefix, suffix, **kwargs) -> None:
        self.filepath = Path(FileHandle(filepath))
        self.name: str = self.filepath.stem[len(prefix) :]
        super()._check_file(self.filepath, prefix, suffix)

    def __fspath__(self) -> Union[str, bytes, Path]:
        return str(self.filepath)


class BaseTargetTopologyFile(BaseTopologyFile):
    pass


class BaseBinderTopologyFile(BaseTopologyFile):
    pass


class BaseComplexTopologyFile(BaseTopologyFile):
    pass


@fileartifact
class LigandLib(BaseParameterFile):
    prefix: str = "binder"
    suffix: str = ".lib"
    tags: tuple = tuple()

    # noinspection PyUnusedLocal
    def __init__(self, filepath: filepath_t, *, priority: int = 1, logger: Optional[Logger] = None, **kwargs) -> None:
        super().__init__(filepath, prefix=self.prefix, suffix=self.suffix, **kwargs)
        self.priority = priority


@fileartifact
class LigandFrcmod(BaseParameterFile):
    prefix: str = "binder"
    suffix: str = ".frcmod"
    tags: tuple = tuple()

    # noinspection PyUnusedLocal
    def __init__(self, filepath: filepath_t, *, priority: int = 1, logger: Optional[Logger] = None, **kwargs) -> None:
        super().__init__(filepath, prefix=self.prefix, suffix=self.suffix, **kwargs)
        self.priority = priority


@fileartifact
class BinderLigandTopology(BaseBinderTopologyFile):
    prefix: str = "binder"
    suffix: str = ".parm7"
    tags: tuple = ("ligand",)

    def __init__(
        self,
        filepath: filepath_t,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(filepath, prefix=self.prefix, suffix=self.suffix, *args, **kwargs)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(filepath={self.filepath})"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(filepath={self.filepath})"


@fileartifact
class ComplexProteinLigandTopology(BaseComplexTopologyFile):
    prefix: str = "complex"
    suffix: str = ".parm7"
    tags: tuple = ("protein", "ligand")

    def __init__(self, filepath: filepath_t, *args, **kwargs) -> None:
        super().__init__(filepath, prefix=self.prefix, suffix=self.suffix, *args, **kwargs)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(filepath={self.filepath})"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(filepath={self.filepath})"


class Charge(BaseParameter):
    """
    A class representing a charge
    """

    def __init__(self, value: Union[int, float]) -> None:
        self.value = float(value)

    def __str__(self) -> str:
        return f"Charge({self.value=})"

    def __repr__(self) -> str:
        return f"Charge(value={self.value})"

    def __float__(self) -> float:
        return self.value

    def __int__(self) -> int:
        return int(self.value)


@fileartifact
class ChargeFile(BaseParameterFile):
    prefix: str = "binder"
    suffix: str = ".charge"
    tags: tuple = ("ligand",)

    def __init__(self, filepath: filepath_t, *args, **kwargs) -> None:
        super().__init__(filepath, prefix=self.prefix, suffix=self.suffix, *args, **kwargs)
        with open(getattr(self, "filepath"), "r") as f:
            value = f.read().strip()
        self.value = float(value)

    def __str__(self) -> str:
        return f"Charge({self.value=})"

    def __repr__(self) -> str:
        return f"Charge(value={self.value})"

    def __float__(self) -> float:
        return self.value

    def __int__(self) -> int:
        return int(self.value)
