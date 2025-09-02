from logging import Logger
from pathlib import Path
from typing import Optional, Iterable, Sequence

from MDAnalysis import Universe
from rdkit import Chem
from rdkit.Chem import AllChem

from amberflow.artifacts import ArtifactContainer
from amberflow.artifacts.artifactsdecorators import fileartifact
from amberflow.artifacts.baseartifact import BaseArtifactFile, BatchArtifacts
from amberflow.primitives import (
    StructureError,
    ACCEPTED_PROTEIN_RESNAMES,
    ACCEPTED_NA_RESNAMES,
    filepath_t,
    conv_build_resnames_set,
)

__all__ = (
    "BaseStructure",
    "BaseStructureFile",
    "BaseStructureReferenceFile",
    "BaseTargetStructureFile",
    "BaseBinderStructureFile",
    "BaseComplexStructureFile",
    "BaseBinderLigandStructureFile",
    "BaseTargetStructureReferenceFile",
    "BaseBinderStructureReferenceFile",
    "BaseComplexStructureReferenceFile",
    "BaseBinderLigandStructureReferenceFile",
    "TargetProteinPDB",
    "TargetNAPDB",
    "BinderLigandPDB",
    "BinderLigandMol2",
    "BinderLigandSmiles",
    "BinderLigandRestart",
    "BaseComplexStructureFile",
    "ComplexProteinLigandPDB",
    "ComplexProteinLigandRestart",
    "ComplexNucleicLigandPDB",
    "TargetProteinRestart",
    "TargetProteinReferenceRestart",
    "BinderLigandReferenceRestart",
    "ComplexProteinLigandReferenceRestart",
    "get_biomolecule",
)


class BaseStructure(BaseArtifactFile):
    pass


class BaseStructureFile(BaseStructure):
    @staticmethod
    def _check_resnames(u: Universe, accepted_resnames: set) -> None:
        not_recognized = set(u.residues.resnames) - accepted_resnames
        if len(not_recognized) != 0:
            raise StructureError(f"Unrecognized residues in input universe: {not_recognized}")

    def _build_universe(
        self,
        struct_filepath: Optional[filepath_t] = None,
        top_filepath: Optional[Path] = None,
        check_resnames: bool = False,
        default_accepted_resnames: Optional[set] = None,
        accepted_resnames: Optional[set] = None,
    ) -> None:
        if top_filepath is None:
            self.u = Universe(str(struct_filepath))
        else:
            self.u = Universe(top_filepath, struct_filepath)
        if check_resnames:
            default_accepted_resnames = conv_build_resnames_set(default_accepted_resnames)
            user_accepted_resnames = conv_build_resnames_set(accepted_resnames)
            self._check_resnames(self.u, user_accepted_resnames | default_accepted_resnames)
            return


class BaseStructureReferenceFile(BaseArtifactFile):
    pass


class BaseTargetStructureFile(BaseStructureFile):
    pass


class BaseBinderStructureFile(BaseStructureFile):
    pass


class BaseComplexStructureFile(BaseStructureFile):
    pass


class BaseBinderLigandStructureFile(BaseBinderStructureFile):
    pass


class BaseTargetStructureReferenceFile(BaseStructureReferenceFile):
    pass


class BaseBinderStructureReferenceFile(BaseStructureReferenceFile):
    pass


class BaseComplexStructureReferenceFile(BaseStructureReferenceFile):
    pass


class BaseComplexProteinLigandStructureReferenceFile(BaseComplexStructureReferenceFile):
    pass


class BaseBinderLigandStructureReferenceFile(BaseBinderStructureReferenceFile):
    pass


@fileartifact
class TargetProteinPDB(BaseTargetStructureFile):
    prefix: str = "target"
    suffix: str = ".pdb"
    tags: tuple[str] = ("protein",)

    def __init__(
        self,
        filepath: filepath_t,
        *,
        build_universe: bool = False,
        check_resnames: bool = False,
        accepted_resnames: Optional[Iterable] = None,
        **kwargs,
    ) -> None:
        super().__init__(filepath, prefix=self.prefix, suffix=self.suffix, **kwargs)

        self.u: Optional[Universe] = None
        if build_universe:
            super()._build_universe(
                struct_filepath=self.filepath,
                check_resnames=check_resnames,
                default_accepted_resnames=ACCEPTED_PROTEIN_RESNAMES,
                accepted_resnames=accepted_resnames,
            )
        elif check_resnames:
            raise ValueError(f"Cannot check structure {self.filepath} without building its universe.")

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(filepath={self.filepath})"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(filepath={self.filepath})"


