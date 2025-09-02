import shutil
from pathlib import Path
from typing import Optional, Any, Sequence

from amberflow.artifacts import (
    BaseRestartStatesFile,
    ArtifactContainer,
    BaseStructureReferenceFile,
    ArtifactRegistry,
    BoreschRestraints,
    LambdaScheduleFile,
    BaseStructureFile,
    BaseStatesFile,
    BaseArtifact,
    BaseTrajectoryStatesFile,
)
from amberflow.primitives import (
    filepath_t,
    dirpath_t,
    DEFAULT_RESOURCES_PATH,
    convert_to_refname,
    WorkNodeError,
)
from amberflow.worknodes import worknodehelper, noderesource, BaseSingleWorkNode

__all__ = ("CreateReferenceStructure", "GenerateLambdaScheduleFile", "FilterStates")


@noderesource(DEFAULT_RESOURCES_PATH / "mdin")
@worknodehelper(
    file_exists=True,
    input_artifact_types=(BaseRestartStatesFile, BaseStructureFile),
    need_all_input_artifacts=False,
    output_artifact_types=(BaseStructureReferenceFile,),
)
class CreateReferenceStructure(BaseSingleWorkNode):
    """
    Create a reference structure file out of a set of restart states.
    """

    def __init__(
        self,
        wnid: str,
        *args,
        state: float = 0,
        **kwargs,
    ) -> None:
        super().__init__(
            wnid=wnid,
            *args,
            **kwargs,
        )
        self.state = state

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
        try:
            struct_states = self.input_artifacts["BaseRestartStatesFile"]
            if self.state not in set(struct_states.states.keys()):
                err_msg = f"State {self.state} not present in input {struct_states} Available states: {struct_states.states.keys()}"
                self.logger.error(err_msg)
                raise ValueError(err_msg)
            art_filepath = struct_states.states[self.state]
            input_artifact_type_str = self.artifact_map["BaseRestartStatesFile"]
        except KeyError:
            struct = self.input_artifacts["BaseStructureFile"]
            if isinstance(struct, Sequence):
                err_msg = f"Got more than 1 BaseStructureFile: {struct}. Please provide a single structure file."
                self.logger.error(err_msg)
                raise ValueError(err_msg)
            art_filepath = struct.filepath
            input_artifact_type_str = self.artifact_map["BaseStructureFile"]

        new_filepath = convert_to_refname(art_filepath, self.work_dir)
        # Copy the file to the work directory
        output_filepath = shutil.copy(art_filepath, new_filepath)
        self.node_logger.info(f"Copying {art_filepath} to {new_filepath} ")
        self.output_artifacts = self.fill_output_artifacts(
            sysname, output_filepath=output_filepath, input_artifact_type_str=input_artifact_type_str
        )
        return self.output_artifacts

    def _try_and_skip(self, sysname: str, *, output_filepath: Path) -> bool:
        raise NotImplementedError

    def fill_output_artifacts(
        self, sysname: str, *, output_filepath: Path, input_artifact_type_str: str
    ) -> ArtifactContainer:
        # TODO: I have to find a better way to do this
        new_tags = set(self.tags[input_artifact_type_str])
        new_tags.discard("alchemical")
        new_tags.add("reference")
        out_art = ArtifactRegistry.create_instance_by_filename(output_filepath, tags=tuple(new_tags))

        return ArtifactContainer(sysname, (out_art,))


