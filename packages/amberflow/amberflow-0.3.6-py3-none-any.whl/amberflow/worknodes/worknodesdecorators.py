import functools
import inspect
import logging
import time
from pathlib import Path
from typing import Callable, Any, Optional

from amberflow import __version__
from amberflow.artifacts import BaseArtifact, BatchArtifacts, ArtifactContainer, ArtifactRegistry
from amberflow.primitives import (
    WorkNodeError,
    DEFAULT_RESOURCES_PATH,
    filepath_t,
    WorkNodeRunningError,
    dirpath_t,
    CommandRegistryMeta,
)
from amberflow.worknodes import WorkNodeStatus, BaseBatchWorkNode, BaseSingleWorkNode

__all__ = (
    "load_resources",
    "noderesource",
    "worknodehelper",
)


def setup_logger(logpath: dirpath_t, level: int = logging.INFO, filemode: str = "w") -> logging.Logger:
    logger = logging.getLogger(f"{logpath.parent}_{logpath.name}")
    logger.setLevel(level)
    formatter = logging.Formatter(
        "{asctime} - {levelname} - {version} {message}",
        style="{",
        datefmt="%Y-%m-%d %H:%M:%S",
        defaults={"version": __version__},
    )
    file_handler = logging.FileHandler(filename=logpath / "log.log", mode=filemode)
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


def load_resources(resources_path: filepath_t = DEFAULT_RESOURCES_PATH) -> dict[str, str]:
    """
    Load all text files from the specified resources directory into a dictionary.

    Args:
        resources_path: The base path where resource type directories reside.
                        Defaults to "src/amberflow/data".

    Returns:
        A dictionary mapping file names (without extensions) to their contents.
    """
    resources_path = Path(resources_path)
    if not resources_path.is_dir():
        raise ValueError(f"Resource directory not found or is not a directory: {resources_path} ")

    loaded_resources: dict[str, str] = {}
    for resource in resources_path.iterdir():
        if resource.is_file():
            try:
                # Read file content as text, assuming UTF-8 encoding
                content = resource.read_text(encoding="utf-8")
                loaded_resources[resource.stem] = content
            except Exception as e:
                raise ValueError(f"Error reading file {resource.resolve()}: {e}. Skipping.", ResourceWarning)

    return loaded_resources


def noderesource(resources_path: filepath_t = DEFAULT_RESOURCES_PATH) -> Callable[[type[Any]], type[Any]]:
    """
    Class decorator factory that loads file contents from a specified resource directory
    into the class dictionary 'resources'.

    Args:
        resources_path: The base path where resource type directories reside.
                        Defaults to "src/amberflow/data".

    Returns:
        The actual class decorator function.
    """
    resources_path = Path(resources_path)
    if not resources_path.is_dir():
        raise ValueError(f"Resource directory not found or is not a directory: {resources_path} ")

    def decorator(cls: type[Any]) -> type[Any]:
        """
        The actual decorator that scans the directory and adds the 'resources' attribute.
        """
        loaded_resources: dict[str, str] = load_resources(resources_path)
        # Add the 'resources' dictionary as a class attribute
        setattr(cls, "resources", loaded_resources)
        return cls

    return decorator


