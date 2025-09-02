import shutil
from pathlib import Path
from string import Template
from typing import Any, Optional, Sequence

import numpy as np

from amberflow.artifacts import (
    BaseTopologyFile,
    BaseTrajectoryFile,
    CpptrajData,
    ArtifactContainer,
    ArtifactRegistry,
)
from amberflow.primitives import DEFAULT_RESOURCES_PATH, dirpath_t, filepath_t
from amberflow.worknodes import noderesource, worknodehelper, BaseSingleWorkNode, check_cpp_log

__all__ = (
    "ImageFit",
    "CpptrajDefault",
)


class BaseAnalysis(BaseSingleWorkNode):
    def _run(
        self,
        *args,
        cwd: dirpath_t,
        sysname: str,
        **kwargs,
    ) -> ArtifactContainer:
        raise NotImplementedError


# I can't add @noderesource here! pycharm complains!
class CpptrajAnalysis(BaseAnalysis):
    resources: Optional[dict] = None
    autoimage: str = "autoimage"
    go: str = "go"
    parm: str = "parm"
    rms_first: str = "rms_first"
    rms_reference_out: str = "rms_reference_out"
    strip: str = "strip"
    trajin: str = "trajin"
    trajout: str = "trajout"

    def __init__(
        self,
        wnid: str,
        *args,
        start: Optional[int] = None,
        stop: Optional[int] = None,
        offset: Optional[int] = None,
        **kwargs,
    ) -> None:
        super().__init__(
            wnid=wnid,
            *args,
            **kwargs,
        )
        if not np.all([i is None for i in (start, stop, offset)]):
            if not np.all([i is not None for i in (start, stop, offset)]):
                raise ValueError("If one of start, stop, offset is set, all must be set.")
        self.start = start
        self.stop = stop
        self.offset = offset

    def load_file(self, template_id: str, mapping: Optional[dict] = None) -> str:
        try:
            cpp_template_txt = Template(self.resources[template_id])
        except KeyError:
            err_msg = f"Invalid template {template_id}. Must be one of {self.resources.keys()}"
            raise ValueError(err_msg)

        return cpp_template_txt.substitute(mapping)

    def run_cpptraj(
        self, output_dir: dirpath_t, cpp_script: filepath_t, *, expected: Optional[Sequence[filepath_t]] = None
    ) -> None:
        logcpp = "cpplog"
        self.command.run(
            ["cpptraj", str(cpp_script), "-o", logcpp],
            cwd=output_dir,
            logger=self.node_logger,
            expected=expected,
        )
        check_cpp_log(output_dir / logcpp, node_logger=self.node_logger)

    def _try_and_skip(self, sysname: str, *args, **kwargs) -> bool:
        raise NotImplementedError

    def fill_output_artifacts(
        self,
        sysname: str,
        *args,
        **kwargs,
    ) -> ArtifactContainer:
        raise NotImplementedError


@noderesource(DEFAULT_RESOURCES_PATH / "cpptraj")
@worknodehelper(
    file_exists=True,
    input_artifact_types=(BaseTopologyFile, BaseTrajectoryFile),
    output_artifact_types=(BaseTrajectoryFile, CpptrajData),
    enforce_output_types=False,
)
class ImageFit(CpptrajAnalysis):
    def __init__(
        self,
        wnid: str,
        *args,
        image_mask: str,
        rms_mask: str,
        boxshape: str = "familiar",
        **kwargs,
    ) -> None:
        super().__init__(
            wnid=wnid,
            *args,
            **kwargs,
        )
        self.image_mask = image_mask
        self.rms_mask = rms_mask

        self.boxshape = boxshape

    def _run(
        self,
        *,
        cwd: dirpath_t,
        sysname: str,
        binpath: Optional[filepath_t] = None,
        **kwargs,
    ) -> Any:
        in_top = Path(self.input_artifacts["BaseTopologyFile"])
        in_trj = Path(self.input_artifacts["BaseTrajectoryFile"])

        out_trj = self.work_dir / in_trj.name
        out_top = self.work_dir / in_top.name
        if self._try_and_skip(sysname, out_top=out_top, out_trj=out_trj):
            return self.output_artifacts

        cppscript = self.write_cpp_script(self.work_dir, in_top, in_trj, out_trj)

        super().run_cpptraj(self.work_dir, cppscript, expected=(out_trj,))

        # Copy the topology file to the output directory, for easier worknode chaining

        shutil.copy(in_top, out_top)
        self.output_artifacts = self.fill_output_artifacts(sysname, out_top=out_top, out_trj=out_trj)

        return self.output_artifacts

    def write_cpp_script(
        self,
        cwd: dirpath_t,
        in_top: Path,
        in_trj: Path,
        out_trj: Path,
    ) -> Path:
        """
        Generates a tleap input script based on a template and writes it to a file sitting right next to the input PDB.
        """

        parm = super().load_file(super().parm, {"PARM7": str(in_top)})
        # Only check start, since the input was already validated in the __init__()
        if self.start is None:
            trajin = super().load_file(super().trajin, {"NC": str(in_trj), "START": "", "STOP": "", "OFFSET": ""})
        else:
            trajin = super().load_file(
                super().trajin, {"NC": str(in_trj), "START": self.start, "STOP": self.stop, "OFFSET": self.offset}
            )
        autoimage = super().load_file(super().autoimage, {"MASK": self.image_mask, "TRICLINIC": self.boxshape})
        rms_first = super().load_file(super().rms_first, {"NAME": "", "MASK": self.rms_mask})
        trajout = super().load_file(super().trajout, {"NC": str(out_trj)})
        go = super().load_file(super().go)

        # Join all sections
        cpp_script = "".join([parm, trajin, autoimage, rms_first, trajout, go, "quit\n"])

        # Write away
        output_path = cwd / f"tleap_{self.__class__.__name__}_{in_top.stem}.in"
        with open(output_path, "w") as outfile:
            outfile.write(cpp_script)

        return output_path

    def _fill_output_artifacts(self, sysname: str, *, out_top: filepath_t, out_trj: filepath_t) -> ArtifactContainer:
        return ArtifactContainer(
            sysname,
            (
                ArtifactRegistry.create_instance_by_filename(
                    out_top, tags=self.tags[self.artifact_map["BaseTopologyFile"]]
                ),
                ArtifactRegistry.create_instance_by_filename(
                    out_trj, tags=self.tags[self.artifact_map["BaseTrajectoryFile"]]
                ),
            ),
        )

    def _try_and_skip(self, sysname: str, *, out_top: filepath_t, out_trj: filepath_t) -> bool:
        if self.skippable:
            try:
                self.output_artifacts = self._fill_output_artifacts(sysname, out_top=out_top, out_trj=out_trj)
                self.node_logger.info(f"Skipped {self.id} WorkNode.")
                return True
            except FileNotFoundError as e:
                self.node_logger.info(f"Can't skip {self.id} Got: {e}")
        return False


