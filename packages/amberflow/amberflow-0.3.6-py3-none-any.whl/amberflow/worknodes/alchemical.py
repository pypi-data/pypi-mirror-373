import shutil
from pathlib import Path
from typing import Optional, Sequence, Any, Literal

import numpy as np
from numpy.typing import NDArray
from scipy.interpolate import interp1d

from amberflow.artifacts import (
    BaseStructureFile,
    BaseTopologyFile,
    BaseMdoutMD,
    BaseRestartStatesFile,
    BoreschRestraints,
    LambdaSchedule,
    BaseArtifact,
    ArtifactContainer,
    ArtifactRegistry,
    BaseStructureReferenceFile,
    LambdaScheduleFile,
    Groupfile,
    BaseMdoutStates,
    Remlog,
    BaseTrajectoryStatesFile,
)
from amberflow.primitives import (
    filepath_t,
    dirpath_t,
    DEFAULT_RESOURCES_PATH,
    BadMDout,
    convert_to_refname,
)
from amberflow.worknodes import worknodehelper, BaseMDWorkNode, noderesource, BaseSingleWorkNode

__all__ = (
    "BaseLambdaMDWorkNode",
    "LambdaAnhilation",
    "LambdaMDRun",
    "QuickLambdaSchedule",
)


class BaseLambdaMDWorkNode(BaseMDWorkNode):
    """
    Base class for work nodes that run MD simulations with a lambda schedule.
    """

    def __init__(
        self,
        wnid: str,
        *args,
        engine: str = "pmemd.cuda.MPI",
        **kwargs,
    ) -> None:
        super().__init__(
            wnid=wnid,
            *args,
            engine=engine,
            **kwargs,
        )

    def _try_and_skip(
        self,
        *,
        out_top: Path,
        out_first_rst7: Path,
        out_first_mdout: Path,
        out_first_nc: Path,
        schdl: LambdaSchedule,
        states_tags: tuple[str, ...],
        sysname: str,
        remlog: Optional[Path] = None,
        out_boresch: Optional[Path] = None,
        lambda_sch: Optional[Path] = None,
        ref_rst7: Optional[Path] = None,
    ) -> bool:
        if self.skippable:
            try:
                self.output_artifacts = self.fill_output_artifacts(
                    out_top=out_top,
                    out_first_rst7=out_first_rst7,
                    out_first_mdout=out_first_mdout,
                    out_first_nc=out_first_nc,
                    schdl=schdl,
                    states_tags=states_tags,
                    sysname=sysname,
                    remlog=remlog,
                    out_boresch=out_boresch,
                    lambda_sch=lambda_sch,
                    ref_rst7=ref_rst7,
                )
                self.node_logger.info(f"Skipped {self.id} WorkNode.")
                return True
            except (FileNotFoundError, ValueError) as e:
                self.node_logger.info(f"Can't skip {self.id} Got: {e}")
            except BadMDout:
                self.node_logger.info(f"Can't skip {self.id}. Bad mdout file")
        return False

    # noinspection PyUnusedLocal
    def fill_output_artifacts(
        self,
        *args,
        out_top: Path,
        out_first_rst7: Path,
        out_first_mdout: Path,
        out_first_nc: Path,
        schdl: LambdaSchedule,
        states_tags: tuple[str, ...],
        sysname: str,
        remlog: Optional[Path] = None,
        out_boresch: Optional[Path] = None,
        lambda_sch: Optional[Path] = None,
        ref_rst7: Optional[Path] = None,
        **kwargs,
    ) -> ArtifactContainer:
        rst7_states = ArtifactRegistry.create_instance_by_filename(out_first_rst7, tags=states_tags)
        mdout_states = ArtifactRegistry.create_instance_by_filename(out_first_mdout, tags=states_tags)
        if not len(rst7_states) == len(mdout_states) == len(schdl):
            raise ValueError(
                f"Expected {len(schdl)} states but found {len(mdout_states)} mdout and {len(rst7_states)} rst7 files "
            )
        artifacts = [
            self.artifact_builder["BaseTopologyFile"](out_top),
            rst7_states,
            mdout_states,
            schdl,
        ]
        if out_first_nc is not None:
            try:
                traj_states = ArtifactRegistry.create_instance_by_filename(out_first_nc, tags=states_tags)
                artifacts.append(traj_states)
            except FileNotFoundError:
                # No trajectory written
                pass
        if out_boresch is not None:
            artifacts.append(BoreschRestraints(out_boresch))
        if remlog is not None:
            artifacts.append(Remlog(remlog))
        if lambda_sch is not None:
            artifacts.append(self.artifact_builder["LambdaScheduleFile"](lambda_sch))
        if ref_rst7 is not None:
            artifacts.append(self.artifact_builder["BaseStructureReferenceFile"](ref_rst7))

        return ArtifactContainer(sysname, artifacts)

    def write_mdin(self, output_dir: dirpath_t, sysname: str, clambda: float) -> Path:
        if self.mdin is None:
            err_msg = "Bad MDWorkNode. '.mdin' contents were not generated."
            raise FileNotFoundError(err_msg)
        output_path = output_dir / f"{self.__class__.__name__}_{clambda}.mdin"
        with open(output_path, "w") as outfile:
            outfile.write(f"{sysname} - {self.id}\n")
            outfile.write(self.mdin)

        return output_path

    def _run_md_groupfile(
        self,
        *,
        cwd: dirpath_t,
        sysname: str,
        ngroups: int,
        groupfile: Path,
        gpus: tuple[int] = (1,),
        windows_rst7: tuple[Path, ...],
        windows_mdouts: tuple[Path, ...],
        remlog: Optional[Path] = None,
        sbatch_params: Optional[dict[str, Any]] = None,
    ) -> None:
        if remlog is None:
            cmd_line = [
                self.engine,
                f"-ng {ngroups}",
                f"-groupfile {groupfile.name}",
            ]
        else:
            cmd_line = [
                self.engine,
                f"-ng {ngroups}",
                f"-groupfile {groupfile.name}",
                "-rem 3",
                f"-remlog {remlog.name}",
            ]

        if sbatch_params is not None:
            sbatch_params.setdefault("job-name", f"{self.id}_{sysname}")
            sbatch_params.setdefault("output", f"{self.id}_{sysname}.slurmout")

        self.command.run(
            cmd_line,
            cwd=cwd,
            logger=self.node_logger,
            expected=windows_mdouts + windows_rst7,
            add_to_env=self.get_cuda_visible_devices(gpus),
            sbatch_params=sbatch_params,
        )

        for mdout in windows_mdouts:
            self.check_mdout(mdout, self.node_logger)

    def _run(
        self,
        *,
        cwd: dirpath_t,
        sysname: str,
        binpath: Optional[filepath_t] = None,
        gpus: tuple[int] = (1,),
        **kwargs,
    ) -> Any:
        raise NotImplementedError