@worknodehelper(
    file_exists=True, optional_artifact_types=(BoreschRestraints,), output_artifact_types=(LambdaScheduleFile,)
)
class GenerateLambdaScheduleFile(BaseSingleWorkNode):
    """ """

    LAMBDA_TYPES: set[str] = {
        "TypeGen",
        "TypeBAT",
        "TypeRestBA",
        "TypeEleRec",
        "TypeEleCC",
        "TypeEleSC",
        "TypeVDW",
        "TypeRestB",
        "TypeRestA",
        "TypeNone",
    }
    FUNCTION_TYPES: set[str] = {
        "linear",
        "smooth_step0",
        "smooth_step1",
        "smooth_step2",
        "smooth_step3",
        "smooth_step4",
    }
    MATCH_TYPES: set[str] = {"complementary", "symmetric"}

    def __init__(
        self,
        wnid: str,
        *args,
        lambda_type: str = "TypeRestBA",
        function_type: str = "smooth_step2",
        match_type: str = "symmetric",
        parameter1: float = 0.0,
        parameter2: float = 1.0,
        **kwargs,
    ) -> None:
        """
        Initializes the TemplateWorkNode.

        It is crucial to call `super().__init__` to ensure the base worknode is properly initialized
        with its unique ID and other required setup.

        Args:
            wnid (str): A unique identifier for the worknode instance.
            *args: Positional arguments passed to the parent class.
            **kwargs: Keyword arguments passed to the parent class. You can
                      add your own custom parameters here.
        """
        super().__init__(
            wnid=wnid,
            *args,
            **kwargs,
        )
        self.lambda_type = lambda_type
        self.function_type = function_type
        self.match_type = match_type
        self.parameter1 = parameter1
        self.parameter2 = parameter2

        self.check_input()

    def _run(
        self,
        *,
        cwd: dirpath_t,
        sysname: str,
        **kwargs,
    ) -> Any:
        """
        The core execution method for the worknode. This method is not called directly by the user, nor the scheduler.
        @worknodehelper will wrap it inside a `run()` method.

        Before this method is called, the `@worknodehelper` decorator has already:
            - Filtered input artifacts based on `input_artifact_types`.
            - Populated `self.input_artifacts` with the filtered artifacts.
            - Created and assigned the node's working directory to `self.work_dir`.
            - Set up a dedicated logger, `self.node_logger`, that logs to the work_dir.
            - Set the node's status to RUNNING.
            - Initialized the `self.command` object for command execution, if necessary.
            - Wrapped the call in a try/except block

        After this method completes, the decorator will:
            - Optionally validate the output artifacts against `output_artifact_types`.
            - Set the node's status to COMPLETED or FAILED.
            - Record the execution time.

        Args:
            cwd (dirpath_t): The working directory for this specific execution.
            sysname (str): The name of the system being processed.
            binpath (Optional[filepath_t]): Path to an external binary, if needed.
            **kwargs: Additional keyword arguments passed from the scheduler.

        Returns:
            The output artifacts generated by this node. The decorator expects these to be in `self.output_artifacts`.
        """

        if self.skippable:
            if self._try_and_skip(sysname):
                return self.output_artifacts

        content = f"{self.lambda_type}, {self.function_type}, {self.match_type}, {self.parameter1}, {self.parameter2}\n"
        output_filepath = Path(self.work_dir, "lambda.sch")
        with open(output_filepath, "w") as f_out:
            f_out.write(content)
        self.node_logger.info(f"✅ Successfully wrote {content.strip()} schedule to {output_filepath}")
        self.output_artifacts = self.fill_output_artifacts(sysname)

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
            except (FileNotFoundError, ValueError) as e:
                self.node_logger.info(f"Can't skip {self.id} Got: {e}")
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
        return ArtifactContainer(sysname, (LambdaScheduleFile(Path(self.work_dir, "lambda.sch")),))

    def check_input(self) -> None:
        if self.lambda_type not in self.LAMBDA_TYPES:
            raise ValueError(f"Invalid LambdaType: '{self.lambda_type}'. Choose from {sorted(list(self.LAMBDA_TYPES))}")
        if self.function_type not in self.FUNCTION_TYPES:
            raise ValueError(f"Invalid FunctionType '{self.function_type}' . Must be one of {self.FUNCTION_TYPES}")
        if self.match_type not in self.MATCH_TYPES:
            raise ValueError(f"Invalid Matchtype '{self.match_type}' . Must be one of {self.MATCH_TYPES}")

        for param in ("parameter1", "parameter2"):
            p_float = float(getattr(self, param))
            if not (0.0 <= p_float <= 1.0):
                raise ValueError(f"{param} must be a number between 0.0 and 1.0, but got: {p_float}")
            setattr(self, param, p_float)


@worknodehelper(file_exists=True, input_artifact_types=(BaseStatesFile,), output_artifact_types=(BaseStatesFile,))
class FilterStates(BaseSingleWorkNode):
    """
    A worknode that filters artifacts that refer to states.
    """

    def __init__(
        self,
        wnid: str,
        *args,
        lambdas: Sequence[str] = None,
        endpoints: bool = False,
        state_type: type = BaseTrajectoryStatesFile,
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
        if not endpoints and lambdas is None:
            raise WorkNodeError("Either endpoints or lambdas must be provided.")
        self.endpoints = endpoints
        self.lambdas = lambdas
        if not issubclass(state_type, BaseStatesFile):
            raise ValueError(f"state_type must be a subclass of BaseStatesFile, but got: {state_type}")
        self.state_type = state_type

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
        out_artifacts: list[BaseArtifact] = []
        for art_type_str, artifacts in self.input_artifacts.items():
            art_type = ArtifactRegistry.name[art_type_str]
            if issubclass(art_type, self.state_type):
                assert len(artifacts) == 1, f"Can only deal with 1 input artifact of each type. Got: {artifacts}"
                states_art = artifacts[0]
                new_filepath = Path(self.work_dir, states_art.filepath.name)
                if self.endpoints:
                    states_keys = list(states_art.keys())
                    self.lambdas = [states_keys[0], states_keys[-1]]
                for state in self.lambdas:
                    try:
                        state_filepath = states_art.states[state]
                        shutil.copy(state_filepath, Path(self.work_dir, state_filepath.name))
                        self.node_logger.info("Filtered state '{art_type}' to '{state}'")
                    except KeyError:
                        err_msg = f"Availables states: {states_art.states}, but requested state: {state}"
                        self.node_logger.error(err_msg)
                        raise ValueError(err_msg)
                out_artifacts.append(art_type(new_filepath, lambdas=self.lambdas))

        if len(out_artifacts) == 0:
            self.node_logger.warn(
                f"No artifacts were selected. Check your filtering criteria. Got: {self.input_artifacts}"
            )

        self.output_artifacts = ArtifactContainer(sysname, out_artifacts)
        return self.output_artifacts

    def _try_and_skip(self, sysname: str) -> bool:
        raise NotImplementedError

    def fill_output_artifacts(
        self,
        sysname: str,
    ) -> ArtifactContainer:
        raise NotImplementedError
