import shutil
from pathlib import Path
from typing import Optional, Sequence, Union, SupportsIndex, Iterator, TypeVar

import numpy as np

from amberflow.artifacts import fileartifact, BaseArtifact, BaseArtifactFile, BaseArtifactDir, BaseMdoutMD
from amberflow.primitives import filepath_t, FileHandle, dirpath_t

__all__ = (
    "LambdaSchedule",
    "BaseStatesFile",
    "BaseRestartStatesFile",
    "BaseTrajectoryStatesFile",
    "ComplexProteinLigandRestartStates",
    "BinderLigandRestartStates",
    "ComplexNucleicLigandRestartStates",
    "ComplexProteinLigandTrajectoryStatesNC",
    "BinderLigandTrajectoryStatesNC",
    "ComplexNucleicLigandTrajectoryStates",
    "BaseMdoutStates",
    "BaseBinderMdoutStates",
    "BaseTargetMdoutStates",
    "BaseComplexMdoutStates",
    "BinderLigandMdoutStates",
    "TargetProteinMdoutStates",
    "ComplexProteinLigandMdoutStates",
    "EdgeMBARhtml",
    "EdgeMBARxml",
    "BaseDatdir",
    "TargetDatdir",
    "ReferenceDatdir",
)


class LambdaSchedule(BaseArtifact):
    """
    A class representing a schedule of lambda values for alchemical transformations.

    Lambda values are used in alchemical free energy calculations to define the
    intermediate states between two end states.
    """

    tags: tuple = ("",)

    def __init__(self, lambdas: Sequence[float], decimals: int = 5) -> None:
        """
        Initialize a LambdaSchedule with a sequence of lambda values.

        Parameters
        ----------
        lambdas : Sequence[float]
            A sequence of lambda values between 0 and 1
        decimals : int, optional
            Number of decimal places to round lambda values to, by default 5
        """
        self.lambdas = np.array(lambdas)
        self.decimals = 5
        if decimals != 0:
            self.lambdas = np.round(self.lambdas, decimals=5)
            self.decimals = decimals

    def __getitem__(self, index: Union[SupportsIndex, slice]) -> Union[float, "LambdaSchedule"]:
        if isinstance(index, slice):
            return type(self)(self.lambdas[index])
        return float(self.lambdas[index])

    def __iter__(self) -> Iterator[float]:
        for x in self.lambdas:
            yield float(x)

    def get_formatted(self, index: Union[SupportsIndex]) -> str:
        return f"{self[index]:.{self.decimals}f}"

    def formatted(self) -> Iterator[str]:
        for x in self.lambdas:
            yield f"{x:.{self.decimals}f}"

    def __contains__(self, item: float) -> bool:
        return item in self.lambdas

    def __repr__(self) -> str:
        return f"{type(self).__name__}(lambdas={self.lambdas.tolist()})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented(f"Bad comparison between {type(self)} and {type(other)}")
        return np.array_equal(self.lambdas, other.lambdas)

    def __len__(self) -> int:
        return len(self.lambdas)


T_StatesFile = TypeVar("T_StatesFile", bound="BaseStatesFile")