@noderesource(DEFAULT_RESOURCES_PATH / "mdin")
@worknodehelper(
    file_exists=True,
    input_artifact_types=(BaseStructureFile, BaseTopologyFile, LambdaSchedule),
    optional_artifact_types=(BoreschRestraints,),
    output_artifact_types=(
        BaseStructureFile,
        BaseTopologyFile,
        BaseRestartStatesFile,
        BaseStructureReferenceFile,
        BaseTrajectoryStatesFile,
        BaseMdoutStates,
        LambdaSchedule,
        BaseMdoutMD,
        BoreschRestraints,
    ),
)
class LambdaAnhilation(BaseLambdaMDWorkNode):
    def __init__(
        self,
        wnid: str,
        *args,
        engine: str = "pmemd.cuda",
        mdin_template: str = "min_icfe",
        **kwargs,
    ) -> None:
        super().__init__(
            wnid=wnid,
            *args,
            mdin_template=mdin_template,
            engine=engine,
            **kwargs,
        )

    # noinspection DuplicatedCode
    def _run(
        self,
        *,
        cwd: dirpath_t,
        sysname: str,
        binpath: Optional[filepath_t] = None,
        gpus: tuple[int] = (1,),
        sbatch_params: Optional[dict[str, Any]] = None,
        **kwargs,
    ) -> Any:
        top_typename = type(self.input_artifacts["BaseTopologyFile"]).__name__
        prefix = self.prefix[top_typename]
        in_rst7 = Path(self.input_artifacts["BaseStructureFile"])
        in_top = Path(self.input_artifacts["BaseTopologyFile"])
        parm7 = self.work_dir / in_top.name
        schdl = self.input_artifacts["LambdaSchedule"]
        first_endpoint_rst7 = self.work_dir / f"{prefix}_{sysname}_{schdl.get_formatted(0)}.rst7"
        first_mdout = self.work_dir / f"{prefix}_{sysname}_{schdl.get_formatted(0)}.mdout"
        first_nc = self.work_dir / f"{prefix}_{sysname}_{schdl.get_formatted(0)}.nc"
        out_boresch = (
            self.work_dir / Path(self.input_artifacts["BoreschRestraints"]).name
            if "BoreschRestraints" in self.input_artifacts
            else None
        )

        if super()._try_and_skip(
            out_top=parm7,
            out_first_rst7=first_endpoint_rst7,
            out_first_mdout=first_mdout,
            out_first_nc=first_nc,
            schdl=schdl,
            states_tags=self.tags[self.artifact_map["BaseStructureFile"]] + ("alchemical",),
            sysname=sysname,
            out_boresch=out_boresch,
        ):
            return self.output_artifacts

        # Copy the parm7 file to the output dir. We'll add it to the output for easier chaining of MDWorkNodes.
        shutil.copy(Path(self.input_artifacts["BaseTopologyFile"]), parm7)

        # Add the Boresch restraints, if provided
        try:
            in_boresch = Path(self.input_artifacts["BoreschRestraints"])
            restraints_name = in_boresch.name
            out_boresch = Path(self.work_dir, restraints_name)
            shutil.copy(in_boresch, out_boresch)
            # We copy the restraints file to the work_dir, so that it can be used in the mdin file with a relative path.
            mdparameters = self.mdparameters.as_dict() | {"REST": restraints_name}
        except KeyError:
            out_boresch = None
            mdparameters = self.mdparameters.as_dict()

        windows_rst7: list[Path] = []
        windows_mdouts: list[Path] = []
        for clambda in schdl.formatted():
            self.mdin = super().load_file(
                self.resources, self.mdin_template, mapping=mdparameters | {"CLAMBDA": clambda}
            )
            mdin_file = super().write_mdin(self.work_dir, sysname, clambda)
            r, x, o = super()._run_md(
                cwd=self.work_dir,
                sysname=sysname,
                i=mdin_file,
                c=in_rst7,
                p=parm7,
                ref=in_rst7,
                output_name_template=f"{prefix}_{sysname}_{clambda}",
                gpus=gpus,
                sbatch_params=sbatch_params,
            )
            in_rst7 = r
            windows_rst7.append(r)
            windows_mdouts.append(o)

        self.output_artifacts = super().fill_output_artifacts(
            self.work_dir,
            out_top=parm7,
            out_first_rst7=windows_rst7[0],
            out_first_mdout=windows_mdouts[0],
            out_first_nc=first_nc,
            schdl=schdl,
            states_tags=self.tags[self.artifact_map["BaseStructureFile"]] + ("alchemical",),
            sysname=sysname,
            out_boresch=out_boresch,
        )

        return self.output_artifacts

    def _try_and_skip(
        self,
        *args,
        out_top: Path,
        out_first_rst7: Path,
        out_first_mdout: Path,
        out_first_nc: Path,
        schdl: LambdaSchedule,
        states_tags: tuple[str, ...],
        sysname: str,
        remlog: Optional[Path] = None,
        out_boresch: Optional[Path] = None,
        **kwargs,
    ) -> bool:
        if self.skippable:
            try:
                self.output_artifacts = self.fill_output_artifacts(
                    self.work_dir,
                    out_top=out_top,
                    out_first_rst7=out_first_rst7,
                    out_first_mdout=out_first_mdout,
                    out_first_nc=out_first_nc,
                    schdl=schdl,
                    states_tags=states_tags,
                    sysname=sysname,
                    out_boresch=out_boresch,
                )
                self.node_logger.info(f"Skipped {self.id} WorkNode.")
                return True
            except (FileNotFoundError, ValueError) as e:
                self.node_logger.info(f"Can't skip {self.id} Got: {e}")
        return False


