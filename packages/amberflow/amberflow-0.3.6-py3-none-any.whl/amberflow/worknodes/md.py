import shutil
from copy import deepcopy
from logging import Logger
from pathlib import Path
from string import Template
from typing import Optional, Sequence, Union, Any

from amberflow.artifacts import (
    BaseStructureFile,
    ArtifactContainer,
    ArtifactRegistry,
    BaseTopologyFile,
    BaseMdoutMD,
    BaseTrajectoryFile,
    AmberParameters,
    BaseStructureReferenceFile,
)
from amberflow.primitives import (
    filepath_t,
    dirpath_t,
    find_word_and_get_line,
    DEFAULT_RESOURCES_PATH,
    WorkNodeRunningError,
    BadMDout,
    convert_to_refname,
)
from amberflow.worknodes import worknodehelper, BaseSingleWorkNode, noderesource

__all__ = (
    "BaseMDWorkNode",
    "MDRun",
)


class BaseMDWorkNode(BaseSingleWorkNode):
    min_cores: int = 1
    min_gpus: int = 0
    output_tags: tuple[str, ...] = ("md",)
    # Inheritors should be anotated with @noderesource and this class attribute should be shadowed by the inheritor
    resources: Optional[dict] = None

    SUPPORTS: dict[str, Sequence[Union[int, str]]] = {
        "ntmin": (0, 1, 2),
        "engine": ("pmemd", "pmemd.cuda", "pmemd.MPI", "pmemd.cuda.MPI", "sander"),  # Base engines
        "prefix": ("target", "binder", "complex"),
        "biomolecule": ("protein", "nucleic"),
    }

    # noinspection PyUnusedLocal
    def __init__(
        self,
        wnid: str,
        *args,
        mdin_template: str = "md",
        mdparameters: Optional[AmberParameters] = None,
        engine: str = "pmemd.cuda",
        cores: int = 1,
        gpus: int = 1,
        max_systems: int = 0,
        sbatch_params: Optional[dict[str, Any]] = None,
        **kwargs,
    ) -> None:
        super().__init__(
            wnid=wnid,
            *args,
            **kwargs,
        )
        self.mdparameters = deepcopy(mdparameters) if mdparameters is not None else AmberParameters(nstlim=1000)
        self.check_supported(self.mdparameters.ntmin, "ntmin")
        self.min_cores = cores
        self.min_gpus = gpus
        self.max_systems = max_systems
        self.mdin_template = mdin_template

        self.engine = self._setup_engine(engine, self.min_cores)
        try:
            self.mdin = self.load_file(self.resources, mdin_template, mapping=self.mdparameters.as_dict())
        except KeyError:
            # The input mdparameters don't have all the required fields
            self.mdin = None

        self.sbatch_params = sbatch_params

    def _setup_engine(self, engine: str, min_cores: int) -> str:
        """
        Setup the engine for the MD run.
        If the engine is 'pmemd.cuda' and cores > 1, it will be set to 'pmemd.cuda.MPI'.
        If the engine is 'pmemd' and cores > 1, it will be set to 'pmemd.MPI'.
        """
        new_engine = self.check_supported(engine, "engine")
        # By now, I know the user typed in a supported engine, but if they're also asking for more than 1 worker,
        # then I need to set it for MPI running.
        if min_cores > 1:
            engine = "pmemd.cuda.MPI" if engine == "pmemd.cuda" else "pmemd.MPI" if engine == "pmemd" else engine
            new_engine = f"mpirun -np {min_cores} " + engine
        return new_engine

    def _run(
        self,
        *args,
        cwd: dirpath_t,
        sysname: str,
        gpus: tuple[int] = (1,),
        sbatch_params: Optional[dict[str, Any]] = None,
        **kwargs,
    ) -> ArtifactContainer:
        raise NotImplementedError

    def _try_and_skip(
        self, sysname: str, *, ref_rst7: Optional[Path] = None, prefix: str, tags: tuple[str, ...]
    ) -> bool:
        if self.skippable:
            try:
                self.output_artifacts = self._fill_output_artifacts(
                    sysname,
                    output_dir=self.work_dir,
                    ref_rst7=ref_rst7,
                    prefix=prefix,
                    tags=tags,
                )
                self.node_logger.info(f"Skipped {self.id} WorkNode.")
                return True
            except (FileNotFoundError, ValueError) as e:
                self.node_logger.info(f"Can't skip {self.id} Got: {e}")
            except BadMDout:
                self.node_logger.info(f"Can't skip {self.id}. Bad mdout file")
        return False

    def _fill_output_artifacts(
        self,
        sysname: str,
        *,
        ref_rst7: Optional[Path] = None,
        output_dir: dirpath_t,
        prefix: str,
        tags: tuple[str, ...],
    ) -> ArtifactContainer:
        output_name_template = f"{prefix}_{sysname}"
        rst7 = output_dir / f"{output_name_template}.rst7"
        traj = output_dir / f"{output_name_template}.nc"
        mdout = output_dir / f"{output_name_template}.mdout"

        # Get the tags for the mdout artifact
        mdout_tags = self.tags[self.artifact_map["BaseTopologyFile"]]

        # Also copy the parm7 file to the output directory, for easier chaining of MD worknodes
        parm7 = output_dir / f"{output_name_template}.parm7"
        shutil.copy(Path(self.input_artifacts["BaseTopology"]), parm7)
        try:
            artifacts = [
                ArtifactRegistry.create_instance_by_filename(parm7, tags=tags),
                ArtifactRegistry.create_instance_by_filename(rst7, tags=tags),
                ArtifactRegistry.create_instance_by_filename(traj, tags=tags),
                ArtifactRegistry.create_instance_by_filename(mdout, tags=mdout_tags),
            ]
        except FileNotFoundError:
            # No trajectory written
            artifacts = [
                ArtifactRegistry.create_instance_by_filename(parm7, tags=tags),
                ArtifactRegistry.create_instance_by_filename(rst7, tags=tags),
                ArtifactRegistry.create_instance_by_filename(mdout, tags=mdout_tags),
            ]
        if ref_rst7 is not None:
            try:
                artifacts.append(self.artifact_builder["BaseStructureReferenceFile"](ref_rst7))
            except KeyError:
                # A reference rst7 was used, but not passed in. We won't forward it.
                pass

        return ArtifactContainer(sysname, artifacts)

    def _write_mdin(self, output_dir: dirpath_t, sysname: str) -> Path:
        if self.mdin is None:
            err_msg = "Bad MDWorkNode. '.mdin' contents were not generated."
            raise FileNotFoundError(err_msg)
        output_path = output_dir / f"{self.__class__.__name__}.mdin"
        with open(output_path, "w") as outfile:
            outfile.write(f"{sysname} - {self.id}\n")
            outfile.write(self.mdin)

        return output_path

    def check_supported(self, element: Union[int, str], opt_type: str) -> Union[int, str]:
        """Checks if an element is supported for a given option type."""
        try:
            supported_options = self.SUPPORTS[opt_type]
            if element not in supported_options:
                raise ValueError(f"Unsupported {opt_type}: '{element}'. Must be one of: {supported_options}")
        except KeyError:
            raise ValueError(f"Unknown option type: '{opt_type}'. Must be one of: {list(self.SUPPORTS.keys())}")
        return element

    @staticmethod
    def load_file(resources: dict[str, str], template_id: str, mapping: Optional[dict] = None) -> str:
        try:
            template_txt = Template(resources[template_id])
        except KeyError:
            raise ValueError(f"Invalid template {template_id}. Must be one of {resources.keys()}")

        if mapping is None:
            return str(template_txt)
        else:
            try:
                return template_txt.substitute(mapping)
            except KeyError as e:
                raise KeyError(f"The input mapping is missing the key: {e}.")

    @staticmethod
    def check_mdout(mdout: filepath_t, node_logger: Logger) -> None:
        check_str = "Total wall time:"
        lines = find_word_and_get_line(mdout, check_str)
        if len(lines) != 0:
            return
        else:
            err_msg = f"Could not find: '{check_str}' in {mdout}. Check the mdout file."
            node_logger.error(err_msg)
            raise WorkNodeRunningError(err_msg)

    @staticmethod
    def get_cuda_visible_devices(gpus: tuple[int]) -> dict[str, str]:
        return {"CUDA_VISIBLE_DEVICES": ",".join(str(g) for g in gpus)}

    @staticmethod
    def copy_input_files_to_work_dir(cwd: dirpath_t, *args) -> None:
        for file_path in args:
            try:
                shutil.copy(Path(file_path), cwd / file_path.name)
            except shutil.SameFileError:
                continue

    def _run_md(
        self,
        *,
        cwd: dirpath_t,
        sysname: str,
        i: filepath_t,
        c: filepath_t,
        p: filepath_t,
        output_name_template: str,
        gpus: tuple[int] = (1,),
        ref: Optional[filepath_t] = None,
        sbatch_params: Optional[dict[str, Any]] = None,
    ) -> tuple[Path, Path, Path]:
        self.copy_input_files_to_work_dir(self.work_dir, p)
        r_name = f"{output_name_template}.rst7"
        x_name = f"{output_name_template}.nc"
        o_name = f"{output_name_template}.mdout"
        r = cwd / r_name
        x = cwd / x_name
        o = cwd / o_name

        # `c.name` and `r.name` may have the same name, so we copy c (input rst7)
        prevc_local = cwd / f"prev_{c.name}"
        shutil.copy(c, prevc_local)

        # use relative paths for the command line, since pmemd is fortran based and doesn't like absolute paths
        cmd_line = [
            self.engine,
            "-O",
            f"-i {i.name}",
            f"-c {prevc_local.name}",
            f"-p {p.name}",
            f"-x {x_name}",
            f"-r {r_name}",
            f"-o {o_name}",
        ]
        if ref is not None:
            if ref.parent != Path(cwd):
                ref_local = convert_to_refname(ref, Path(cwd))
                refname = ref_local.name
            else:
                refname = ref.name
            cmd_line.append(f"-ref {refname}")

        if sbatch_params is not None:
            sbatch_params.setdefault("job-name", f"{self.id}_{sysname}")
            sbatch_params.setdefault("output", f"{self.id}_{sysname}.slurmout")

        self.command.run(
            cmd_line,
            cwd=cwd,
            logger=self.node_logger,
            expected=(r, o),
            add_to_env=self.get_cuda_visible_devices(gpus),
            sbatch_params=sbatch_params,
        )

        self.check_mdout(o, self.node_logger)

        return r, x, o

    def _setup_reference(self) -> Union[None, str]:
        # If a reference structure was passed in, copy it to the working dir
        ref_rst7 = self.input_artifacts.get("BaseStructureReferenceFile")
        if ref_rst7 is None:
            ref = None
            self.node_logger.info("No reference rst7 provided")
        else:
            ref_rst7_filepath = Path(ref_rst7.filepath)
            ref = ref_rst7_filepath.name
            shutil.copy(ref_rst7_filepath, self.work_dir / ref)
            self.node_logger.info(f"Using reference rst7 {ref_rst7_filepath} ")
        return ref

    def __str__(self) -> str:
        return f"{self.__class__.__name__} - {self.id}"


