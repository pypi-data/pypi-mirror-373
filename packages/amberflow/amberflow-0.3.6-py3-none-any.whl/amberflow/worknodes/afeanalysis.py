import shutil
import xml.etree.ElementTree as ElementTree
from itertools import chain
from pathlib import Path
from typing import Any, Optional, Final, Sequence

import numpy as np
import yaml
from edgembar.amber2dats import extract_traditional_ti, remd_analysis, read_rst_file, read_rem_log

from amberflow.artifacts import (
    BaseMdoutStates,
    BoreschRestraints,
    Remlog,
    EdgeMBARxml,
    BaseDatdir,
    ArtifactContainer,
    EdgeMBARhtml,
    ArtifactRegistry,
    ReferenceDatdir,
    TargetDatdir,
)
from amberflow.primitives import filepath_t, dirpath_t, capture_stdout
from amberflow.worknodes import BaseAnalysis, worknodehelper

__all__ = (
    "Amber2Dats",
    "GetXML",
    "EdgeMBAR",
)


@worknodehelper(
    file_exists=True,
    input_artifact_types=(
        BaseMdoutStates,
        Remlog,
    ),
    optional_artifact_types=(BoreschRestraints,),
    output_artifact_types=(BaseDatdir,),
)
class Amber2Dats(BaseAnalysis):
    """
    TODO: add the `stage` to the name,
    """

    takes_multiple_artifacts = True

    def __init__(
        self,
        wnid: str,
        *args,
        mdin_template: str = "md",
        starting_trial: int = 1,
        nan: Optional[float] = None,
        exclude_untrustworthy_samples: bool = False,
        nmax: int = 10000,
        **kwargs,
    ) -> None:
        super().__init__(
            wnid=wnid,
            *args,
            mdin_template=mdin_template,
            **kwargs,
        )
        self.starting_trial = starting_trial

        self.nan = nan
        self.exclude_untrustworthy_samples = exclude_untrustworthy_samples
        self.nmax = nmax

    def _run(
        self,
        *,
        cwd: dirpath_t,
        sysname: str,
        binpath: Optional[filepath_t] = None,
        **kwargs,
    ) -> Any:
        binder_mdout_states, binder_dat_dirs = self.get_states_and_datdirs("BaseBinderMdoutStates", self.starting_trial)
        complex_mdout_states, complex_dat_dirs = self.get_states_and_datdirs(
            "BaseComplexMdoutStates", self.starting_trial
        )

        if self._try_and_skip(sysname=sysname, binder_dat_dirs=binder_dat_dirs, complex_dat_dirs=complex_dat_dirs):
            return self.output_artifacts

        # noinspection PyTypeChecker
        all_boresch: list[BoreschRestraints] = self.input_artifacts.get_as_list("BoreschRestraints")
        boresch_name = {b.filepath.parent.name: b for b in all_boresch}
        for trial_dir, mdout_set in zip(complex_dat_dirs, complex_mdout_states):
            complex_dirname = mdout_set.filepath.parent.name
            # Restraints
            if complex_dirname in boresch_name:
                boresch_file = Path(boresch_name[complex_dirname])
                with capture_stdout():
                    read_rst_file(boresch_file, str(trial_dir.filepath))
                if trial_dir.try_load_boresch() is None:
                    self.node_logger.warn(f"Failed to load boresch restraints from {boresch_file} Check {trial_dir}")

        # noinspection PyTypeChecker
        all_remlogs: list[Remlog] = self.input_artifacts.get_as_list("Remlog")
        remlog_name = {b.filepath.parent.name: b for b in all_remlogs}
        for trial_dir, mdout_set in zip(complex_dat_dirs + binder_dat_dirs, complex_mdout_states + binder_mdout_states):
            trial_dirname = mdout_set.filepath.parent.name
            # remlog
            try:
                remlog_filepath = Path(remlog_name[trial_dirname])
            except KeyError:
                err_msg = f"{trial_dirname} not found in {remlog_name} - Trial {trial_dir} has remlog?"
                self.node_logger.warn(err_msg)
                raise KeyError(err_msg)
            with capture_stdout():
                reptraj, nstate, nexch, nsucc, acceptance_ratios = read_rem_log(str(remlog_filepath))
                remd_analysis(reptraj, acceptance_ratios, str(trial_dir.filepath))

            # mdouts
            with capture_stdout():
                for mdout in mdout_set.values():
                    extract_traditional_ti(
                        mdout,
                        write=True,
                        odir=str(trial_dir.filepath),
                        skip_bad=self.exclude_untrustworthy_samples,
                        maxsamples=self.nmax,
                        undefene=self.nan,
                    )
        # noinspection PyTypeChecker
        self.output_artifacts = self.fill_output_artifacts(
            sysname=sysname, binder_dat_dirs=binder_dat_dirs, complex_dat_dirs=complex_dat_dirs
        )

        return self.output_artifacts

    def get_states_and_datdirs(
        self,
        mdout_states_type_str: str,
        starting_trial: int,
    ) -> tuple[list[BaseMdoutStates], list[BaseDatdir]]:
        # noinspection PyTypeChecker
        mdout_states: list = self.input_artifacts.get_as_list(mdout_states_type_str)
        dat_dirs = []
        for i, mdout_set in enumerate(mdout_states, starting_trial):
            mdout_states_art_type = ArtifactRegistry.concrete_artifact(BaseDatdir, getattr(mdout_set, "tags"))
            ctctor = getattr(mdout_states_art_type, "from_mdout_states")
            dat_dirs.append(ctctor(self.work_dir, states=mdout_set, trial=i, makedir=True))

        return mdout_states, dat_dirs

    # noinspection DuplicatedCode
    def _try_and_skip(
        self,
        sysname: str,
        *,
        binder_dat_dirs: Sequence[ReferenceDatdir],
        complex_dat_dirs: Sequence[TargetDatdir],
    ) -> bool:
        if self.skippable:
            try:
                self.output_artifacts = self.fill_output_artifacts(
                    sysname=sysname, binder_dat_dirs=binder_dat_dirs, complex_dat_dirs=complex_dat_dirs
                )
                self.node_logger.info(f"Skipped {self.id} WorkNode.")
                return True
            except (FileNotFoundError, ValueError) as e:
                self.node_logger.info(f"Can't skip {self.id} Got: {e}")
        return False

    # noinspection PyMethodMayBeStatic
    def fill_output_artifacts(
        self,
        sysname: str,
        *,
        binder_dat_dirs: Sequence[ReferenceDatdir],
        complex_dat_dirs: Sequence[TargetDatdir],
    ) -> ArtifactContainer:
        for tdir in binder_dat_dirs:
            if not tdir.is_valid():
                raise ValueError(f"{tdir} is not a valid trial dat directory")
        for tdir in complex_dat_dirs:
            if not tdir.is_valid():
                raise ValueError(f"{tdir} is not a valid trial dat directory")
        return ArtifactContainer(sysname, list(binder_dat_dirs) + list(complex_dat_dirs))


