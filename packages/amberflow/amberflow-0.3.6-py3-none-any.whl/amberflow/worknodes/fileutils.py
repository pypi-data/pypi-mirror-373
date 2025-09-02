"""
Provides worknodes for Zstandard compression and decompression within a workflow.

This module contains classes for handling TAR archives compressed with the
Zstandard (`.tar.zst`) algorithm. These are designed as `WorkNode` components
for use in data processing pipelines, allowing for efficient archiving and
extraction of intermediate files.

Classes
-------
CompressZstd
    A worknode that takes one or more input artifacts and compresses them
    into a single `.tar.zst` archive.
ExtractZstd
    A worknode that takes a `.tar.zst` archive and extracts its contents
    into the node's working directory.
"""

import tarfile
from pathlib import Path
from typing import Any, Sequence

import zstandard as zstd

from amberflow.artifacts import (
    BaseArtifact,
    ArtifactContainer,
    TarZstd,
    BaseStatesFile,
    BaseDatdir,
)
from amberflow.primitives import dirpath_t, filepath_t
from amberflow.worknodes import BaseSingleWorkNode, worknodehelper

__all__ = ("CompressZstd", "ExtractZstd")


@worknodehelper(
    file_exists=True,
    output_artifact_types=(TarZstd,),
)
class CompressZstd(BaseSingleWorkNode):
    """
    Archives and compresses all input artifacts using the Zstandard algorithm into a .tar.zst file.

    User can then uncompress with:
    ```
    find . -name "*zst" | xargs -n1 tar -xf
    ```
    """

    takes_multiple_artifacts = True

    def __init__(
        self,
        wnid: str,
        *args,
        artifact_types: Sequence[str],
        level: int = 22,
        cores: int = 1,
        **kwargs,
    ) -> None:
        super().__init__(
            wnid=wnid,
            *args,
            **kwargs,
        )
        self.supported_artifacts = {
            "BaseMdoutMD",
            "BaseStructureFile",
            "BaseStructureReferenceFile",
            "BaseTopologyFile",
            "BaseMdoutStates",
            "BaseRestartStatesFile",
            "BoreschRestraints",
            "LambdaScheduleFile",
            "GroupFile",
            "Remlog",
            "BaseDatdir",
            "EdgeMBARxml",
            "EdgeMBARhtml",
        }
        self.level = level
        self.cores = cores
        if len(set(artifact_types) - self.supported_artifacts) != 0:
            err_msg = f"Unsupported artifact types {set(artifact_types) - self.supported_artifacts} for {self.id}."
            raise ValueError(err_msg)
        self.artifact_types = artifact_types

    def _run(
        self,
        *,
        cwd: dirpath_t,
        sysname: str,
        **kwargs,
    ) -> Any:
        input_filepaths = self.get_inputs()
        art_output_filepaths_map: dict[str, Path] = {
            art_type: Path(self.work_dir, f"{art_type}_{sysname}.tar.zst")
            for art_type, filepaths in input_filepaths.items()
        }
        output_filepaths = list(art_output_filepaths_map.values())
        if self.skippable:
            if self._try_and_skip(sysname, output_filenames=output_filepaths):
                return self.output_artifacts

        input_filepaths = self.get_inputs()
        for in_filepaths, out_tar_zst in zip(input_filepaths.values(), art_output_filepaths_map.values()):
            self.write_zstd(in_filepaths, self.level, self.cores, out_tar_zst)
        self.output_artifacts = self.fill_output_artifacts(sysname, output_filenames=output_filepaths)
        return self.output_artifacts

    def get_inputs(self) -> dict[str, list[Any]]:
        input_filepaths = {}
        for art_type in self.artifact_types:
            artifacts = self.input_artifacts.get_as_list(art_type)
            if artifacts is None:
                self.node_logger.warning(f"No input artifacts of type {art_type} found")
                continue
            artifact_type_filepaths = []
            for art in artifacts:
                if isinstance(art, BaseStatesFile):
                    states = getattr(art, "states")
                    if states is not None:
                        states_filepaths = []
                        for key, state in states.items():
                            filepath = Path(state)
                            if filepath is not None and filepath.is_file():
                                states_filepaths.append(filepath)
                                self.node_logger.debug(f"Found state file for {key}: {filepath}")
                            else:
                                self.node_logger.warning(f"No valid filepath for state {key} in artifact {art}.")
                        input_filepaths[art_type] = states_filepaths
                    else:
                        self.node_logger.warning(
                            f"No states found in artifact {art} which is a BaseStatesFile. Arifact is corrupted?"
                        )
                else:
                    filepath = (
                        getattr(art, "parent_filepath") if isinstance(art, BaseDatdir) else getattr(art, "filepath")
                    )
                    if filepath is not None:
                        artifact_type_filepaths.append(filepath)
                        self.node_logger.debug(f"Found {filepath} of type {art_type}")
            if len(artifact_type_filepaths) > 0:
                input_filepaths[art_type] = artifact_type_filepaths
            else:
                self.node_logger.warning(f"No input artifacts of type {art_type} found")

        if len(input_filepaths) == 0:
            err_msg = (
                f"No valid input artifacts found for {self.id} `input_artifacts`: {self.input_artifacts} - "
                f"Requested `artifact_types`: {self.artifact_types}"
            )
            self.node_logger.error(err_msg)
            raise ValueError(err_msg)
        return input_filepaths

    @staticmethod
    def write_zstd(files: Sequence[Path], compression_level: int, cores: int, output_filename: filepath_t) -> Path:
        # Set up the Zstandard compressor with the highest level and all cores
        cctx = zstd.ZstdCompressor(level=compression_level, threads=cores)

        with open(output_filename, "wb") as f_out:
            with cctx.stream_writer(f_out) as compressor:
                with tarfile.open(fileobj=compressor, mode="w") as tar:
                    for file_path in files:
                        tar.add(file_path, arcname=file_path.name)
        return output_filename

    def _try_and_skip(self, sysname: str, *, output_filenames: list[Path]) -> bool:
        """
        Determines if the worknode execution can be skipped.

        Args:
            sysname (str): The name of the system being processed.
            output_filenames (Sequence[Path]): List of output filenames to check for existence.

        Returns:
            True if the node can be skipped, False otherwise.
        """
        if self.skippable:
            try:
                self.output_artifacts = self.fill_output_artifacts(sysname, output_filenames=output_filenames)
                self.node_logger.info(f"Skipped {self.id} WorkNode.")
                return True
            except (FileNotFoundError, ValueError) as e:
                self.node_logger.debug(f"Can't skip {self.id} Got:{e}")
            except NotImplementedError:
                self.node_logger.debug(
                    f"Can't skip {self.id}. {self.__class__.__name__} did not implement `fill_output_artifacts()`"
                )
        return False

    # noinspection PyMethodMayBeStatic
    def fill_output_artifacts(
        self,
        sysname: str,
        *,
        output_filenames: Sequence[Path],
    ) -> ArtifactContainer:
        """
        Populates output artifacts when a node is skipped.

        If `_try_and_skip` determines that a node can be skipped, this method
        is responsible for creating the artifact objects that correspond to
        the pre-existing output files.

        Args:
            sysname (str): The name of the system being processed.
            output_filenames (Sequence[Path]): List of output filenames to create artifacts for.

        Returns:
            An `ArtifactContainer` or `BatchArtifacts` object containing the
            output artifacts for the skipped node.
        """

        return ArtifactContainer(sysname, [TarZstd(filename) for filename in output_filenames])


