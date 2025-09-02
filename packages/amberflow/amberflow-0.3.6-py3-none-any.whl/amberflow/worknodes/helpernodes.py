"""
Provides a collection of utility and helper worknodes for data workflows.

This module contains a variety of `WorkNode` implementations that perform common,
reusable tasks within a larger data processing pipeline. These nodes handle
operations such as filtering artifacts, merging structural data, collecting
files, and performing specialized file modifications like adding chain IDs to
PDB files.

Classes
-------
WorkNodeDummy
    A simple node that copies its input artifacts to its output.
Filter
    Selectively passes through artifacts based on their type.
JoinTargetBinder
    Merges protein (target) and ligand (binder) structure files into a
    single complex.
CollectFiles
    A base class for nodes that gather and potentially link files.
AddChainid
    Assigns unique, sequential chain IDs to molecules within a PDB file.
"""

import os
import mmap
import shutil
import string
import warnings
from pathlib import Path
from typing import Optional, Sequence, List, Type

import MDAnalysis as mda
import numpy as np
from typing_extensions import override

from amberflow.artifacts import (
    BaseArtifact,
    ArtifactContainer,
    BaseTargetStructureFile,
    BinderLigandPDB,
    BaseBinderStructureFile,
    ArtifactRegistry,
    BaseStructureFile,
)
from amberflow.primitives import dirpath_t, filepath_t
from amberflow.worknodes import worknodehelper, BaseSingleWorkNode, runiverse, wuniverse

__all__ = [
    "WorkNodeDummy",
    "Filter",
    "JoinTargetBinder",
    "CollectFiles",
    "AddChainid",
]


@worknodehelper(file_exists=True, input_artifact_types=(BaseArtifact,))
class WorkNodeDummy(BaseSingleWorkNode):
    """
    A simple worknode that copies all input artifacts to its output.

    This node serves as a placeholder or a simple pass-through mechanism in a
    workflow, duplicating its inputs without modification. It's useful for
    debugging or forking workflow paths.
    """

    @override
    def __init__(
        self,
        wnid: str,
        *args,
        **kwargs,
    ):
        """
        Initializes the WorkNodeDummy instance.

        Args:
            wnid (str): A unique identifier for the worknode instance.
            *args: Positional arguments passed to the parent class.
            **kwargs: Keyword arguments passed to the parent class.
        """
        super().__init__(wnid=wnid, *args, **kwargs)

    @override
    def _run(
        self,
        *args,
        cwd: dirpath_t,
        sysname: str,
        **kwargs,
    ) -> ArtifactContainer:
        # This is all that the dummy node does:
        output_artifacts = []
        for arts in self.input_artifacts.values():
            for artifact in arts:
                try:
                    copy_to_method = getattr(artifact, "copy_to")
                    output_artifacts.append(copy_to_method(self.work_dir))
                except AttributeError:
                    raise AttributeError(f"Artifact {artifact} does not have a copy_to() method.")
        self.output_artifacts = ArtifactContainer(sysname, output_artifacts)
        return self.output_artifacts

    def __repr__(self) -> str:
        return f"WorkNodeDummy(id={self.id})"