@worknodehelper(
    file_exists=True,
    input_artifact_types=(BaseDatdir,),
    output_artifact_types=(EdgeMBARxml,),
)
class GetXML(BaseAnalysis):
    map_to_edgembar: dict[str, str] = {
        "complex": "target",
        "binder": "reference",
    }

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
        binpath: Optional[filepath_t] = None,
        **kwargs,
    ) -> Any:
        xml_path = Path(self.work_dir, f"edge_{sysname}.xml")
        if self._try_and_skip(sysname=sysname, edges_xml=xml_path):
            return self.output_artifacts

        edges = set([getattr(datdir, "edge") for datdir in self.input_artifacts.get_as_list("BaseDatdir")])
        if len(edges) != 1:
            err_msg = f"Can only deal with 1 edge. Got: {edges} "
            self.node_logger.error(err_msg)
            raise ValueError(err_msg)

        root = ElementTree.Element("edge", name=edges.pop())
        # Use dictionaries to keep track of created elements to avoid duplicates
        env_elements: dict[str, ElementTree.Element] = {}
        stage_element: dict[tuple[str, str], ElementTree.Element] = {}
        for dir_list in self.input_artifacts.values():
            for datdir in dir_list:
                self.add_trial(root, datdir, env_elements, stage_element)
        # Create the full XML tree and write it to the file
        tree = ElementTree.ElementTree(root)
        # 'indent' makes the XML human-readable
        ElementTree.indent(tree, space="\t", level=0)
        tree.write(str(xml_path), xml_declaration=True, encoding="utf-8", method="xml")

        self.output_artifacts = self.fill_output_artifacts(sysname=sysname, edges_xml=xml_path)
        return self.output_artifacts

    def add_trial(
        self,
        root: ElementTree.Element,
        datdir: BaseDatdir,
        env_elements: dict[str, ElementTree.Element],
        stage_elements: dict[tuple[str, str], ElementTree.Element],
    ) -> None:
        if datdir.environment not in env_elements:
            env_element = ElementTree.SubElement(root, "env", name=self.map_to_edgembar[datdir.environment])
            env_elements[datdir.environment] = env_element
        else:
            env_element = env_elements[datdir.environment]
        if (datdir.environment, datdir.stage) not in stage_elements:
            stage_element = ElementTree.SubElement(env_element, "stage", name=datdir.stage)
            stage_elements[(datdir.environment, datdir.stage)] = stage_element
        else:
            stage_element = stage_elements[(datdir.environment, datdir.stage)]
        # we don't worry about duplicating trials since 1 DatDir is 1 trial
        trial_element = ElementTree.SubElement(stage_element, "trial", name=datdir.trial)

        # Add the <dir> element
        dir_element = ElementTree.SubElement(trial_element, "dir")
        dir_element.text = str(datdir.filepath)

        # Add the optional <shift> element
        if boresch_fn := getattr(datdir, "boresch_restraints", None):
            shift_element = ElementTree.SubElement(trial_element, "shift")
            shift = self.parse_offset_from_boresch(boresch_fn)
            shift_element.text = f"{shift:.5f}"

        # Add all the <ene> elements
        for window in datdir.states:
            ene_element = ElementTree.SubElement(trial_element, "ene")
            ene_element.text = f"{window:.8f}"

    # noinspection DuplicatedCode
    def _try_and_skip(self, sysname: str, *, edges_xml: Path) -> bool:
        if self.skippable:
            try:
                self.output_artifacts = self.fill_output_artifacts(sysname=sysname, edges_xml=edges_xml)
                self.node_logger.info(f"Skipped {self.id} WorkNode.")
                return True
            except (FileNotFoundError, ValueError) as e:
                self.node_logger.info(f"Can't skip {self.id} Got: {e}")
        return False

    # noinspection PyPep8Naming
    @staticmethod
    def parse_offset_from_boresch(boresch_fn: filepath_t) -> float:
        kb: Final[float] = 0.0019872  # kcal/(mol*K)
        T: Final[float] = 298.0  # K
        V0: Final[float] = 1660.0  # Angstroms^3 - Standard State volume for 1M

        k_rst = []
        eq0_rst = []
        with open(boresch_fn, "r") as fh:
            # noinspection PyUnresolvedReferences
            data = yaml.safe_load(fh)
            if "Angle" in data:
                angle_data = data["Angle"]
                # Flatten r2 and process every number
                if "r2" in angle_data:
                    r2_flat = list(chain.from_iterable(angle_data["r2"]))
                    for val in r2_flat:
                        num = float(val)
                        eq0_rst.append(np.sin(num * np.pi / 180.0))
                # Flatten rk2 and process every number
                if "rk2" in angle_data:
                    rk2_flat = list(chain.from_iterable(angle_data["rk2"]))
                    for val in rk2_flat:
                        num = float(val)
                        k_rst.append(num)
            if "Bond" in data:
                bond_data = data["Bond"]
                if "r2" in bond_data:
                    r2_flat = list(chain.from_iterable(bond_data["r2"]))
                    for val in r2_flat:
                        num = float(val)
                        eq0_rst.append(num**2)
                if "rk2" in bond_data:
                    rk2_flat = list(chain.from_iterable(bond_data["rk2"]))
                    for val in rk2_flat:
                        num = float(val)
                        k_rst.append(num)
            if dihedral_data := data["Dihedral"]:
                # For Dihedral, only rk2 is used (Jacobian doesn't take theta angle into account. The volume is the same across all theta angles)
                if "rk2" in dihedral_data:
                    rk2_flat = list(chain.from_iterable(dihedral_data["rk2"]))
                    for val in rk2_flat:
                        num = float(val)
                        k_rst.append(num)
            if len(k_rst) == 0:
                raise RuntimeError(f"Could not parse Boresch restraints from: {boresch_fn}")
            kk = np.prod(k_rst)
            rr = np.prod(eq0_rst)

            # noinspection PyTypeChecker
            dAr = -kb * T * np.log(((8 * np.pi**2 * V0) / rr) * ((kk**0.5) / ((np.pi * kb * T) ** 3)))
        return dAr

    @staticmethod
    def fill_output_artifacts(
        sysname: str,
        *,
        edges_xml: Path,
    ) -> ArtifactContainer:
        return ArtifactContainer(sysname, (EdgeMBARxml(edges_xml),))


