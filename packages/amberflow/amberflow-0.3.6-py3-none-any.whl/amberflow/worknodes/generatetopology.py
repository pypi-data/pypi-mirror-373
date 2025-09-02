import shutil
from pathlib import Path
from typing import Any, Optional

import numpy as np
from parmed.amber import AmberParm

from amberflow.artifacts import (
    ArtifactContainer,
    BaseBinderStructureFile,
    BaseComplexTopologyFile,
    BaseBinderTopologyFile,
    ArtifactRegistry,
    BaseTargetStructureFile,
    BaseBinderLigandStructureFile,
    BaseTargetTopologyFile,
    BasePeriodicBox,
)
from amberflow.artifacts.structure import BaseComplexStructureFile, BaseTargetStructureReferenceFile
from amberflow.artifacts.topology import LigandLib, LigandFrcmod
from amberflow.primitives import (
    filepath_t,
    dirpath_t,
    DEFAULT_RESOURCES_PATH,
    WorkNodeRunningError,
)
from amberflow.worknodes import (
    noderesource,
    worknodehelper,
    BaseSingleWorkNode,
    TleapMixin,
    check_leap_log,
    TLeapSourcesGenerator,
)

__all__ = ("GenerateTopology",)


# noinspection DuplicatedCode
@noderesource(DEFAULT_RESOURCES_PATH / "tleap")
@worknodehelper(
    file_exists=True,
    input_artifact_types=(
        BaseComplexStructureFile,
        BaseTargetStructureFile,
        BaseBinderStructureFile,
        LigandLib,
        LigandFrcmod,
        BasePeriodicBox,
    ),
    need_all_input_artifacts=False,
    output_artifact_types=(
        BaseComplexStructureFile,
        BaseComplexTopologyFile,
        BaseBinderStructureFile,
        BaseBinderTopologyFile,
        BaseTargetStructureReferenceFile,
        BaseTargetTopologyFile,
    ),
)
class GenerateTopology(BaseSingleWorkNode, TleapMixin):
    """
    GenerateTopologyComplex
    The stages of a tleap script are:
    1. Source leaprc files
    2. Load parameters for non-standard molecules (`loadamberparams`+`loadoff`)
    3. Load the main structure (`loadpdb`)
    4. Add box (with or without solvent molecules)
    5. Neutralize
    6. Output parm7+rst7

    (1), (4) and (5) are set by the user
    (2), (3) and (6) are controlled by the WorkNode
    """

    templates: tuple[str, ...] = (
        "leaprc",
        "load_nonstandard",
        "load_pdb",
        "neutralize_ions",
        "solvateoct",
        "save_amberparm",
        "quit",
    )

    # noinspection PyUnusedLocal
    def __init__(
        self,
        wnid: str,
        *args,
        solvent: str = "opc",
        force_field: str = "19SB",
        atom_type: str = "gaff2",
        box_or_oct: Optional[str] = None,
        neutralize: bool = True,
        buffer: float = 0.0,
        aniso: bool = True,
        closeness: float = 9999.0,
        **kwargs,
    ) -> None:
        super().__init__(
            wnid=wnid,
            *args,
            **kwargs,
        )
        self.sources = TLeapSourcesGenerator(
            force_field=force_field,
            atom_type=atom_type,
            water=solvent,
            ions="jc",
        )
        if box_or_oct is not None:
            if box_or_oct not in ("box", "oct"):
                raise ValueError(f"Invalid box_or_oct value: {box_or_oct}. Must be 'box' or 'oct'.")
        self.box_or_oct = box_or_oct
        self.buffer = buffer
        self.closeness = closeness
        self.neutralize = neutralize

    def _run(
        self,
        *,
        cwd: dirpath_t,
        sysname: str,
        binpath: Optional[filepath_t] = None,
        **kwargs,
    ) -> Any:
        system_type = self.validate()
        if self._try_and_skip(sysname, system_type=system_type):
            return self.output_artifacts

        tleap_script = self.generate_tleap(
            self.input_artifacts,
            self.sources,
            sysname,
            system_type,
            box_or_oct=self.box_or_oct,
            buffer=self.buffer,
            aniso="aniso" if self.box_or_oct == "oct" else "",
            closeness=self.closeness,
            neutralize=self.neutralize,
        )
        # Write tleap script
        tleap_script_fn = self.work_dir / f"tleap_{self.__class__.__name__}_{sysname}.in"
        with open(tleap_script_fn, "w") as outfile:
            outfile.write(tleap_script)

        self.run_tleap(self.work_dir, tleap_script_fn, sysname, system_type)

        self.chbox(self.work_dir, sysname, system_type=system_type, box=self.input_artifacts.get("BasePeriodicBox"))

        self.output_artifacts = self.fill_output_artifacts(sysname, system_type=system_type)

        return self.output_artifacts

    def chbox(
        self, output_dir: dirpath_t, sysname: str, *, system_type: str, box: Optional[BasePeriodicBox] = None
    ) -> Path:
        self.node_logger.info(f"Setting box for {system_type} {sysname} to  {box}")

        # Fix rst7
        rst7 = Path(output_dir, f"{system_type}_{sysname}.rst7")
        prebox_rst7 = Path(output_dir, f"prebox_{system_type}_{sysname}.rst7")
        if box is None:
            shutil.copy(prebox_rst7, rst7)
            self.node_logger.warning(f"No box provided. Copying {prebox_rst7} to: {rst7}")
        else:
            self.command.run(
                ["ChBox", "-c", str(prebox_rst7), "-o", str(rst7), str(box)],
                cwd=output_dir,
                logger=self.node_logger,
                expected=(rst7,),
            )
            self.node_logger.debug(f"Used ChBox to set box {box} in {rst7}")

        # Fix the box in the topology file
        parm7 = Path(output_dir, f"{system_type}_{sysname}.parm7")
        prebox_parm7 = Path(output_dir, f"prebox_{system_type}_{sysname}.parm7")

        if box is None:
            shutil.copy(prebox_parm7, parm7)
            self.node_logger.warning(f"No box provided. Copying {prebox_parm7} to: {parm7}")
        else:
            top = AmberParm(str(prebox_parm7))
            top.box = np.array(list(box))
            top.save(str(parm7), overwrite=True)
            self.node_logger.debug(f"Used parmed to set box {box} in {parm7}")

        return rst7

    def validate(self) -> str:
        """
        Validates the input artifacts
        """
        has_complex = "BaseComplexStructureFile" in self.input_artifacts
        has_frcmod = "LigandFrcmod" in self.input_artifacts
        has_lib = "LigandLib" in self.input_artifacts
        has_target = "BaseTargetStructureFile" in self.input_artifacts
        has_binder = "BaseBinderLigandStructureFile" in self.input_artifacts

        if has_complex and has_frcmod and has_lib:
            return "complex"
        elif has_target and not has_complex:
            return "target"
        elif all([has_binder, has_frcmod, has_lib]) and not (has_complex or has_target):
            return "binder"
        else:
            err_msg = f"""Bad `input_artifacts`. Must be  one of the following:
    - A BaseComplexStructureFile + LigandLib, LigandFrcmod
    - A BinderStructureFile + LigandLib, LigandFrcmod
    - A TargetStructureFile + optional LigandLib, LigandFrcmod
Got: {self.input_artifacts}"""
            self.node_logger.error(err_msg)
            raise ValueError(err_msg)

    @staticmethod
    def generate_tleap(
        input_artifacts: ArtifactContainer,
        sources: TLeapSourcesGenerator,
        sysname: str,
        system_type: str,
        *,
        box_or_oct: Optional[str] = None,
        buffer: float = 0.0,
        closeness: float = 9999.0,
        aniso: str = "",
        neutralize: bool = True,
    ) -> str:
        """
        Generates a tleap input script

        BUG: if you send multiple artifacts of the same type, it will only load the last one.
        I'm in a hurry, so I won't fix it now.
        """
        new_lines: list[str] = []

        # Load nonstandard params first, and respect the priority
        ligand_libs = sorted(
            [
                art
                for art_type, artifacts in input_artifacts.items()
                if issubclass(ArtifactRegistry.name[art_type], LigandLib)
                for art in artifacts
            ],
            key=lambda x: x.priority,
        )
        new_lines.extend([f"loadoff {lib.filepath}" for lib in ligand_libs])

        ligand_frcmods = sorted(
            [
                art
                for art_type, artifacts in input_artifacts.items()
                if issubclass(ArtifactRegistry.name[art_type], LigandFrcmod)
                for art in artifacts
            ],
            key=lambda x: x.priority,
        )
        new_lines.extend([f"loadamberparams {frcmod.filepath}" for frcmod in ligand_frcmods])

        for art_type, artifacts in input_artifacts.items():
            if issubclass(ArtifactRegistry.name[art_type], BaseComplexStructureFile):
                for art in artifacts:
                    new_lines.append(f"mol = loadpdb {art.filepath}")
            elif issubclass(ArtifactRegistry.name[art_type], BaseTargetStructureFile):
                for art in artifacts:
                    new_lines.append(f"mol = loadpdb {art.filepath}")
            elif issubclass(ArtifactRegistry.name[art_type], BaseBinderLigandStructureFile):
                for art in artifacts:
                    new_lines.append(f"mol = loadpdb {art.filepath}")
        if box_or_oct is not None:
            new_lines.append(f"solvate{box_or_oct} mol {sources['box']} {buffer} {aniso} {closeness}")
        if neutralize:
            new_lines.append("addions2 mol Na+ 0")
            new_lines.append("addions2 mol Cl- 0")

        new_lines.append(f"saveamberparm mol prebox_{system_type}_{sysname}.parm7 prebox_{system_type}_{sysname}.rst7")
        return str(sources) + "\n".join(new_lines) + "\nquit\n"

    def run_tleap(self, output_dir: dirpath_t, tleap_script: filepath_t, sysname: str, system_type: str) -> None:
        logleap = "logleap"
        self.command.run(
            ["tleap", "-f", str(tleap_script), ">", logleap],
            cwd=output_dir,
            logger=self.node_logger,
            expected=(
                output_dir / f"prebox_{system_type}_{sysname}.parm7",
                output_dir / f"prebox_{system_type}_{sysname}.rst7",
            ),
        )
        check_leap_log(output_dir / logleap, node_logger=self.node_logger)

    def _try_and_skip(self, sysname: str, *, system_type: str) -> bool:
        if self.skippable:
            try:
                self.output_artifacts = self.fill_output_artifacts(sysname, system_type=system_type)
                self.node_logger.info(f"Skipped {self.id} WorkNode.")
                return True
            except (FileNotFoundError, ValueError) as e:
                self.node_logger.info(f"Can't skip {self.id} Got: {e}")
        return False

    def fill_output_artifacts(self, sysname: str, *, system_type: str) -> ArtifactContainer:
        """
        awful way of doing this.
        """
        if system_type == "complex":
            return ArtifactContainer(
                sysname,
                (
                    ArtifactRegistry.create_instance_by_filename(
                        self.work_dir / f"{system_type}_{sysname}.parm7",
                        tags=self.tags[self.artifact_map["BaseComplexStructureFile"]],
                    ),
                    ArtifactRegistry.create_instance_by_filename(
                        self.work_dir / f"{system_type}_{sysname}.rst7",
                        tags=self.tags[self.artifact_map["BaseComplexStructureFile"]],
                    ),
                ),
            )
        elif system_type == "target":
            return ArtifactContainer(
                sysname,
                (
                    ArtifactRegistry.create_instance_by_filename(
                        self.work_dir / f"{system_type}_{sysname}.parm7",
                        tags=self.tags[self.artifact_map["BaseTargetStructureFile"]],
                    ),
                    ArtifactRegistry.create_instance_by_filename(
                        self.work_dir / f"{system_type}_{sysname}.rst7",
                        tags=self.tags[self.artifact_map["BaseTargetStructureFile"]],
                    ),
                ),
            )
        elif system_type == "binder":
            return ArtifactContainer(
                sysname,
                (
                    ArtifactRegistry.create_instance_by_filename(
                        self.work_dir / f"{system_type}_{sysname}.parm7",
                        tags=self.tags[self.artifact_map["BaseBinderStructureFile"]],
                    ),
                    ArtifactRegistry.create_instance_by_filename(
                        self.work_dir / f"{system_type}_{sysname}.rst7",
                        tags=self.tags[self.artifact_map["BaseBinderStructureFile"]],
                    ),
                ),
            )
        else:
            raise WorkNodeRunningError("The system type is not recognized. This should not happen.")