@noderesource(DEFAULT_RESOURCES_PATH / "mdin")
@worknodehelper(
    file_exists=True,
    input_artifact_types=(BaseTopologyFile, BaseRestartStatesFile, LambdaSchedule),
    optional_artifact_types=(BoreschRestraints, LambdaScheduleFile, BaseStructureReferenceFile),
    output_artifact_types=(
        BaseStructureFile,
        BaseTopologyFile,
        BaseRestartStatesFile,
        BaseTrajectoryStatesFile,
        BaseMdoutStates,
        LambdaSchedule,
        LambdaScheduleFile,
        BoreschRestraints,
        Remlog,
        BaseStructureReferenceFile,
    ),
)
class LambdaMDRun(BaseLambdaMDWorkNode):
    def __init__(
        self,
        wnid: str,
        *args,
        mdin_template: str = "min_icfe_restrained",
        exchange: bool = False,
        ifmbar: bool = False,
        # Don't allow more than one `max_systems` to be run in parallel, even if there are available resources.
        max_systems: int = 1,
        **kwargs,
    ) -> None:
        super().__init__(
            wnid=wnid,
            *args,
            mdin_template=mdin_template,
            max_systems=max_systems,
            **kwargs,
        )

        if not self.engine.endswith("MPI"):
            raise ValueError(
                f"Engine {self.engine} is not supported for alchemical MD simulations. Use an MPI-enabled version of pmemd."
            )
        self.exchange = exchange
        self.ifmbar = ifmbar

    # noinspection DuplicatedCode
    def _run(
        self,
        *,
        cwd: dirpath_t,
        sysname: str,
        binpath: Optional[filepath_t] = None,
        cores: Optional[int] = None,
        gpus: tuple[int] = (1,),
        restraints_file: Optional[filepath_t] = None,
        sbatch_params: Optional[dict[str, Any]] = None,
        **kwargs,
    ) -> Any:
        # Initialize the paths to the output artifacts
        in_top = Path(self.input_artifacts["BaseTopologyFile"])
        parm7 = self.work_dir / in_top.name
        schdl = self.input_artifacts["LambdaSchedule"]
        prefix = self.prefix[self.artifact_map["BaseTopologyFile"]]
        first_endpoint_rst7 = self.work_dir / f"{prefix}_{sysname}_{schdl.get_formatted(0)}.rst7"
        first_mdout = self.work_dir / f"{prefix}_{sysname}_{schdl.get_formatted(0)}.mdout"
        first_nc = self.work_dir / f"{prefix}_{sysname}_{schdl.get_formatted(0)}.nc"
        out_boresch = (
            self.work_dir / Path(self.input_artifacts["BoreschRestraints"]).name
            if "BoreschRestraints" in self.input_artifacts
            else None
        )
        remlog = self.work_dir / f"remd_{sysname}.log" if self.exchange else None
        lambda_sch = (
            self.work_dir / Path(self.input_artifacts["LambdaScheduleFile"]).name
            if "LambdaScheduleFile" in self.input_artifacts
            else None
        )
        ref = super()._setup_reference()
        ref_passed_in = False if ref is None else True
        if super()._try_and_skip(
            out_top=parm7,
            out_first_rst7=first_endpoint_rst7,
            out_first_mdout=first_mdout,
            out_first_nc=first_nc,
            schdl=schdl,
            states_tags=self.tags[self.artifact_map["BaseRestartStatesFile"]],
            sysname=sysname,
            out_boresch=out_boresch,
            remlog=remlog,
            lambda_sch=lambda_sch,
            ref_rst7=Path(self.work_dir, ref) if ref_passed_in else None,
        ):
            return self.output_artifacts

        # Couldn't skip, run the work node
        in_states_rst7 = self.input_artifacts["BaseRestartStatesFile"]
        if len(schdl) != len(in_states_rst7):
            raise ValueError(
                f"Expected {len(schdl)} states in {in_states_rst7.parent}, but found {len(in_states_rst7)}. "
            )
        # Copy the topology file to the work_dir. We'll add it to the output for easier chaining of MDWorkNodes.
        shutil.copy(in_top, parm7)

        # Add the Boresch restraints, if provided
        if out_boresch is not None:
            in_boresch = Path(self.input_artifacts["BoreschRestraints"])
            # We copy the restraints file to the work_dir, so that it can be used in the mdin file with a relative path.
            shutil.copy(in_boresch, out_boresch)
            mdparameters = self.mdparameters.as_dict() | {"REST": in_boresch.name}
        else:
            out_boresch = None
            mdparameters = self.mdparameters.as_dict()

        # # If a reference structure was passed in, copy it to the working dir
        # ref_rst7 = self.input_artifacts.get("BaseStructureReferenceFile")
        # if ref_rst7 is None:
        #     ref = None
        # else:
        #     ref_rst7_filepath = Path(ref_rst7.filepath)
        #     ref = f"ref_{ref_rst7_filepath.name}"
        #     shutil.copy(ref_rst7_filepath, self.work_dir / ref)
        #     self.node_logger.info(f"Using reference rst7 {ref_rst7_filepath} ")

        windows_mdouts: list[Path] = []
        windows_rst7: list[Path] = []
        groupfile_lines: list[str] = []
        first_iteration = True
        for clambda, state_rst7 in zip(schdl.formatted(), in_states_rst7.values()):
            # First, write the mdin file for the current lambda state.
            self.mdin = super().load_file(
                self.resources,
                self.mdin_template,
                mapping=mdparameters | {"CLAMBDA": clambda} | {"NLAMBDA": len(schdl)},
            )
            if self.ifmbar:
                mdin_chunks = self.mdin.split("/")
                mbar_lambdas = [f"mbar_lambda({i}) = {lam}" for i, lam in enumerate(schdl.formatted(), 1)]
                mdin_chunks[0] = mdin_chunks[0] + "\n".join(mbar_lambdas)
                self.mdin = "\n/".join(mdin_chunks)

            mdin_file = super().write_mdin(self.work_dir, sysname, clambda)

            # Then, copy the input rst7 file for the current lambda state to the work_dir so that it can be used\
            # in the group file with a relative path.
            output_name_template = f"{prefix}_{sysname}_{clambda}"
            in_rst7_name = "in_" + output_name_template + state_rst7.suffix
            in_rst7_filepath = self.work_dir / in_rst7_name
            shutil.copy(state_rst7, in_rst7_filepath)
            if first_iteration:
                first_iteration = False
                # If the reference rst7 file is provided, use it. Otherwise, use the input rst7 file for the first state.
                if not ref_passed_in:
                    ref_rst7_filepath = convert_to_refname(state_rst7, self.work_dir)
                    shutil.copy(state_rst7, ref_rst7_filepath)
                    ref = ref_rst7_filepath.name

            # Collect the outputs for each lambda state for later checking.
            windows_mdouts.append(self.work_dir / f"{output_name_template}.mdout")
            windows_rst7.append(self.work_dir / f"{output_name_template}.rst7")

            # Finally, append the group line to the groupfile_lines.
            group_line = f"-O -p {parm7.name} -c {in_rst7_name} -i {mdin_file.name} -o {output_name_template}.mdout -r {output_name_template}.rst7 -x {output_name_template}.nc -ref {ref}"
            groupfile_lines.append(group_line)

        if lambda_sch is not None:
            shutil.copy(Path(self.input_artifacts["LambdaScheduleFile"]), lambda_sch)
            groupfile_lines = [line + f" -lambda_sch {lambda_sch.name}" for line in groupfile_lines]
        groupfile = Groupfile.from_lines(self.work_dir / f"{sysname}.groupfile", groupfile_lines)

        # overwrite `cores` from __init__ with the number of lambda windows
        self.cores = len(schdl)
        sbatch_params = (
            {"ntasks-per-node": self.cores}
            if sbatch_params is None
            else sbatch_params | {"ntasks-per-node": self.cores}
        )
        # Force the use of pmemd.cuda.MPI for H-REMD
        self.engine = super()._setup_engine("pmemd.cuda.MPI", self.cores)

        self._run_md_groupfile(
            cwd=self.work_dir,
            sysname=sysname,
            ngroups=len(schdl),
            groupfile=Path(groupfile),
            gpus=gpus,
            remlog=remlog,
            windows_rst7=tuple(windows_rst7),
            windows_mdouts=tuple(windows_mdouts),
            sbatch_params=sbatch_params,
        )

        self.output_artifacts = self.fill_output_artifacts(
            out_top=parm7,
            out_first_rst7=windows_rst7[0],
            out_first_mdout=windows_mdouts[0],
            out_first_nc=first_nc,
            schdl=schdl,
            states_tags=self.tags[self.artifact_map["BaseRestartStatesFile"]],
            sysname=sysname,
            out_boresch=out_boresch,
            remlog=remlog,
            lambda_sch=lambda_sch,
            ref_rst7=Path(self.work_dir, ref) if ref_passed_in else None,
        )

        return self.output_artifacts