@worknodehelper(file_exists=True)
class Filter(BaseSingleWorkNode):
    """
    A worknode that filters artifacts based on their type.

    This node can be configured to either include or exclude a specified list
    of artifact types, allowing for selective processing in a workflow.
    """

    @override
    def __init__(
        self,
        wnid: str,
        *args,
        artifact_types: Sequence[Type],
        in_or_out: str = "in",
        **kwargs,
    ):
        """
        Initializes the Filter instance.

        Args:
            wnid (str): A unique identifier for the worknode instance.
            artifact_types (Sequence[type]): A sequence of artifact classes to
                be used for filtering.
            in_or_out (str): Determines the filtering logic. "in" to keep
                matching types, "out" to keep non-matching types.
            *args: Positional arguments passed to the parent class.
            **kwargs: Keyword arguments passed to the parent class.
        """
        super().__init__(wnid=wnid, *args, **kwargs)
        self.artifact_types = artifact_types
        if in_or_out not in ("in", "out"):
            raise ValueError(f"in_or_out must be 'in' or 'out', got {in_or_out}.")
        self.in_or_out = in_or_out

    def _run(
        self,
        *args,
        cwd: dirpath_t,
        sysname: str,
        **kwargs,
    ) -> ArtifactContainer:
        """
        Executes the filtering logic on the input artifacts.

        Args:
            cwd (dirpath_t): The working directory for this execution.
            sysname (str): The name of the system being processed.
            **kwargs: Additional keyword arguments.

        Returns:
            An ArtifactContainer holding the artifacts that passed the filter.
        """
        output_artifacts: List[BaseArtifact] = []
        for arts in self.input_artifacts.values():
            for artifact in arts:
                is_instance = isinstance(artifact, tuple(self.artifact_types))
                if (is_instance and self.in_or_out == "in") or (not is_instance and self.in_or_out == "out"):
                    self._add(artifact, output_artifacts)

        if not output_artifacts:
            self.node_logger.warning(
                f"No artifacts passed the filter with types {self.artifact_types} and mode '{self.in_or_out}'."
            )
        self.output_artifacts = ArtifactContainer(sysname, output_artifacts)
        return self.output_artifacts

    def _add(self, artifact: BaseArtifact, output_artifacts: list[BaseArtifact]) -> None:
        """
        Copies the artifact to the work directory and adds it to the output list.
        """
        if hasattr(artifact, "filepath"):
            copy_to_method = getattr(artifact, "copy_to")
            output_artifacts.append(copy_to_method(self.work_dir))
        else:
            output_artifacts.append(artifact)

    def _try_and_skip(self, sysname: str) -> bool:
        raise NotImplementedError

    def fill_output_artifacts(
        self,
        sysname: str,
    ) -> ArtifactContainer:
        raise NotImplementedError

    def __repr__(self) -> str:
        """Provides a developer-friendly representation of the node."""
        return f"{self.__class__.__name__}(id={self.id}, artifact_types={self.artifact_types})"


@worknodehelper(file_exists=True, input_artifact_types=(BaseTargetStructureFile, BinderLigandPDB))
class JoinTargetBinder(BaseSingleWorkNode):
    """
    Merges separate target (e.g., protein) and binder (e.g., ligand)
    structure files into a single complex structure file (PDB).
    """

    @override
    def __init__(
        self,
        wnid: str,
        *args,
        binder_first: bool = True,
        to_guess: Optional[tuple] = None,
        renumber: bool = False,
        starting_residue: int = 1,
        **kwargs,
    ):
        """
        Initializes the JoinTargetBinder instance.

        Args:
            wnid (str): A unique identifier for the worknode instance.
            binder_first (bool): If True, the binder's atoms will appear first
                in the output file. Otherwise, the target's atoms will.
            to_guess (Optional[tuple]): Options passed to MDAnalysis for guessing
                bond information when reading structures.
            renumber (bool): If True, renumbers residues sequentially starting
                from `starting_residue`.
            starting_residue (int): The starting number for residue renumbering.
            *args: Positional arguments passed to the parent class.
            **kwargs: Keyword arguments passed to the parent class.
        """
        super().__init__(wnid=wnid, *args, **kwargs)
        self.binder_first = binder_first
        self.renumber = renumber
        self.starting_residue = starting_residue
        self.to_guess = to_guess

    def _run(
        self,
        *args,
        cwd: dirpath_t,
        sysname: str,
        **kwargs,
    ) -> ArtifactContainer:
        """
        Executes the merging logic.

        Args:
            cwd (dirpath_t): The working directory for this execution.
            sysname (str): The name of the system being processed.
            **kwargs: Additional keyword arguments.

        Returns:
            An ArtifactContainer with the newly created complex structure file.

        Raises:
            AttributeError: If an unexpected artifact type is encountered.
        """
        utarget: Optional[mda.Universe] = None
        ubinder: Optional[mda.Universe] = None
        for arts in self.input_artifacts.values():
            for artifact in arts:
                if isinstance(artifact, BaseTargetStructureFile):
                    self.node_logger.debug(f"Found target structure file: {artifact}")
                    utarget = runiverse(artifact, to_guess=self.to_guess)
                elif isinstance(artifact, BaseBinderStructureFile):
                    self.node_logger.debug(f"Found binder structure file: {artifact}")
                    ubinder = runiverse(artifact, to_guess=self.to_guess)
                else:
                    err_msg = f"Artifact {artifact} is not a BaseTargetFile or BaseBinderFile."
                    self.node_logger.error(err_msg)
                    raise AttributeError(err_msg)

        # MDAnalysis doesn't add TER records between segments, thankfully tleap can split molecules based on different
        # chainIDs / segids
        self.fix_chainids(utarget, string.ascii_uppercase, "TAR")
        self.fix_chainids(ubinder, string.ascii_uppercase[-3:], "BIN")

        if not hasattr(ubinder.atoms, "chainIDs") or any(np.equal(ubinder.atoms.chainIDs, "")):
            self.node_logger.warning(
                f"At least 1 atom in {ubinder.filename} lacks a chainID. This may cause issues later."
            )

        if self.binder_first:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                ucpx = mda.Merge(ubinder.atoms, utarget.atoms)
        else:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                ucpx = mda.Merge(utarget.atoms, ubinder.atoms)

        if self.renumber:
            ucpx.residues.resids = np.arange(self.starting_residue, len(ucpx.residues.resids) + self.starting_residue)

        out_pdb = self.work_dir / f"complex_{sysname}.pdb"
        wuniverse(ucpx, out_pdb)

        # TODO: document how to use tags and probably improve the API
        tar_type: str = self.artifact_map["BaseTargetStructureFile"]
        bin_type: str = self.artifact_map["BinderLigandPDB"]
        file_artifact = ArtifactRegistry.create_instance_by_filename(
            out_pdb, tags=self.tags[tar_type] + self.tags[bin_type]
        )

        self.output_artifacts = ArtifactContainer(sysname, (file_artifact,))
        return self.output_artifacts

    def fix_chainids(self, universe: mda.Universe, available_chainids: Sequence[str], segid: str) -> None:
        if not hasattr(universe.atoms, "chainIDs"):
            universe.add_TopologyAttr("chainID")
            self.node_logger.warning(f"{universe.filename} lacks chainID information. This may cause issues later.")
        elif any(np.equal(universe.atoms.chainIDs, "")):
            self.node_logger.warning(
                f"At least 1 atom in {universe.filename} lacks a chainID. This may cause issues later."
            )

            for sgmnt, chainid in zip(universe.segments, available_chainids):
                sgmnt.atoms.chainIDs = chainid

        # Assign a unique segid to the binder and another one to the target
        universe.segments.segids = segid

    def _try_and_skip(self, sysname: str) -> bool:
        raise NotImplementedError

    def fill_output_artifacts(
        self,
        sysname: str,
    ) -> ArtifactContainer:
        raise NotImplementedError


