import itertools
import shutil as sh
from importlib import resources
import subprocess as sp
from functools import singledispatch
from logging import Logger
import mmap
from pathlib import Path
from typing import Final, Set, Union, TypeAlias, Optional
import re
from warnings import warn

from attr import asdict

from .. import __package__

from Bio.SeqUtils import seq1
from attrs import frozen, field, define

__all__ = [
    "FileHandle",
    "InvalidPipeline",
    "UserInputError",
    "StructureError",
    "UnknownFileType",
    "ArtifactError",
    "UnknownArtifactError",
    "MissingTagsError",
    "NonmatchingTagsError",
    "WorkNodeError",
    "UnknownWorkNodeError",
    "WorkNodeRunningError",
    "CommandError",
    "MDError",
    "BadMDout",
    "CommandRunningError",
    "SLURMError",
    "CheckpointError",
    "ext",
    "my_seq1",
    "get_gpu_count",
    "CyclicalContainer",
    "SystemPath",
    "DirHandle",
    "update_header",
    "catenate",
    "catenate_pdbs",
    "copy_to",
    "ACCEPTED_PROTEIN_RESNAMES",
    "ACCEPTED_NA_RESNAMES",
    "DEFAULT_RESOURCES_PATH",
    "filepath_t",
    "dirpath_t",
    "find_word_and_get_line",
    "convert_to_refname",
]

DEFAULT_RESOURCES_PATH = resources.files(__package__) / "data"

# This will be used to map non-conventional AAs to conventional ones
AA_MAP: Final[dict[str, str]] = {
    "ALA": "ALA",
    "ARG": "ARG",
    "ASN": "ASN",
    "ASP": "ASP",
    "CYS": "CYS",
    "CYX": "CYS",
    "CY2": "CYS",
    "GLN": "GLN",
    "GLU": "GLU",
    "GLY": "GLY",
    "HIS": "HIS",
    "HIE": "HIS",
    "HE1": "HIS",
    "HID": "HIS",
    "ILE": "ILE",
    "LEU": "LEU",
    "LYS": "LYS",
    "MET": "MET",
    "PHE": "PHE",
    "PRO": "PRO",
    "SER": "SER",
    "THR": "THR",
    "TRP": "TRP",
    "TYR": "TYR",
    "VAL": "VAL",
}

MISC_RESNAMES: Final[Set] = {"WAT", "Na+", "Cl-", "Na", "Cl"}
ACCEPTED_PROTEIN_RESNAMES: Final[Set] = set(AA_MAP.keys()) | MISC_RESNAMES
ACCEPTED_NA_RESNAMES: Final[Set] = {"C", "G", "T", "A", "C3", "C5", "G3", "G5", "T3", "T5", "A3", "A5"}
DEFAULT_BINDER_NAME: Final[str] = "LIG"


@define
class FileHandle:
    path: Path = field(converter=Path)
    name: str = field(init=False)
    extension: str = field(init=False)

    # noinspection PyUnusedLocal
    @path.validator  # type: ignore
    def file_exists(self, attribute, value: Path):
        if not value.is_file():
            raise FileNotFoundError(f"File: {value} doesn't exist.")

    def __attrs_post_init__(self):
        try:
            self.name, self.extension = self.path.name.split(".")
        except ValueError:
            self.name = self.path.name
            self.extension = ""
        except Exception as e:
            print(f"Bad input for FileHandle: {self.path}", flush=True)
            raise e

    @classmethod
    def from_existing(cls, name: Path) -> "FileHandle":
        # This method conflicts with the default constructor
        # I'm just leaving it here in case I want to use it later.
        return cls(name)

    def __str__(self) -> str:
        return str(self.path)

    def __fspath__(self) -> str:
        return self.__str__()

    def unlink(self) -> None:
        self.path.unlink()

    def replace_text(self, text_0: str, text_1: str) -> None:
        with open(self.path, "r") as f:
            lineas = f.read()
        lineas = lineas.replace(text_0, text_1)
        with open(self.path, "w") as f:
            f.write(lineas)

    def name_ext(self) -> str:
        return self.path.name


filepath_t: TypeAlias = Union[str, Path, FileHandle]


class InvalidPipeline(Exception):
    pass


class UserInputError(Exception):
    pass


class StructureError(Exception):
    pass


class UnknownFileType(Exception):
    pass


class ArtifactError(Exception):
    pass


class UnknownArtifactError(ArtifactError):
    pass


class MissingTagsError(ArtifactError):
    pass


class NonmatchingTagsError(ArtifactError):
    pass