@worknodehelper(
    file_exists=False,
    input_artifact_types=(BaseArtifact,),
    output_artifact_types=(LambdaSchedule,),
)
class QuickLambdaSchedule(BaseSingleWorkNode):
    """
    This class is used to generate a lambda schedule for alchemical simulations.
    It runs eagerly, since it doesn't need any input files.
    """

    prefix: str = ""
    suffix: str = ""
    tags: tuple = ("",)
    schedules: tuple = ("linear", "s2inverse")

    def __init__(
        self,
        wnid: str,
        *args,
        endstates: Optional[tuple[float, float]] = (0.0, 1.0),
        nlambdas: Optional[int] = None,
        step: Optional[float] = None,
        lambdas: Optional[Sequence[float]] = None,
        schedule: Optional[str] = None,
        decimals: int = 5,
        **kwargs,
    ) -> None:
        super().__init__(
            wnid=wnid,
            *args,
            **kwargs,
        )
        self.decimals = decimals

        self._schedule_handlers = {
            list: self._handler_lambdas,
            ("linear", tuple, int, type(None)): self._handler_linear_nlambdas,
            ("linear", tuple, type(None), float): self._handler_linear_step,
            ("s2inverse", tuple, int, type(None)): self._handle_s2inverse,
        }
        try:
            self.lambdas = self._schedule_handlers[type(lambdas)](list(lambdas))
        except KeyError:
            try:
                self.lambdas = self._schedule_handlers[(schedule, type(endstates), type(nlambdas), type(step))](
                    endstates, nlambdas, step
                )
            except KeyError:
                err_msg = (
                    f"Bad input: {schedule=}, {endstates=}, {nlambdas=}, {step=}\nSupported input signatures:\n"
                    + self.format_dict_types(self._schedule_handlers)
                )
                raise ValueError(err_msg)

    def _run(
        self,
        *,
        cwd: dirpath_t,
        sysname: str,
        **kwargs,
    ) -> Any:
        self.node_logger.info(f"Generated lambda schedule:\n{self.lambdas}")
        self.output_artifacts = ArtifactContainer(sysname, (LambdaSchedule(self.lambdas, decimals=self.decimals),))
        return self.output_artifacts

    @staticmethod
    def _handler_lambdas(lambdas: list[float]) -> NDArray[np.float64]:
        return np.array(lambdas)

    @staticmethod
    def _handler_linear_nlambdas(endstates: tuple[float, float], nlambdas: int, _):
        return np.linspace(endstates[0], endstates[1], nlambdas)

    @staticmethod
    def _handler_linear_step(endstates: tuple[float, float], _, step=None):
        return np.arange(endstates[0], endstates[1], step)

    def _handle_s2inverse(self, _, nlambdas: int, __):
        return self.s2inverse(nlambda=nlambdas)

    def s2inverse(self, nlambda):
        """Predict lambda values using the second order smoothstep function.

        Parameters
        ----------
        nlambda : int
            The number of lambda values to predict.

        Returns
        -------
        array_like
            The predicted lambda values.

        """
        xnew = np.linspace(0, 1, nlambda)
        lams = self.inverse_s2_interpolation(xnew)
        return lams

    @staticmethod
    def s2(x):
        """The second order smoothstep function.

        Parameters
        ----------
        x : float or array_like
            The input values.

        Returns
        -------
        float or array_like
            The output values.

        """
        return 6 * x**5 - 15 * x**4 + 10 * x**3

    def inverse_s2_interpolation(
        self, y_values, x_min: float = 0.0, x_max: float = 1.0, kind: Literal["cubic"] = "cubic"
    ):
        """Calculate the inverse of the second order smoothstep function using interpolation.

        Parameters
        ----------
        y_values : array_like
            The input values.
        x_min : float, optional
            The minimum input value. Default is 0.
        x_max : float, optional
            The maximum input value. Default is 1.
        kind : Literal["cubic"]
            The kind of interpolation. Default is 'cubic'.

        Returns
        -------
        array_like
            The input values.

        """
        x_interp = np.linspace(x_min, x_max, 1000)  # More points = better accuracy
        y_interp = self.s2(x_interp)
        f_inverse = interp1d(y_interp, x_interp, kind=kind, bounds_error=False, fill_value=np.nan)
        # Calculate inverse values using interpolation
        return f_inverse(y_values)

    @staticmethod
    def format_dict_types(data_dict: dict[Any, Any]) -> str:
        """
        Prints the keys of a dict in a nice format.

        - Type objects are printed as their __name__ (e.g., 'list', 'int', 'NoneType').
        - Tuples are printed with their elements formatted similarly. Strings within
          tuples are shown with quotes (e.g., 'linear') via repr().
        - Other key types are printed using their standard string representation.
        """

        def _format_element(element: Any) -> str:
            if isinstance(element, type):
                return element.__name__
            # repr() is used to get a string representation that, for strings,
            # includes quotes, making it clear it's a string literal.
            # For other types, it provides their standard unambiguous representation.
            return repr(element)

        out_string = []
        for key in data_dict.keys():
            formatted_string: str
            if isinstance(key, type):
                formatted_string = key.__name__
            elif isinstance(key, (tuple, list)):
                elements_str = ", ".join(_format_element(el) for el in key)
                if len(key) == 1:
                    formatted_string = f"({elements_str},)"
                else:
                    formatted_string = f"({elements_str})"
            else:
                formatted_string = str(key)
            out_string.append(formatted_string)

        return "\n".join(out_string)

    def _try_and_skip(self, sysname: str, *, outfile: filepath_t) -> bool:
        raise NotImplementedError

    def fill_output_artifacts(
        self,
        sysname: str,
        *,
        outfile: filepath_t,
    ) -> ArtifactContainer:
        raise NotImplementedError