@fileartifact
class TargetProteinRestart(BaseTargetStructureFile):
    prefix: str = "target"
    suffix: str = ".rst7"
    tags: tuple = ("protein",)

    def __init__(
        self,
        filepath: filepath_t,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(filepath, prefix=self.prefix, suffix=self.suffix, *args, **kwargs)


@fileartifact
class TargetNAPDB(BaseTargetStructureFile):
    prefix: str = "target"
    suffix: str = ".pdb"
    tags: tuple = ("nucleic",)

    # noinspection PyUnusedLocal
    def __init__(
        self,
        filepath: filepath_t,
        *,
        check_resnames: bool = False,
        accepted_resnames: Optional[Iterable] = None,
        **kwargs,
    ) -> None:
        super().__init__(filepath, prefix=self.prefix, suffix=self.suffix, **kwargs)
        super()._check_file(self.filepath, self.prefix, self.suffix)
        self.u: Optional[Universe] = None
        if check_resnames:
            super()._build_universe(
                struct_filepath=Path(self.filepath),
                check_resnames=check_resnames,
                default_accepted_resnames=ACCEPTED_NA_RESNAMES,
                accepted_resnames=accepted_resnames,
            )


@fileartifact
class BinderLigandPDB(BaseBinderLigandStructureFile):
    prefix: str = "binder"
    suffix: str = ".pdb"
    tags: tuple = ("ligand",)

    # noinspection PyUnusedLocal
    def __init__(self, filepath: filepath_t, *args, **kwargs) -> None:
        super().__init__(filepath, prefix=self.prefix, suffix=self.suffix, **kwargs)


@fileartifact
class BinderLigandMol2(BaseBinderLigandStructureFile):
    prefix: str = "binder"
    suffix: str = ".mol2"
    tags: tuple = ("ligand",)

    def __init__(self, filepath: filepath_t, *args, **kwargs) -> None:
        super().__init__(filepath, prefix=self.prefix, suffix=self.suffix, *args, **kwargs)


@fileartifact
class BinderLigandSmiles(BaseBinderLigandStructureFile):
    prefix: str = "binder"
    suffix: str = ".txt"
    tags: tuple = ("ligand",)

    # noinspection PyUnusedLocal
    def __init__(
        self,
        filepath: filepath_t,
        *,
        build_ligand: bool = False,
        add_hydrogens: bool = True,
        logger: Optional[Logger] = None,
        **kwargs,
    ) -> None:
        super().__init__(filepath, prefix=self.prefix, suffix=self.suffix, **kwargs)
        self.smiles: Optional[str] = None
        self.mol: Optional[Chem.Mol] = None
        if build_ligand:
            self.read_smiles(filepath)
            self.from_string(add_hydrogens)

    def read_smiles(self, filepath: Path) -> str:
        with open(filepath, "r") as file:
            self.smiles = file.read().strip()
            return self.smiles

    def from_string(self, add_hydrogens: bool = True, random_seed=0xF00D) -> Chem.Mol:
        self.mol = Chem.MolFromSmiles(self.smiles)
        if add_hydrogens:
            self.mol = Chem.rdmolops.AddHs(self.mol)

        # noinspection PyUnresolvedReferences
        params = AllChem.ETKDGv3()
        params.randomSeed = random_seed
        # noinspection PyUnresolvedReferences
        AllChem.EmbedMolecule(self.mol, params)
        return self.mol


@fileartifact
class BinderLigandRestart(BaseBinderLigandStructureFile):
    prefix: str = "binder"
    suffix: str = ".rst7"
    tags: tuple = ("ligand",)

    def __init__(
        self,
        filepath: filepath_t,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(filepath, prefix=self.prefix, suffix=self.suffix, *args, **kwargs)


@fileartifact
class ComplexProteinLigandPDB(BaseComplexStructureFile):
    prefix: str = "complex"
    suffix: str = ".pdb"
    tags: tuple = ("protein", "ligand")

    def __init__(
        self,
        filepath: filepath_t,
        *,
        check_resnames: bool = False,
        accepted_resnames: Optional[Sequence] = None,
        **kwargs,
    ) -> None:
        super().__init__(
            filepath,
            prefix=self.prefix,
            suffix=self.suffix,
            check_resnames=check_resnames,
            accepted_resnames=accepted_resnames,
            **kwargs,
        )


@fileartifact
class ComplexProteinLigandRestart(BaseComplexStructureFile):
    prefix: str = "complex"
    suffix: str = ".rst7"
    tags: tuple = ("protein", "ligand")

    def __init__(
        self,
        filepath: filepath_t,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(filepath, prefix=self.prefix, suffix=self.suffix, *args, **kwargs)


@fileartifact
class ComplexNucleicLigandPDB(BaseComplexStructureFile):
    prefix: str = "complex"
    suffix: str = ".pdb"
    tags: tuple = ("nucleic", "ligand")

    def __init__(
        self,
        filepath: filepath_t,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(filepath, prefix=self.prefix, suffix=self.suffix, *args, **kwargs)


@fileartifact
class TargetProteinReferenceRestart(BaseTargetStructureReferenceFile):
    prefix: str = "targetref"
    suffix: str = ".rst7"
    tags: tuple = ("protein", "reference")

    def __init__(
        self,
        filepath: filepath_t,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(filepath, prefix=self.prefix, suffix=self.suffix, *args, **kwargs)


@fileartifact
class BinderLigandReferenceRestart(BaseBinderLigandStructureReferenceFile):
    prefix: str = "binderref"
    suffix: str = ".rst7"
    tags: tuple = ("ligand", "reference")

    def __init__(
        self,
        filepath: filepath_t,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(filepath, prefix=self.prefix, suffix=self.suffix, *args, **kwargs)


@fileartifact
class ComplexProteinLigandReferenceRestart(BaseComplexProteinLigandStructureReferenceFile):
    prefix: str = "complexref"
    suffix: str = ".rst7"
    tags: tuple = ("protein", "ligand", "reference")

    def __init__(
        self,
        filepath: filepath_t,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(filepath, prefix=self.prefix, suffix=self.suffix, *args, **kwargs)


# noinspection PyTypeHints
def get_biomolecule(input_artifacts: BatchArtifacts | ArtifactContainer, node_logger: Logger) -> str:
    if isinstance(input_artifacts, BatchArtifacts):
        some_art_container = next(iter(input_artifacts.values()))
        some_artifacts = next(iter(some_art_container.values()))
    elif isinstance(input_artifacts, ArtifactContainer):
        some_artifacts = next(iter(input_artifacts.values()))
    else:
        err_msg = f"Invalid input type {type(input_artifacts)}. Must be BatchArtifacts or ArtifactContainer."
        node_logger.error(err_msg)
        raise ValueError(err_msg)

    tags = [getattr(art, "tags", tuple()) for art in some_artifacts if isinstance(art, BaseComplexStructureFile)]
    flattened_tags = [item for sublist in tags for item in sublist]
    if "nucleic" in flattened_tags:
        if "protein" in flattened_tags:
            err_msg = f"Invalid system. Found both nucleic and protein tags ({tags}) in {some_artifacts}"
            node_logger.error(err_msg)
            raise ValueError(err_msg)
        else:
            return "nucleic"
    elif "protein" in flattened_tags:
        if "nucleic" in flattened_tags:
            err_msg = f"Invalid system. Found both nucleic and protein tags ({tags}) in {some_artifacts}"
            node_logger.error(err_msg)
            raise ValueError(err_msg)
        else:
            return "protein"
    else:
        err_msg = f"Could not determine biomolecule type from tags ({tags}) in {some_artifacts}"
        node_logger.error(err_msg)
        raise ValueError(err_msg)