@worknodehelper(file_exists=True, input_artifact_types=(BaseArtifact,))
class CollectFiles(BaseSingleWorkNode):
    """
    NOT BEING USED.

    This class is intended to be subclassed. The `symlink_dat_dirs` method
    provides utility for linking directories into the working directory.
    """

    @override
    def __init__(
        self,
        wnid: str,
        *args,
        **kwargs,
    ):
        """
        Initializes the CollectFiles instance.

        Args:
            wnid (str): A unique identifier for the worknode instance.
            *args: Positional arguments passed to the parent class.
            **kwargs: Keyword arguments passed to the parent class.
        """
        super().__init__(wnid=wnid, *args, **kwargs)

    def _run(
        self,
        *args,
        cwd: dirpath_t,
        sysname: str,
        **kwargs,
    ) -> ArtifactContainer:
        """This method must be implemented by subclasses."""
        raise NotImplementedError

    def symlink_dat_dirs(self, dir_list: list[BaseArtifact]) -> Optional[str]:
        """
        Symlinks directory artifacts into the node's working directory.

        It also determines the common 'environment' from the
        artifacts if one exists.

        Args:
            dir_list (list[BaseArtifact]): A list of artifacts that represent
                directories to be linked.

        Returns:
            The common environment string if one is found, otherwise None.

        Raises:
            ValueError: If multiple different environments are detected.
        """
        environment: Optional[str] = None
        if dir_list:
            all_environments = set()
            for datdir in dir_list:
                dirpath = getattr(datdir, "filepath")
                if dirpath is None or not dirpath.is_dir():
                    self.node_logger.warning(f"Artifact {datdir} does not have a valid directory path, skipping.")
                    continue
                parent_filepath = getattr(datdir, "parent_filepath")
                dat_dir_layout = Path(dirpath).relative_to(dirpath).parts
                for i in range(1, len(dat_dir_layout) + 1):
                    current_dat_dirname = Path(*dat_dir_layout[0:i])
                    local_dat_dir = Path(parent_filepath, current_dat_dirname)
                    try:
                        os.symlink(local_dat_dir, self.work_dir / current_dat_dirname, target_is_directory=True)
                    except FileExistsError:
                        continue
                environment = getattr(datdir, "environment")
                all_environments.add(environment)
            if len(all_environments) == 1:
                environment = all_environments.pop()
            elif len(all_environments) > 1:
                raise ValueError(f"Too many environments: {all_environments}. It should be just 1")
        return environment

    def _try_and_skip(self, sysname: str) -> bool:
        raise NotImplementedError

    def fill_output_artifacts(
        self,
        sysname: str,
    ) -> ArtifactContainer:
        raise NotImplementedError