# TODO: `expects_unique` is removed, now that ArtifactContainer is a dict, which enforces uniqueness by default.
# maybe it should check that the length of each list is 1
def worknodehelper(
    file_exists: bool = True,
    input_artifact_types: tuple = (BaseArtifact,),
    output_artifact_types: tuple = (BaseArtifact,),
    enforce_output_types: bool = True,
    need_all_input_artifacts: bool = True,
    logging_level: int = logging.INFO,
    optional_artifact_types: Optional[tuple] = None,
    input_suffix: Optional[str] = None,
):
    """
    Class decorator factory that:
     - Enhances the 'run' method of a class by adding status tracking, timing, directory creation and error handling,
     - Validates the types of input_artifacts, filters out those that are not wanted and optionally checks that the actual files
       exist (if file based).
    """
    public_run_method = "run"
    private_run_method = "_run"

    # TODO: if we ever change ArtifactCointainer from a dict-like DS to a list-like DS, we must implement
    # `must_be_unique` check here.
    def filter_input_artifacts(
        expected_artifact_types: tuple[type[ArtifactRegistry]],
        input_artifacts: ArtifactContainer,
        input_arg_name: str,
        cls: type,
        method_name: str,
        check_file_exists: bool = False,
        enforce_input_artifacts: bool = True,
        opt_art_types: Optional[tuple] = None,
        suffix: Optional[str] = None,
    ) -> tuple[ArtifactContainer, dict[str, str], dict[str, type]]:
        """
        Checks that all the expected types be present in the input artifacts, it doesn't matter if there are others
        Parameters

        Args:
            expected_artifact_types (Sequence[type]): The expected artifact types annotated on the class.
            input_artifacts (ArtifactContainer): A sequence of input artifact types to validate.
            input_arg_name (str): The name of the input argument being validated.
            cls (type): The class to which the method belongs.
            method_name (str): The name of the method being validated.
            check_file_exists: If True, checks if the file exists for each artifact in 'input_artifacts'.
            enforce_input_artifacts: If True, raises TypeError if not all expected artifact types are present.
            opt_art_types: If provided, these types are not required but can be present in the input artifacts.
            suffix: If provided, checks that the input artifacts have this suffix.
        Raises:
            TypeError: If the input artifacts do not match the expected types or their inheritors.

        Returns:
            tuple[ArtifactContainer, dict[str, str], dict[str, type]]: A tuple containing:
                - ArtifactContainer with the filtered input artifacts that match the expected types
                - Dictionary mapping expected artifact types to their actual implementation types, both as strings
                - Dictionary mapping expected artifact types (string) to their actual implementation types (types)

        """
        set_expected_artifact_types = set(expected_artifact_types)

        # Ugly implementation, there's a better way
        expected_artifacts = []
        artifact_map: dict[str, str] = {}
        artifact_builder: dict[str, type] = {}

        for i, art_container in enumerate(input_artifacts.values()):
            for item in art_container:
                for expected_type in expected_artifact_types:
                    if isinstance(item, expected_type):
                        try:
                            filepath = getattr(item, "filepath")
                            if check_file_exists and not Path(filepath).exists():
                                raise FileNotFoundError(f"File {filepath} does not exist.")
                        except (KeyError, AttributeError):
                            # Artifact is not a file-based artifact.
                            pass
                        try:
                            item_suffix = getattr(item, "suffix")
                            if suffix is not None and item_suffix != suffix:
                                # Filter out artifacts that do not have the expected suffix
                                continue
                        except (KeyError, AttributeError):
                            # Artifact does not have a suffix, probably not a file-based artifact.
                            pass
                        set_expected_artifact_types.discard(expected_type)
                        expected_artifacts.append(item)
                        artifact_map[expected_type.__name__] = type(item).__name__
                        artifact_builder[expected_type.__name__] = type(item)

                if opt_art_types is not None and isinstance(item, opt_art_types):
                    expected_artifacts.append(item)
                    for expected_type in opt_art_types:
                        if isinstance(item, expected_type):
                            artifact_map[expected_type.__name__] = type(item).__name__
                            artifact_builder[expected_type.__name__] = type(item)

        if len(set_expected_artifact_types) > 0 and enforce_input_artifacts:
            # Format expected types for readability
            input_types_str = ", ".join(type(a).__name__ for arts in input_artifacts.values() for a in arts)
            expected_types_str = ", ".join(t.__name__ for t in expected_artifact_types)
            raise TypeError(
                f"{cls.__name__}.{method_name} got '{input_arg_name}' with artifact types: ({input_types_str}) "
                f"and it should, at least, have the following types (or their inheritors): ({expected_types_str})."
                f" Missing types: {', '.join(t.__name__ for t in set_expected_artifact_types)}."
            )

        return ArtifactContainer(input_artifacts.id, expected_artifacts), artifact_map, artifact_builder

    def check_attributes(
        cls_instance,
        keyword_args: dict[str, Any],
        attr_cwd: str = "cwd",
        attr_out_dirname: str = "out_dirname",
        attr_id: str = "id",
        attr_logger: str = "logger",
        attr_status: str = "status",
    ) -> None:
        required_attrs = [attr_cwd, attr_out_dirname, attr_id, attr_logger, attr_status]
        missing_attrs = [
            attr for attr in required_attrs if getattr(cls_instance, attr) is None and keyword_args.get(attr) is None
        ]
        if missing_attrs:
            raise AttributeError(
                f"Instance of type {type(cls_instance)} is missing required attributes for @work_node_runner: {', '.join(missing_attrs)}"
            )

    def collect_artifacts_attrs(input_artifacts: ArtifactContainer, attr: str) -> dict:
        input_attrs = {}
        for art_name, arts in input_artifacts.items():
            for art in arts:
                try:
                    input_attrs[art_name] = getattr(art, attr)
                except AttributeError:
                    # No `attr` in this artifact, skip it
                    continue
        return input_attrs

    def worknodehelper_decorator(cls):
        try:
            original_public_method = getattr(cls, public_run_method)
        except AttributeError:
            raise TypeError(
                f"""Class {cls.__name__} must have a callable '{public_run_method}' method to use @worknodehelper.
Does it inherit from BaseSingleWorkNode or BaseBatchWorkNode?"""
            )
        try:
            original_private_method = getattr(cls, private_run_method)
        except AttributeError:
            raise TypeError(
                f"""Class {cls.__name__} must have a callable '{private_run_method}' method to use @worknodehelper.
Does it inherit from BaseSingleWorkNode or BaseBatchWorkNode?"""
            )

        # Check for malformed private method signature
        private_run_signature = inspect.signature(original_private_method)
        try:
            private_run_signature.parameters["cwd"]
        except KeyError:
            raise TypeError(f"Class {cls.__name__} method: '{original_private_method}' must have a `cwd` argument.")
        if issubclass(cls, BaseSingleWorkNode):
            try:
                private_run_signature.parameters["sysname"]
            except KeyError:
                raise TypeError(
                    f"Class {cls.__name__} method: '{original_private_method}' must have a `sysname` argument."
                )

        def validate_args(args, kwargs, is_batch: bool) -> None:
            err_msg = ""
            if len(args) == 0:
                err_msg += "missing required positional argument: 'input_artifacts'\n"
            if "cwd" not in kwargs:
                err_msg += "missing required keyword argument: 'cwd'\n"
            if is_batch:
                if "systems" not in kwargs:
                    err_msg += "missing required keyword argument: 'systems'\n"
            else:
                if "sysname" not in kwargs:
                    err_msg += "missing required keyword argument: 'sysname'\n"
            if err_msg != "":
                raise TypeError(f"{cls.__name__}.{public_run_method}: {err_msg}")

        @functools.wraps(original_public_method)
        def run_wrapper(self, *args, **kwargs):
            # `input_artifact_map` and `artifact_builder` map the expected artifact types to their actual implementation types.
            input_artifact_map = {}
            artifact_builder = {}

            # First, validate the input artifacts
            validate_args(args, kwargs, isinstance(self, BaseBatchWorkNode))
            all_artifacts = args[0]
            data: dict[str, ArtifactContainer] = {}
            if isinstance(self, BaseBatchWorkNode):
                if not isinstance(all_artifacts, BatchArtifacts):
                    raise TypeError(
                        f"`input_artifacts` for {cls.__name__}.{public_run_method} must be a BatchArtifacts, got {type(all_artifacts).__name__}."
                    )
                for sysname, input_artifact in all_artifacts.items():
                    data[sysname], input_artifact_map, artifact_builder = filter_input_artifacts(
                        input_artifact_types,
                        input_artifact,
                        "input_artifacts",
                        cls,
                        public_run_method,
                        file_exists,
                        enforce_input_artifacts=need_all_input_artifacts,
                        opt_art_types=optional_artifact_types,
                        suffix=input_suffix,
                    )
                input_artifacts = BatchArtifacts(art_id=all_artifacts.id, data=data)

                # Get the artifact container from the first system, so we can get the prefixes and the tags
                some_artifact_container = next(iter(all_artifacts.values()))
                input_prefixes = collect_artifacts_attrs(some_artifact_container, "prefix")
                input_tags = collect_artifacts_attrs(some_artifact_container, "tags")
            elif isinstance(self, BaseSingleWorkNode):
                if not isinstance(all_artifacts, ArtifactContainer):
                    raise TypeError(
                        f"Argument input_artifacts for {cls.__name__}.{public_run_method} must be an ArtifactContainer, got {type(all_artifacts).__name__}."
                    )
                input_artifacts, input_artifact_map, artifact_builder = filter_input_artifacts(
                    input_artifact_types,
                    all_artifacts,
                    "input_artifacts",
                    cls,
                    public_run_method,
                    file_exists,
                    enforce_input_artifacts=need_all_input_artifacts,
                    opt_art_types=optional_artifact_types,
                    suffix=input_suffix,
                )
                input_prefixes = collect_artifacts_attrs(input_artifacts, "prefix")
                input_tags = collect_artifacts_attrs(input_artifacts, "tags")
            else:
                raise TypeError(
                    f"WorkNode must be either `BaseSingleWorkNode` or `BaseBatchWorkNode`, got {type(self)}."
                )
            # Set the validated and filtered input artifacts
            setattr(self, "input_artifacts", input_artifacts)
            # Set the prefixes and tags from the input artifacts
            setattr(self, "prefix", input_prefixes)
            setattr(self, "tags", input_tags)
            setattr(self, "artifact_map", input_artifact_map)
            setattr(self, "artifact_builder", artifact_builder)
            # my setdefault for a class attribute. There should be something nicer. The idea is to give
            # precedence to the WorkNode's attribute, but to also allow the run() method to override it.
            if getattr(self, "skippable") is None:
                setattr(self, "skippable", kwargs.get("skippable", False))
            # Set `expects` and `gives` attributes for the node. These are for schedulers to know if 2 nodes can be connected.
            setattr(self, "expects", input_artifact_types)
            setattr(self, "gives", output_artifact_types)

            # Check for required attributes on the instance
            attr_cwd = "cwd"
            attr_out_dirname = "out_dirname"
            attr_id: str = "id"
            attr_logger: str = "logger"
            attr_status: str = "status"
            check_attributes(self, kwargs, attr_cwd, attr_out_dirname, attr_id, attr_logger, attr_status)

            try:
                setattr(self, "status", WorkNodeStatus.RUNNING)
                self.start_time = time.monotonic()

                # Create working dir
                base_cwd_path = Path(kwargs[attr_cwd])
                node_out_dir = getattr(self, attr_out_dirname)
                self.work_dir = base_cwd_path / node_out_dir
                self.work_dir.mkdir(parents=True, exist_ok=True)

                # Initialize the command if it hasn't been already.
                if self.command is None:
                    # `root_dir` is used by remote running commands and their executors, and must be set by the Pipeline,
                    # or manually by the user
                    self.command = CommandRegistryMeta.name[self.command_str](
                        self.remote_server, self.remote_base_dir, self.root_dir
                    )
                elif not self.command.initialized:
                    # If the command is not initialized, we need to initialize it with the root_dir
                    self.command = self.command.replace(local_base_dir=self.root_dir)

                # Set up logger
                instance_id = getattr(self, attr_id)
                logger = getattr(self, attr_logger)
                new_logging_level = logging_level if self.logging_level is None else self.logging_level
                new_logging_filemode = "w" if self.logging_filemode is None else self.logging_filemode
                if logger == "file":
                    # noinspection PyUnresolvedReferences
                    self.node_logger = setup_logger(self.work_dir, new_logging_level, new_logging_filemode)
                    self.node_logger.debug(f"Running {cls.__name__} {instance_id}")

                # Initialize output dir names for each system, the batch node will then decide if it creates them or not.
                if isinstance(self, BaseBatchWorkNode):
                    systems: dict[str, dirpath_t] = kwargs["systems"]
                    self.out_dirs = {sysname: Path(directory) / node_out_dir for sysname, directory in systems.items()}

                # Run the original method
                result = original_private_method(self, *args[1:], **kwargs)

                # Clean-up TODO: Implement cleanup logic if needed, reading from `self.debug` and `temp_files`
                check_batch: bool = enforce_output_types and isinstance(self, BaseBatchWorkNode)
                check_single: bool = enforce_output_types and isinstance(self, BaseSingleWorkNode)
                if check_single:
                    for artifacts in self.output_artifacts.values():
                        for art in artifacts:
                            if not isinstance(art, output_artifact_types):
                                err_msg = f"Output artifact {art} is not an instance of one of the expected types: {output_artifact_types}"
                                self.node_logger.error(err_msg)
                                raise WorkNodeError(err_msg)
                elif check_batch:
                    for art_container in self.output_artifacts.values():
                        for artifacts in art_container.values():
                            for art in artifacts:
                                if not isinstance(art, output_artifact_types):
                                    err_msg = f"Output artifact {art} is not an instance of one of the expected types: {output_artifact_types}"
                                    self.node_logger.error(err_msg)

                setattr(self, attr_status, WorkNodeStatus.COMPLETED)
                self.node_logger.debug(
                    f"Done with {cls.__name__} {instance_id} `output_artifacts`: {self.output_artifacts}"
                )
                return result

            except Exception as e:
                setattr(self, attr_status, WorkNodeStatus.FAILED)

                cls_name = cls.__name__
                instance_id = getattr(self, attr_id, "NO ID")
                work_dir = getattr(self, "work_dir", "Not available")

                # Detailed error msg to the log file
                log_err_msg = f"Error running {cls_name} '{instance_id}' at {work_dir}. Caught exception:"
                self.node_logger.error(log_err_msg, exc_info=True)  # exc_info=True adds the full traceback to the log

                # Shorter error message for the CLI
                user_err_msg = (
                    f"WorkNode '{instance_id}' failed. Check the log file in directory: {work_dir}\n"
                    f"  > Original error: {type(e).__name__}: {e}"
                )
                if isinstance(e, (AttributeError, TypeError)):
                    for art_type, arts in input_artifacts.items():
                        if len(arts) > 1:
                            user_err_msg += f"""\nInput artifact {art_type} has more than 1 artifact: {arts}
Maybe you expected unique artifacts?"""
                raise WorkNodeRunningError(user_err_msg) from e
            finally:
                self.end_time = time.monotonic()
                self.elapsed_time = self.end_time - self.start_time

        setattr(cls, public_run_method, run_wrapper)
        return cls

    return worknodehelper_decorator