@noderesource(DEFAULT_RESOURCES_PATH / "cpptraj")
@worknodehelper(
    file_exists=True,
    input_artifact_types=(BaseTopologyFile, BaseTrajectoryFile),
    # optional_artifact_types=(BaseArtifact, ),
    output_artifact_types=(CpptrajData,),
    enforce_output_types=False,
)
class CpptrajDefault(CpptrajAnalysis):
    def __init__(
        self,
        wnid: str,
        *args,
        additional_cpp: list[str],
        out_dat: str,
        **kwargs,
    ) -> None:
        super().__init__(
            wnid=wnid,
            *args,
            **kwargs,
        )
        self.additional_cpp = additional_cpp
        self.out_dat = out_dat

    def _run(
        self,
        *,
        cwd: dirpath_t,
        sysname: str,
        binpath: Optional[filepath_t] = None,
        **kwargs,
    ) -> Any:
        in_top = Path(self.input_artifacts["BaseTopologyFile"])
        in_trj = Path(self.input_artifacts["BaseTrajectoryFile"])
        cppscript = self.write_cpp_script(self.work_dir, in_top, in_trj)

        super().run_cpptraj(self.work_dir, cppscript, expected=(self.work_dir / self.out_dat,))

        # Copy the topology file to the output directory, for easier worknode chaining
        out_top = self.work_dir / in_top.name
        shutil.copy(in_top, out_top)
        self.output_artifacts = self._fill_output_artifacts(out_top, sysname)

        return self.output_artifacts

    def write_cpp_script(
        self,
        cwd: dirpath_t,
        in_top: Path,
        in_trj: Path,
    ) -> Path:
        """
        Generates a tleap input script based on a template and writes it to a file sitting right next to the input PDB.
        """

        parm = super().load_file(super().parm, {"PARM7": str(in_top)})
        # Only check start, since the input was already validated in the __init__()
        if self.start is None:
            trajin = super().load_file(super().trajin, {"NC": str(in_trj), "START": "", "STOP": "", "OFFSET": ""})
        else:
            trajin = super().load_file(
                super().trajin, {"NC": str(in_trj), "START": self.start, "STOP": self.stop, "OFFSET": self.offset}
            )

        go = super().load_file(super().go)
        # Join all sections
        cpp_script = "".join([parm, trajin, "\n".join(self.additional_cpp), "\n", go, "quit\n"])

        # Write away
        output_path = cwd / f"tleap_{self.__class__.__name__}_{in_top.stem}.in"
        with open(output_path, "w") as outfile:
            outfile.write(cpp_script)

        return output_path

    def _fill_output_artifacts(self, out_top: filepath_t, sysname: str) -> ArtifactContainer:
        return ArtifactContainer(
            sysname,
            (
                ArtifactRegistry.create_instance_by_filename(
                    out_top, tags=self.tags[self.artifact_map["BaseTopologyFile"]]
                ),
                CpptrajData(self.work_dir / self.out_dat),
            ),
        )