class WorkNodeError(Exception):
    pass


class UnknownWorkNodeError(WorkNodeError):
    pass


class WorkNodeRunningError(WorkNodeError):
    pass


class CommandError(Exception):
    pass


class MDError(Exception):
    """Base class for errors related to molecular dynamics simulations."""

    pass


class BadMDout(MDError):
    pass


class CommandRunningError(CommandError):
    pass


class SLURMError(CommandError):
    pass


class CheckpointError(Exception):
    pass


def report_error(err_type: type, err_msg: str, logger: Optional[Logger] = None) -> None:
    if logger:
        logger.error(err_msg)
    raise err_type(err_msg)


def ext(name: str, suffix: str) -> str:
    """ext utility function, so I don't have to worry about the extension.

    Args:
        name (str): filename with or without the extension.
        suffix (str): desired extension.

    Returns:
        str: filename with the extension.
    """
    return f"{name.split('.')[0]}.{suffix}"


def my_seq1(resn_3: str) -> str:
    resn_1 = seq1(resn_3)
    if resn_1 == "X":
        try:
            resn_1 = seq1(AA_MAP[resn_3])
            warn(f"Converted non-standard residue {resn_3} from 3-letter code to 1-letter: {resn_1}.")
        except KeyError:
            warn(f"Could not convert non-standard residue {resn_3} from 3-letter code to 1-letter. Setting it to 'X'.")
    return resn_1


def get_gpu_count():
    """
    Get the number of available GPUs on the system.

    Returns:
        int: The number of available GPUs.
    """
    try:
        output = sp.check_output(["nvidia-smi", "-L"])
        gpu_count = len(output.decode("utf-8").strip().split("\n"))
    except (sp.CalledProcessError, FileNotFoundError):
        # If nvidia-smi fails or is not found, assume no GPUs are available
        gpu_count = 0
    return gpu_count


class CyclicalContainer:
    """
    A container that cycles indefinitely through a range given from 0 to n-1.
    """

    def __init__(self, n: int):
        self._items = tuple(range(n))
        self._iterator = itertools.cycle(self._items)

    def __getstate__(self):
        """Return the state to be pickled."""
        return {"items": self._items}

    def __setstate__(self, state):
        """Restore the state from the pickled state."""
        self._items = state["items"]
        self._iterator = itertools.cycle(self._items)

    def get(self, cnt: Optional[int] = None) -> Union[int, list[int]]:
        if cnt is None:
            return next(self._iterator)
        else:
            output = []
            for _ in range(cnt):
                output.append(next(self._iterator))
            return output

    def __repr__(self) -> str:
        return f"CyclicalContainer(items={self._items})"

    def __str__(self) -> str:
        return f"Cycles through: {self._items}"

    def __len__(self) -> int:
        return len(self._items)

    def items(self) -> tuple[int]:
        return self._items


@frozen
class SystemPath:
    name: Path = field(converter=Path, default="")

    def __str__(self) -> str:
        return str(self.name)


@define
class DirHandle:
    dir_path: Path = field(converter=Path)
    name: str = field(init=False)
    make: bool = field(kw_only=True, default=False)
    force: bool = field(kw_only=True, default=False)
    replace: bool = field(kw_only=True, default=False)

    # noinspection PyUnusedLocal
    @dir_path.validator  # type: ignore
    def file_exists(self, attribute, value: Path):  # type: ignore
        if not self.make and not value.is_dir():
            raise FileNotFoundError(f"Directory: {value} doesn't exist.")

    def __attrs_post_init__(self):
        self.name = self.dir_path.name
        if self.make:
            try:
                self.dir_path.mkdir()
            except FileExistsError as e_dir_exists:
                if self.force:
                    # Add a numbered prefix to the directory name to avoid conflict.
                    for i in range(1, 100):
                        self.dir_path = Path.joinpath(self.dir_path.parent, str(i) + "-" + self.name)
                        try:
                            Path(self.dir_path).mkdir()
                        except FileExistsError:
                            continue
                        else:
                            self.name = self.dir_path.name
                            break
                    else:
                        print(f"[1:99]-{self.dir_path.name} exist. Can't mkdir.")
                        raise FileExistsError
                elif self.replace:
                    # Delete the conflicting directory.
                    sh.rmtree(self.dir_path)
                    self.dir_path.mkdir()
                    print(f"Replaced dir: {self.dir_path}")
                else:
                    raise e_dir_exists

    def __getstate__(self):
        """Return state for pickling, avoiding filesystem operations on unpickle."""
        return asdict(self)

    def __setstate__(self, state):
        """Restore state from pickle, bypassing __attrs_post_init__."""
        for key, value in state.items():
            super().__setattr__(key, value)

    def __str__(self) -> str:
        return str(self.dir_path)

    def __fspath__(self) -> str:
        return self.__str__()

    def __truediv__(self, key) -> Union[FileHandle, "DirHandle"]:
        """__truediv__ analog to Path's __truediv__ function, but it also checks the
        existence of the resulting path, whether if its file or dir. Use Path(*args...)
        if you don't want this behaviour

        Raises:
            FileNotFoundError: _description_

        Returns:
            _type_: _description_
        """
        new_path = self.dir_path / key
        if new_path.is_file():
            return FileHandle(new_path)
        elif new_path.is_dir():
            return DirHandle(new_path, make=False)
        else:
            raise FileNotFoundError(f"{new_path} doesn't exist.")


