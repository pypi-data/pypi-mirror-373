from logging import Logger
import warnings
from pathlib import Path
from string import Template
from typing import Optional, Union

import MDAnalysis as mda

from amberflow.artifacts import (
    BaseArtifact,
)
from amberflow.primitives import filepath_t, find_word_and_get_line

__all__ = [
    "TleapMixin",
    "AntechamberMixin",
    "runiverse",
    "wuniverse",
    "check_leap_log",
    "check_cpp_log",
]


class TleapMixin:
    resources: Optional[dict] = None
    leaprc: str = "leaprc"
    load_nonstandard: str = "load_nonstandard"
    load_pdb: str = "load_pdb"
    neutralize_ions: str = "neutralize_ions"
    save_amberparm: str = "save_amberparm"
    quit: str = "quit"

    supports = {
        "water": ("opc", "tip3p", "tip4pew", "spce"),
        "force_field": ("14SB", "19SB"),
        "atom_type": ("gaff", "gaff2"),
        "boxshape": ("orthorhombic", "truncated_octahedron"),
    }

    SOLVENT_TO_BOX = {
        "tip3p": "TIP3PBOX",
        "opc": "OPCBOX",
        "tip4pew": "TIP4PEWBOX",
        "spce": "SPCEBOX",
    }

    def check_supported(self, element: str, opt_type: str) -> None:
        try:
            supported_options = self.supports[opt_type]
            if element not in supported_options:
                err_msg = f"Unknown: {element}. Must be one of: {supported_options}"
                raise ValueError(err_msg)
        except KeyError:
            err_msg = f"Unknown option: {opt_type}. Must be one of: {list(self.supports.keys())}"
            raise ValueError(err_msg)

    def load_file(self, template_id: str, mapping: Optional[dict] = None) -> str:
        try:
            tleap_template_txt = Template(self.resources[template_id])
        except KeyError:
            err_msg = f"Invalid template {template_id}. Must be one of {self.resources.keys()}"
            raise ValueError(err_msg)

        return tleap_template_txt.substitute(mapping)

    def load_template(self, template_id: str) -> Template:
        try:
            tleap_template_txt = Template(self.resources[template_id])
        except KeyError:
            err_msg = f"Invalid template {template_id}. Must be one of {self.resources.keys()}"
            raise ValueError(err_msg)

        return tleap_template_txt


class AntechamberMixin:
    supports = {
        "atom_type": ("gaff", "gaff2", "abcg2", "bcc"),
        "charge_model": ("bcc", "abcg2"),
    }

    def check_supported(self, element: str, opt_type: str) -> None:
        try:
            supported_options = self.supports[opt_type]
            if element not in supported_options:
                err_msg = f"Unknown: {element}. Must be one of: {supported_options}"
                raise ValueError(err_msg)
        except KeyError:
            err_msg = f"Unknown option: {opt_type}. Must be one of: {list(self.supports.keys())}"
            raise ValueError(err_msg)


def check_leap_log(leap_log: filepath_t, node_logger: Logger, debug_warn: bool = False) -> None:
    if lines := find_word_and_get_line(leap_log, "Error!"):
        err_msg = f"Error! found in {leap_log}\n{lines}"
        node_logger.error(err_msg)
        raise RuntimeError(err_msg)
    if debug_warn:
        if lines := find_word_and_get_line(leap_log, "Warning!"):
            node_logger.warning(f"Warning! found in {leap_log}\n{lines}")


def check_cpp_log(leap_log: filepath_t, node_logger: Logger, debug_warn: bool = False) -> None:
    if lines := find_word_and_get_line(leap_log, "Error!"):
        err_msg = f"Error! found in {leap_log}\n{lines}"
        node_logger.error(err_msg)
        raise RuntimeError(err_msg)
    if debug_warn:
        if lines := find_word_and_get_line(leap_log, "Warning!"):
            node_logger.warning(f"Warning! found in {leap_log}\n{lines}")


def runiverse(infile: Union[filepath_t, BaseArtifact], to_guess: Optional[tuple] = None) -> mda.Universe:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        if to_guess is None:
            return mda.Universe(Path(infile))
        else:
            return mda.Universe(Path(infile), to_guess=to_guess)


def wuniverse(u: mda.Universe, outfile: filepath_t) -> None:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        u.atoms.write(Path(outfile))