@noderesource(DEFAULT_RESOURCES_PATH / "mdin")
@worknodehelper(
    file_exists=True,
    input_artifact_types=(BaseStructureFile, BaseTopologyFile),
    optional_artifact_types=(BaseStructureReferenceFile,),
    output_artifact_types=(
        BaseStructureFile,
        BaseTopologyFile,
        BaseTrajectoryFile,
        BaseMdoutMD,
        BaseStructureReferenceFile,
    ),
)
class MDRun(BaseMDWorkNode):
    def __init__(
        self,
        wnid: str,
        *args,
        mdin_template: str = "md_restrained_varying",
        **kwargs,
    ) -> None:
        super().__init__(
            wnid=wnid,
            *args,
            mdin_template=mdin_template,
            **kwargs,
        )

    def _run(
        self,
        *,
        cwd: dirpath_t,
        sysname: str,
        binpath: Optional[filepath_t] = None,
        cores: Optional[int] = None,
        gpus: tuple[int] = (1,),
        sbatch_params: Optional[dict[str, Any]] = None,
        **kwargs,
    ) -> Any:
        top_typename = type(self.input_artifacts["BaseTopology"]).__name__
        prefix = self.prefix[top_typename]
        tags = self.tags[top_typename]
        ref = super()._setup_reference()
        ref_passed_in = False if ref is None else True
        if ref_passed_in:
            ref_rst7 = Path(self.work_dir, ref)
        else:
            in_rst7 = Path(self.input_artifacts["BaseStructureFile"])
            ref_rst7 = convert_to_refname(in_rst7, self.work_dir)
            shutil.copy(in_rst7, ref_rst7)
            self.node_logger.info(f"Using reference rst7 {ref_rst7} copied from input structure file {in_rst7}")

        if super()._try_and_skip(sysname, ref_rst7=ref_rst7, prefix=prefix, tags=tags):
            return self.output_artifacts

        # overwrite `cores` from __init__ with _run() `cores`
        self.cores = self.min_cores if cores is None else cores
        sbatch_params = (
            {"ntasks-per-node": self.cores}
            if sbatch_params is None
            else sbatch_params | {"ntasks-per-node": self.cores}
        )

        mdin_file = self.write_mdin(self.work_dir, sysname)

        self._run_md(
            cwd=self.work_dir,
            sysname=sysname,
            i=mdin_file,
            c=Path(self.input_artifacts["BaseStructureFile"]),
            p=Path(self.input_artifacts["BaseTopology"]),
            ref=ref_rst7,
            output_name_template=f"{prefix}_{sysname}",
            gpus=gpus,
            sbatch_params=sbatch_params,
        )

        self.output_artifacts = self._fill_output_artifacts(
            sysname, output_dir=self.work_dir, ref_rst7=ref_rst7 if ref_passed_in else None, prefix=prefix, tags=tags
        )

        return self.output_artifacts

    def write_mdin(self, output_dir: dirpath_t, sysname: str) -> Path:
        output_path = output_dir / f"{self.__class__.__name__}.mdin"
        with open(output_path, "w") as outfile:
            outfile.write(f"{sysname} - {self.id}\n")
            outfile.write(self.mdin)

        return output_path

    def _try_and_skip(self, sysname: str, *args, **kwargs) -> bool:
        raise NotImplementedError

    def fill_output_artifacts(
        self,
        sysname: str,
    ) -> ArtifactContainer:
        raise NotImplementedError