@worknodehelper(file_exists=True, input_artifact_types=(BaseStructureFile,))
class AddChainid(BaseSingleWorkNode):
    """
    A worknode that assigns sequential chain IDs to molecules in a PDB file.

    It identifies separate molecules by 'TER' records and assigns chain IDs
    from A-Z, then a-z. The process is memory-efficient, using memory-mapping
    to modify a copy of the file in place.
    """

    @override
    def __init__(
        self,
        wnid: str,
        *args,
        **kwargs,
    ):
        """
        Initializes the AddChainid instance.

        Args:
            wnid (str): A unique identifier for the worknode instance.
            *args: Positional arguments passed to the parent class.
            **kwargs: Keyword arguments passed to the parent class.
        """
        super().__init__(wnid=wnid, *args, **kwargs)

    def _run(
        self,
        *args,
        cwd: dirpath_t,
        sysname: str,
        **kwargs,
    ) -> ArtifactContainer:
        """
        Executes the chain ID assignment for each input PDB file.

        Args:
            cwd (dirpath_t): The working directory for this execution.
            sysname (str): The name of the system being processed.
            **kwargs: Additional keyword arguments.

        Returns:
            An ArtifactContainer with the modified PDB file artifacts.
        """
        if self._try_and_skip(sysname):
            return self.output_artifacts

        for artifacts in self.input_artifacts.values():
            for art in artifacts:
                if art.filepath.suffix.lower() != ".pdb":
                    self.node_logger.warning(f"{art} is not a PDB file, skipping.")
                    continue
                self.assign_chain_ids_mmap(art.filepath, Path(self.work_dir, art.filepath.name))

        self.output_artifacts = self.fill_output_artifacts(sysname)
        return self.output_artifacts

    @staticmethod
    def assign_chain_ids_mmap(input_pdb_path: filepath_t, output_pdb_path: filepath_t) -> None:
        """
        Assigns a unique chain ID to each molecule in a PDB file using mmap.

        This function processes a PDB file, identifying molecules separated by
        "TER" records. It assigns a chain ID character from A-Z, then a-z, to
        each molecule. The modification is done in-place on a copy of the
        original file using a memory map for high performance.

        If more than 52 molecules are present, subsequent molecules will not
        have their chain ID modified.

        Args:
            input_pdb_path (filepath_t): The path to the source PDB file.
            output_pdb_path (filepath_t): The path where the modified PDB file
                will be saved.
        """
        # Create a generator for the chain IDs (A-Z, then a-z)
        chain_id_chars = iter(string.ascii_uppercase + string.ascii_lowercase)

        # mmap works directly on the output file
        shutil.copy(input_pdb_path, output_pdb_path)
        with open(output_pdb_path, "r+b") as f:
            # Create a memory-mapped file object
            with mmap.mmap(f.fileno(), 0) as mm:
                # Get the first chain ID for the first molecule
                current_chain_id = next(chain_id_chars, None)

                line_start = 0
                while line_start < len(mm):
                    # Find the end of the current line
                    line_end = mm.find(b"\n", line_start)
                    if line_end == -1:  # End of file
                        line_end = len(mm)

                    # Check ATOM/HETATM records
                    # The chain ID is at a fixed position (column 22, index 21)
                    if mm[line_start : line_start + 6] in (b"ATOM  ", b"HETATM"):
                        if current_chain_id is not None:
                            # Modify the byte in-place
                            mm[line_start + 21] = ord(current_chain_id)

                    # Check for molecule separator
                    elif mm[line_start : line_start + 3] == b"TER":
                        # Move to the next chain ID for the next molecule
                        current_chain_id = next(chain_id_chars, None)

                    # Move to the start of the next line
                    line_start = line_end + 1

    def _try_and_skip(self, sysname: str) -> bool:
        """Checks if the node's execution can be skipped."""
        if self.skippable:
            try:
                self.output_artifacts = self.fill_output_artifacts(sysname)
                self.node_logger.info(f"Skipped {self.id} WorkNode.")
                return True
            except (FileNotFoundError, ValueError) as e:
                self.node_logger.info(f"Can't skip {self.id} Got: {e}")
        return False

    def fill_output_artifacts(self, sysname: str) -> ArtifactContainer:
        """Creates output artifacts corresponding to pre-existing files."""
        output_artifacts = [
            ArtifactRegistry.create_instance_by_name(art.__class__.__name__, self.work_dir / art.filepath.name)
            for artifacts in self.input_artifacts.values()
            for art in artifacts
        ]
        return ArtifactContainer(sysname, output_artifacts)