@worknodehelper(
    file_exists=True,
    input_artifact_types=(EdgeMBARxml,),
    output_artifact_types=(EdgeMBARhtml,),
)
class EdgeMBAR(BaseAnalysis):
    min_cores: int = 1
    supported_modes: tuple[str] = (
        "AUTO",
        "MBAR",
        "MBAREXP0",
        "MBAREXP1",
        "MBAREXP",
        "BAR",
        "BAREXP0",
        "BAREXP1",
        "BAREXP",
    )

    def __init__(
        self,
        wnid: str,
        *args,
        threads: int = 1,
        temp: float = 298.0,
        tol: float = 1e-13,
        btol: float = 1e-07,
        ptol: float = 0.05,
        nboot: int = 20,
        verbosity: int = 0,
        ncon: float = 2,
        dcon: float = 2.0,
        ntimes: int = 4,
        fstart: float = 0.0,
        fstop: float = 1.0,
        fmaxeq: float = 0.5,
        ferreq: float = -1.0,
        stride: int = 1,
        mode: str = "AUTO",
        halves: bool = True,
        fwdrev: bool = True,
        **kwargs,
    ) -> None:
        super().__init__(
            wnid=wnid,
            *args,
            **kwargs,
        )
        self.min_cores = threads
        self.binary = "edgembar" if threads == 1 else f"OMP_NUM_THREADS={threads} edgembar_omp"
        self.temp = temp
        self.tol = tol
        self.btol = btol
        self.ptol = ptol
        self.nboot = nboot
        self.verbosity = verbosity
        self.ncon = ncon
        self.dcon = dcon
        self.ntimes = ntimes
        self.fstart = fstart
        self.fstop = fstop
        self.fmaxeq = fmaxeq
        self.ferreq = ferreq
        self.stride = stride
        self.halves = halves
        self.fwdrev = fwdrev
        if mode not in self.supported_modes:
            raise ValueError(f"Unsupported mode '{mode}'. Supported modes: {self.supported_modes}")
        self.mode = mode

    def _run(
        self,
        *,
        cwd: dirpath_t,
        sysname: str,
        binpath: Optional[filepath_t] = None,
        **kwargs,
    ) -> Any:
        in_xml = Path(self.input_artifacts["EdgeMBARxml"])
        out_html = Path(self.work_dir, in_xml.stem + ".html")
        if self._try_and_skip(sysname=sysname, out_html=out_html):
            return self.output_artifacts

        here_xml = self.work_dir / in_xml.name
        shutil.copy(in_xml, here_xml)

        out_py = self.work_dir / in_xml.with_suffix(".py").name

        # use relative paths for the command line
        cmd_line = [
            self.binary,
            f"--temp {self.temp}",
            f"--tol {self.tol}",
            f"--btol {self.btol}",
            f"--ptol {self.ptol}",
            f"--nboot {self.nboot}",
            f"--verbosity {self.verbosity}",
            f"--ncon {self.ncon}",
            f"--dcon {self.dcon}",
            f"--ntimes {self.ntimes}",
            f"--fstart {self.fstart}",
            f"--fstop {self.fstop}",
            f"--fmaxeq {self.fmaxeq}",
            f"--ferreq {self.ferreq}",
            f"--stride {self.stride}",
            f"--mode {self.mode}",
            f"{in_xml.name}",
        ]
        if self.halves:
            cmd_line.append("--halves")
        if self.fwdrev:
            cmd_line.append("--fwdrev")
        self.command.run(
            cmd_line,
            cwd=self.work_dir,
            logger=self.node_logger,
            expected=(out_py,),
        )

        out_html = out_py.with_suffix(".html")
        self.command.run(
            ["python", str(out_py)],
            cwd=self.work_dir,
            logger=self.node_logger,
            expected=(out_html,),
        )

        self.output_artifacts = self.fill_output_artifacts(sysname=sysname, out_html=out_html)
        return self.output_artifacts

    # noinspection DuplicatedCode
    def _try_and_skip(self, sysname: str, *, out_html: Path) -> bool:
        if self.skippable:
            try:
                self.output_artifacts = self.fill_output_artifacts(sysname=sysname, out_html=out_html)
                self.node_logger.info(f"Skipped {self.id} WorkNode.")
                return True
            except (FileNotFoundError, ValueError) as e:
                self.node_logger.info(f"Can't skip {self.id} Got: {e}")
        return False

    @staticmethod
    def fill_output_artifacts(
        sysname: str,
        *,
        out_html: Path,
    ) -> ArtifactContainer:
        return ArtifactContainer(sysname, (EdgeMBARhtml(out_html),))
