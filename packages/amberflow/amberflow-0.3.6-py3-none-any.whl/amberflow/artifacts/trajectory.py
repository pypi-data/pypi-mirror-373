from amberflow.artifacts import BaseArtifactFile, fileartifact
from amberflow.primitives import filepath_t

__all__ = (
    "BaseTrajectory",
    "BaseTrajectoryFile",
    "BaseTargetTrajectoryFile",
    "BaseBinderTrajectoryFile",
    "BaseComplexTrajectoryFile",
    "NucleicTargetTrajectoryNC",
)


class BaseTrajectory(BaseArtifactFile):
    pass


class BaseTrajectoryFile(BaseTrajectory):
    pass


class BaseTargetTrajectoryFile(BaseTrajectoryFile):
    pass


class BaseBinderTrajectoryFile(BaseTrajectoryFile):
    pass


class BaseComplexTrajectoryFile(BaseTrajectoryFile):
    pass


@fileartifact
class ProteinTargetTrajectoryNC(BaseTargetTrajectoryFile):
    prefix: str = "target"
    suffix: str = ".nc"
    tags: tuple[str] = ("protein",)

    def __init__(
        self,
        filepath: filepath_t,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(filepath, prefix=self.prefix, suffix=self.suffix, *args, **kwargs)


@fileartifact
class NucleicTargetTrajectoryNC(BaseTargetTrajectoryFile):
    prefix: str = "target"
    suffix: str = ".nc"
    tags: tuple[str] = ("nucleic",)

    def __init__(
        self,
        filepath: filepath_t,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(filepath, prefix=self.prefix, suffix=self.suffix, *args, **kwargs)


@fileartifact
class BinderLigandTrajectoryNC(BaseBinderTrajectoryFile):
    prefix: str = "binder"
    suffix: str = ".nc"
    tags: tuple[str] = ("ligand",)

    def __init__(
        self,
        filepath: filepath_t,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(filepath, prefix=self.prefix, suffix=self.suffix, *args, **kwargs)


@fileartifact
class ComplexProteinLigandTrajectoryNC(BaseComplexTrajectoryFile):
    prefix: str = "complex"
    suffix: str = ".nc"
    tags: tuple[str] = (
        "protein",
        "ligand",
    )

    def __init__(
        self,
        filepath: filepath_t,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(filepath, prefix=self.prefix, suffix=self.suffix, *args, **kwargs)