class BaseStatesFile(BaseArtifact):
    """
    Base class for managing collections of state files in alchemical simulations.

    This class provides functionality to handle multiple files corresponding to different
    lambda states in an alchemical transformation.
    """

    def __init__(
        self,
        filepath: filepath_t,
        *args,
        prefix,
        suffix,
        lambdas: Optional[Sequence[str] | Sequence[float]] = None,
        decimals: int = 5,
        **kwargs,
    ) -> None:
        """
        Initialize a BaseStatesFile object.

        Parameters
        ----------
        filepath : filepath_t
            Path to a representative file in the collection
        prefix : str
            Prefix for the filenames
        suffix : str
            Suffix (extension) for the filenames
        lambdas : Optional[Sequence[float]], optional
            Sequence of lambda values, by default None
        """
        self.filepath = Path(FileHandle(filepath))
        self.name: str = self.filepath.stem[len(prefix) + 1 :]
        super()._check_file(self.filepath, prefix, suffix)
        self.decimals: int = decimals
        self.states: dict[str, Path] = {}

        if lambdas is not None:
            # noinspection PyTypeChecker
            self.lambdas = self._norm_lambdas(lambdas, decimals)
            name_wo_clambda = "_".join(filepath.stem.split("_")[:-1])
            # use FileHandle to ensure the files exist
            self.states = {
                f"{clambda:.{self.decimals}f}": Path(
                    FileHandle(filepath.with_name(f"{name_wo_clambda}_{clambda:.{self.decimals}f}{suffix}"))
                )
                for clambda in self.lambdas
            }
        else:
            prefix = prefix if prefix != "" else "*"
            for state in sorted(filepath.parent.glob(f"{prefix}_*{suffix}")):
                str_lambda = state.stem.split("_")[-1]
                try:
                    float(str_lambda)
                except ValueError:
                    # If the last part of the filename is not a float, skip this file
                    continue
                self.states[str_lambda] = state
                self.decimals = len(str_lambda)
            self.lambdas = self._norm_lambdas(list(self.states.keys()), decimals)
        self.nlambdas = len(self.states)

    @staticmethod
    def _norm_lambdas(lambdas: Sequence[str] | Sequence[float], decimals: int) -> np.ndarray:
        try:
            lambdas[0]
        except IndexError:
            raise ValueError("Lambdas sequence must not be empty.")
        if all(isinstance(l, str) for l in lambdas):
            try:
                # noinspection PyTypeChecker
                lambdas = [float(l) for l in lambdas]
                return np.round(np.array(lambdas), decimals=decimals)
            except ValueError as e:
                raise ValueError("Lambdas sequence must contain only float or str convertible to float.") from e
        elif all(isinstance(l, (float, int)) for l in lambdas):
            return np.round(np.array(lambdas), decimals=decimals)
        else:
            raise ValueError("Lambdas sequence must contain only float or str convertible to float.")

    def copy_to(self: T_StatesFile, dest_dir: dirpath_t) -> T_StatesFile:
        """
        Copies all state files to a new directory and returns a new instance
        representing the copied files.


        Args:
            dest_dir: The target directory to which all files will be copied.

        Returns:
            A new instance of the same class, pointing to the copied files.
        """
        dest_path = Path(dest_dir)
        for source_file in self.states.values():
            shutil.copy2(source_file, dest_path / source_file.name)
        new_filepath = dest_path / self.filepath.name
        return self.__class__(
            filepath=new_filepath,
            lambdas=self.lambdas,
            decimals=self.decimals,
        )

    def __getitem__(self, key: float | str) -> filepath_t:
        return self.states[str(key)]

    def __iter__(self) -> Iterator[Path]:
        return iter(self.states.values())

    def __len__(self) -> int:
        return len(self.states)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(states={self.states})"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(states={self.states})"

    def values(self):
        return self.states.values()

    def keys(self):
        return self.states.keys()

    def items(self):
        return self.states.items()

    def get(self, key, default=None):
        return self.states.get(key, default)

    @staticmethod
    def get_name(filepath: Path, prefix: str) -> str:
        return filepath.stem[len(prefix) :]

    def __fspath__(self) -> Union[str, bytes, Path]:
        return str(self.filepath)


class BaseRestartStatesFile(BaseStatesFile):
    pass


class BaseTrajectoryStatesFile(BaseStatesFile):
    pass


@fileartifact
class ComplexProteinLigandRestartStates(BaseRestartStatesFile):
    prefix: str = "complex"
    suffix: str = ".rst7"
    tags: tuple = ("protein", "ligand", "alchemical")

    def __init__(
        self,
        filepath: filepath_t,
        *args,
        lambdas: Optional[Sequence[float]] = None,
        **kwargs,
    ) -> None:
        super().__init__(filepath, *args, prefix=self.prefix, suffix=self.suffix, lambdas=lambdas, **kwargs)


@fileartifact
class BinderLigandRestartStates(BaseRestartStatesFile):
    prefix: str = "binder"
    suffix: str = ".rst7"
    tags: tuple = ("ligand", "alchemical")

    def __init__(
        self,
        filepath: filepath_t,
        *args,
        lambdas: Optional[Sequence[float]] = None,
        **kwargs,
    ) -> None:
        super().__init__(filepath, *args, prefix=self.prefix, suffix=self.suffix, lambdas=lambdas, **kwargs)


@fileartifact
class ComplexNucleicLigandRestartStates(BaseRestartStatesFile):
    prefix: str = "complex"
    suffix: str = ".rst7"
    tags: tuple = ("nucleic", "ligand", "alchemical")

    def __init__(
        self,
        filepath: filepath_t,
        *args,
        lambdas: Optional[Sequence[float]] = None,
        **kwargs,
    ) -> None:
        super().__init__(filepath, *args, prefix=self.prefix, suffix=self.suffix, lambdas=lambdas, **kwargs)


@fileartifact
class BinderLigandTrajectoryStatesNC(BaseTrajectoryStatesFile):
    prefix: str = "binder"
    suffix: str = ".nc"
    tags: tuple = ("ligand", "alchemical")

    def __init__(
        self,
        filepath: filepath_t,
        *args,
        lambdas: Optional[Sequence[float]] = None,
        **kwargs,
    ) -> None:
        super().__init__(filepath, *args, prefix=self.prefix, suffix=self.suffix, lambdas=lambdas, **kwargs)