@worknodehelper(file_exists=True, input_artifact_types=(TarZstd,), output_artifact_types=(BaseArtifact,))
class ExtractZstd(BaseSingleWorkNode):
    """
    Archives and compresses all input artifacts using the Zstandard algorithm into a .tar.zst file.

    """

    def __init__(
        self,
        wnid: str,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(
            wnid=wnid,
            *args,
            **kwargs,
        )

    def _run(
        self,
        *,
        cwd: dirpath_t,
        sysname: str,
        **kwargs,
    ) -> Any:
        if self.skippable:
            if self._try_and_skip(sysname):
                return self.output_artifacts

        dctx = zstd.ZstdDecompressor()
        for tar_zstd in self.input_artifacts.get_as_list("TarZstd"):
            tar_zstd_filepath = getattr(tar_zstd, "filepath")
            assert tar_zstd_filepath is not None, f"{tar_zstd} should have a filepath."
            if not tar_zstd_filepath.is_file():
                err_msg = f"Input file {tar_zstd_filepath} does not exist or is not a file."
                self.node_logger.error(err_msg)
                raise FileNotFoundError(err_msg)
            with open(tar_zstd_filepath, "rb") as f_in:
                with dctx.stream_reader(f_in) as reader:
                    with tarfile.open(fileobj=reader, mode="r:") as tar:
                        file_list = tar.getnames()
                        self.node_logger.debug(f"Found {len(file_list)} files in {tar_zstd_filepath}: {file_list}")
                        tar.extractall(path=self.work_dir)

        return self.output_artifacts

    def _try_and_skip(self, sysname: str) -> bool:
        """
        Determines if the worknode execution can be skipped.

        This method is called if the `skippable` attribute is True. It should check for the existence of expected
        output files or other conditions that would make re-running the node unnecessary.
        It's not strictly required to implement this method.

        Args:
            sysname (str): The name of the system being processed.

        Returns:
            True if the node can be skipped, False otherwise.
        """
        if self.skippable:
            try:
                self.output_artifacts = self.fill_output_artifacts(sysname)
                self.node_logger.info(f"Skipped {self.id} WorkNode.")
                return True
            except FileNotFoundError as e:
                self.node_logger.debug(f"Can't skip {self.id} Got: {e}")
            except ValueError as e:
                self.node_logger.debug(f"Can't skip {self.id} Got:{e}")
            except NotImplementedError:
                self.node_logger.debug(
                    f"Can't skip {self.id}. {self.__class__.__name__} did not implement `fill_output_artifacts()`"
                )
        return False

    def fill_output_artifacts(
        self,
        sysname: str,
    ) -> ArtifactContainer:
        """
        Populates output artifacts when a node is skipped.

        If `_try_and_skip` determines that a node can be skipped, this method
        is responsible for creating the artifact objects that correspond to
        the pre-existing output files.

        Args:
            sysname (str): The name of the system being processed.

        Returns:
            An `ArtifactContainer` or `BatchArtifacts` object containing the
            output artifacts for the skipped node.
        """
        # return ArtifactContainer(sysname, self.artifact_builder[BaseTopologyFile](outfile))
        raise NotImplementedError