dirpath_t: TypeAlias = Union[str, Path, DirHandle]


def update_header(file_obj: FileHandle, new_header: str):
    """
    Update the header of a file.

    This function reads the content of the file, replaces the first line with the new header,
    and writes the updated content back to the file.

    Parameters
    ----------
    file_obj : FileHandle
        The file object whose header needs to be updated.
    new_header : str
        The new header to replace the first line of the file.
    """
    with open(file_obj.path, "r") as file:
        texto = file.readlines()
    texto[0] = new_header
    with open(file_obj.path, "w") as file:
        [file.write(linea) for linea in texto]


def catenate(out_path: Path, *file_objs: FileHandle, newline_between_files: bool = True):
    lineas = []
    for file_obj in file_objs:
        with open(file_obj.path, "r") as file:
            lineas.append(file.readlines())
        if newline_between_files:
            lineas.append(["\n"])

    texto = itertools.chain.from_iterable(lineas)
    with open(out_path, "w") as file:
        [file.write(linea) for linea in texto]
    return FileHandle(out_path)


def catenate_pdbs(out_path: Path, *file_objs: FileHandle):
    lineas = []
    for file_obj in file_objs:
        with open(file_obj.path, "r") as file:
            lineas.append(file.readlines())
    texto = itertools.chain.from_iterable(lineas)
    with open(out_path, "w") as file:
        [file.write(linea) for linea in texto if linea[0:3] != "END"]
        file.write("END")
    return FileHandle(out_path)


# noinspection PyUnusedLocal
@singledispatch
def copy_to(obj, dir_path: Union[Path, DirHandle], name=None):  # type: ignore
    raise NotImplementedError


@copy_to.register
def _(obj: FileHandle, dir_path: Union[Path, DirHandle], name=None):
    if name is None:
        name = obj.path.name
    new_file = Path(dir_path) / name
    sh.copy(obj.path, new_file)
    return FileHandle(new_file)


def find_word_and_get_line(filepath: Union[Path, str], word: str):
    """
    Finds a word in a file using memory mapping and returns the full lines
    containing the word.
    """
    word_b = word.encode()  # Encode the word to bytes for searching in mmap
    lines_found = []

    with open(filepath, mode="rb") as file:
        with mmap.mmap(file.fileno(), length=0, access=mmap.ACCESS_READ) as mm:
            for match in re.finditer(word_b, mm):  # Use re.finditer to find all occurrences
                start = match.start()
                end = match.end()

                # Find the start of the line (go back until newline or start of file)
                line_start = mm.rfind(b"\n", 0, start) + 1  # +1 to move past the newline
                if line_start == -1:
                    line_start = 0  # Handle case where match is on the first line

                # Find the end of the line and then get the next line as well.
                line_end = mm.find(b"\n", end)
                line_end = mm.find(b"\n", line_end + 1)
                if line_end == -1:
                    line_end = mm.size()  # Handle case where match is on the last line

                # Extract and decode the line
                line = mm[line_start:line_end].decode("utf-8")  # Adjust decoding if needed
                lines_found.append(line.strip())

    return lines_found


def convert_to_refname(filepath: filepath_t, cwd: Optional[dirpath_t] = None) -> Path:
    # Generate the reference name
    filepath = Path(filepath)
    old_name_chunks = filepath.name.split("_")
    molecule = old_name_chunks[0]
    if molecule.endswith("ref"):
        pass
    else:
        old_name_chunks[0] = f"{molecule}ref"
    new_name = "_".join(old_name_chunks)
    if cwd is None:
        return filepath.with_name(new_name)
    else:
        return Path(cwd, new_name)