@fileartifact
class ComplexProteinLigandTrajectoryStatesNC(BaseTrajectoryStatesFile):
    prefix: str = "complex"
    suffix: str = ".nc"
    tags: tuple = ("protein", "ligand", "alchemical")

    def __init__(
        self,
        filepath: filepath_t,
        *args,
        lambdas: Optional[Sequence[float]] = None,
        **kwargs,
    ) -> None:
        super().__init__(filepath, *args, prefix=self.prefix, suffix=self.suffix, lambdas=lambdas, **kwargs)


@fileartifact
class ComplexNucleicLigandTrajectoryStates(BaseTrajectoryStatesFile):
    prefix: str = "complex"
    suffix: str = ".nc"
    tags: tuple = ("nucleic", "ligand", "alchemical")

    def __init__(
        self,
        filepath: filepath_t,
        *args,
        lambdas: Optional[Sequence[float]] = None,
        **kwargs,
    ) -> None:
        super().__init__(filepath, *args, prefix=self.prefix, suffix=self.suffix, lambdas=lambdas, **kwargs)


class BaseMdoutStates(BaseStatesFile):
    def __init__(self, filepath: filepath_t, *args, prefix: str, suffix: str, check=True, **kwargs) -> None:
        super().__init__(filepath, *args, prefix=prefix, suffix=suffix, **kwargs)
        if check:
            self.check_mdouts(self.states)

    @staticmethod
    def check_mdouts(states: dict[str, Path]) -> None:
        for mdout in states.values():
            BaseMdoutMD.check_mdout(mdout)


class BaseComplexMdoutStates(BaseMdoutStates):
    pass


class BaseTargetMdoutStates(BaseMdoutStates):
    pass


class BaseBinderMdoutStates(BaseMdoutStates):
    pass


@fileartifact
class TargetProteinMdoutStates(BaseTargetMdoutStates):
    prefix: str = "target"
    suffix: str = ".mdout"
    tags: tuple[str] = ("protein", "alchemical")

    def __init__(self, filepath: filepath_t, *args, **kwargs) -> None:
        super().__init__(filepath, *args, prefix=self.prefix, suffix=self.suffix, **kwargs)


@fileartifact
class BinderLigandMdoutStates(BaseBinderMdoutStates):
    prefix: str = "binder"
    suffix: str = ".mdout"
    tags: tuple[str] = ("ligand", "alchemical")

    def __init__(self, filepath: filepath_t, *args, **kwargs) -> None:
        super().__init__(filepath, *args, prefix=self.prefix, suffix=self.suffix, **kwargs)


@fileartifact
class ComplexProteinLigandMdoutStates(BaseComplexMdoutStates):
    prefix: str = "complex"
    suffix: str = ".mdout"
    tags: tuple[str] = ("protein", "ligand", "alchemical")

    def __init__(self, filepath: filepath_t, *args, **kwargs) -> None:
        super().__init__(filepath, *args, prefix=self.prefix, suffix=self.suffix, **kwargs)


@fileartifact
class EdgeMBARhtml(BaseArtifactFile):
    prefix: str = ""
    suffix: str = ".html"
    tags: tuple[str] = ("",)

    def __init__(self, filepath: filepath_t, *args, **kwargs) -> None:
        super().__init__(filepath, *args, prefix=self.prefix, suffix=self.suffix, **kwargs)


@fileartifact
class EdgeMBARxml(BaseArtifactFile):
    prefix: str = ""
    suffix: str = ".xml"
    tags: tuple[str] = ("",)

    def __init__(self, filepath: filepath_t, *args, **kwargs) -> None:
        super().__init__(filepath, *args, prefix=self.prefix, suffix=self.suffix, **kwargs)


T_Datdir = TypeVar("T_Datdir", bound="BaseDatdir")


class BaseDatdir(BaseArtifactDir):
    def __init__(
        self,
        filepath: filepath_t,
        *args,
        edge: str = "sysname",
        environment: str = "com",
        stage: str = "vdw",
        trial: int = 1,
        states: Optional[Sequence[float]] = None,
        makedir=False,
        **kwargs,
    ) -> None:
        self.edge = edge
        self.environment = environment
        self.stage = stage
        self.trial = f"t{trial}"
        self.states = tuple(states) if states is not None else None
        self.parent_filepath = Path(filepath)
        new_filepath = Path(filepath, self.edge, self.environment, self.stage, self.trial)
        if makedir:
            new_filepath.mkdir(parents=True, exist_ok=True)
        super().__init__(new_filepath, *args, prefix=kwargs.get("prefix"), suffix=kwargs.get("suffix"))

    @classmethod
    def from_mdout_states(
        cls: type[T_Datdir], cwd: filepath_t, *, states: BaseMdoutStates, trial: int, makedir: bool = True
    ) -> T_Datdir:
        # Format should be `"complex/binder"_{sysname}_{state}.mdout` edge is set to 'vdw'
        try:
            fp = next(iter(states.values()))
        except StopIteration:
            raise f"Empty states in {states}"
        try:
            env, sysname, _ = fp.stem.split("_")
            states: tuple[float, ...] = tuple([float(fp.stem.split("_")[2]) for fp in states.values()])
            # filepaths: tuple[Path] = tuple([fp for fp in states.values()])
        except ValueError:
            raise f"Unexpected naming format in {fp}"
        return cls(cwd, edge=sysname, environment=env, stage="vdw", trial=trial, states=states, makedir=makedir)

    def is_valid(self, nlambdas: Optional[int] = None, remlog: bool = True, mbar: bool = False) -> bool:
        """
        Check if the directory contains the expected number of lambda states and required files.

        Parameters
        ----------
        nlambdas : int
            Number of lambda states expected.
        remlog : bool, optional
            Whether to require at least one .yaml file (default: True).
        mbar : bool, optional
            Whether to use MBAR file counting logic (default: False). Set it to True only if you're sure your
            run had valid MBAR Energy values for all windows against all windows.

        Returns
        -------
        bool
            True if the directory is valid, False otherwise.
        """
        if nlambdas is None:
            if not (states := getattr(self, "states", False)):
                raise ValueError("The `states` attribute must be set before calling is_valid() without `nlambdas`.")
            nlambdas = len(states)
        # First, check that the directory actually exists
        if not self.filepath.is_dir():
            return False
        if remlog:
            try:
                next(iter(self.filepath.glob("*.yaml")))
            except StopIteration:
                return False
        # Check if the directory contains the expected number of dat files, given the number of lambdas.
        dvdl_count = len(list(self.filepath.glob("dvdl*.dat")))
        if dvdl_count < nlambdas:
            return False
        # if BAR: 3 dat files for each window, except the first and last windows which have 2 dat files each.
        efep_count = len(list(self.filepath.glob("efep*.dat")))
        efep_expected = nlambdas * nlambdas if mbar else (nlambdas - 2) * 3 + 4
        return efep_count >= efep_expected

    def get_path_template(self) -> str:
        if self.stage == "":
            return str(self.parent_filepath / r"{edge}/{env}/{trial}/efep_{traj}_{ene}.dat")
        else:
            return str(self.parent_filepath / r"{edge}/{env}/{stage}/{trial}/efep_{traj}_{ene}.dat")

    def try_load_boresch(self) -> Optional[Path]:
        raise NotImplementedError("Only TargetDatdir implements this method")


@fileartifact
class TargetDatdir(BaseDatdir):
    prefix: str = ""
    suffix: str = ""
    tags: tuple[str] = ("protein", "ligand", "alchemical")

    def __init__(
        self,
        filepath: filepath_t,
        *args,
        edge: str = "sysname",
        environment: str = "aq",
        stage: str = "vdw",
        trial: int = 1,
        states: Optional[Sequence[float]] = None,
        makedir=False,
        **kwargs,
    ) -> None:
        super().__init__(
            filepath,
            *args,
            edge=edge,
            environment=environment,
            stage=stage,
            trial=trial,
            states=states,
            makedir=makedir,
            prefix=self.prefix,
            suffix=self.suffix,
            **kwargs,
        )
        self.boresch_restraints = None
        self.try_load_boresch()

    def try_load_boresch(self) -> Optional[Path]:
        try:
            top_level_dir = getattr(self, "filepath")
            self.boresch_restraints = next(iter(top_level_dir.glob("boresch*.yaml")))
        except StopIteration:
            self.boresch_restraints = None
        return self.boresch_restraints


@fileartifact
class ReferenceDatdir(BaseDatdir):
    prefix: str = ""
    suffix: str = ""
    tags: tuple[str] = ("ligand", "alchemical")

    def __init__(
        self,
        filepath: filepath_t,
        *args,
        edge: str = "sysname",
        environment: str = "com",
        stage: str = "vdw",
        trial: int = 1,
        states: Optional[Sequence[float]] = None,
        makedir=False,
        **kwargs,
    ) -> None:
        super().__init__(
            filepath,
            *args,
            edge=edge,
            environment=environment,
            stage=stage,
            trial=trial,
            states=states,
            makedir=makedir,
            prefix=self.prefix,
            suffix=self.suffix,
            **kwargs,
        )
