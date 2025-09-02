import inspect
import logging
from enum import Enum
from pathlib import Path
from typing import List, Dict, Any, Type, Optional, Union, Sequence

from amberflow.artifacts import BatchArtifacts, ArtifactContainer
from amberflow.primitives import (
    WorkNodeError,
    UnknownWorkNodeError,
    dirpath_t,
    get_null_logger,
    BaseCommand,
)

__all__ = [
    "BaseWorkNode",
    "WorkNodeRegistryMeta",
    "WorkNodeStatus",
    "BaseBatchWorkNode",
    "BaseSingleWorkNode",
]


# noinspection PyMethodParameters
class WorkNodeRegistryMeta(type):
    """
    Metaclass to register WorkNodes.
    It inspects and stores __init__ parameters.
    Optionally uses 'prefix', 'suffix', and 'tags' class attributes
    for identification and lookup via an identifier key.
    """

    # Registry mapping WorkNode class name to class object
    _name: Dict[str, Type] = {}
    # Registry mapping identifier tuple (prefix, suffix, *tags) to class object
    _identifiers: dict[tuple[str, str, tuple], type] = {}
    # Registry mapping WorkNode class name to its __init__ parameter info list
    _init_params: Dict[str, List[Dict[str, Any]]] = {}
    _template_cls = None

    @classmethod
    def _get_template_cls(cls):
        if cls._template_cls is None:
            # This import is delayed to avoid circular dependencies
            from amberflow.worknodes.templateworknode import TemplateWorkNode

            cls._template_cls = TemplateWorkNode
        return cls._template_cls

    def __new__(meta_cls, cls_name: str, bases: tuple, cls_dict: Dict[str, Any]):
        new_cls = super().__new__(meta_cls, cls_name, bases, cls_dict)

        # Avoid registering common base classes (e.g., BaseWorkNode)
        is_base_class = cls_name.startswith("Base")
        if not is_base_class:
            # register by name
            if cls_name in meta_cls._name:
                raise WorkNodeError(f"WorkNode class '{cls_name}' already registered by name.")
            meta_cls._name[cls_name] = new_cls

            # --- Register by Identifier (prefix, suffix, tags) if available ---
            try:
                # These keys must exist in the class definition for this registration path
                prefix = cls_dict["prefix"]
                suffix = cls_dict["suffix"]
                tags = cls_dict.get("tags", tuple())
                identifier_key = (prefix, suffix, tags)

                if identifier_key in meta_cls._identifiers:
                    existing_cls = meta_cls._identifiers[identifier_key].__name__
                    raise WorkNodeError(
                        f"WorkNode class '{cls_name}' attempts to register identifier "
                        f"(prefix='{prefix}', suffix='{suffix}', tags={tags}) "
                        f"which is already used by class '{existing_cls}'."
                    )

                meta_cls._identifiers[identifier_key] = new_cls
            except KeyError:
                # If 'prefix' or 'suffix' are missing, this WorkNode isn't registered
                # by identifier. This is expected for WorkNodes not associated
                # with this specific identification scheme.
                pass

            # Use the existing _get_init helper method
            meta_cls._init_params[cls_name] = meta_cls._get_init(cls_name, cls_dict)

            if (
                cls_name not in ["TemplateWorkNode", "WorkNodeDummy"]
                and inspect.isclass(new_cls)
                and issubclass(new_cls, BaseSingleWorkNode)
            ):
                template_cls = meta_cls._get_template_cls()
                meta_cls.validate_against_template(new_cls, template_cls)

        # Return the newly created WorkNode class
        return new_cls

    @classmethod
    def validate_against_template(meta_cls, new_cls, template_cls):
        """
        Validates that a new WorkNode class conforms to the method signatures of a template class.
        """
        methods_to_check = ["__init__", "_run", "_try_and_skip", "fill_output_artifacts"]

        for method_name in methods_to_check:
            template_method = getattr(template_cls, method_name, None)
            new_method = getattr(new_cls, method_name, None)

            if not new_method:
                raise WorkNodeError(f"WorkNode class '{new_cls.__name__}' must implement the '{method_name}' method.")

            if not inspect.isfunction(new_method):
                continue

            template_sig = inspect.signature(template_method)
            new_sig = inspect.signature(new_method)

            meta_cls.compare_signatures(new_cls.__name__, method_name, new_sig, template_sig)

    @classmethod
    def compare_signatures(meta_cls, cls_name, method_name, new_sig, template_sig):
        """
        Compares two method signatures for compatibility.
        The new signature must accept all arguments of the template signature.
        Extra arguments in the new signature must be keyword-only or have default values.
        """
        template_params = template_sig.parameters
        new_params = new_sig.parameters

        # Check that all parameters from template are in new signature
        for param_name, template_param in template_params.items():
            if param_name == "self":
                continue
            if param_name not in new_params:
                raise WorkNodeError(
                    f"Method '{method_name}' in '{cls_name}' is missing parameter '{param_name}' "
                    f"from template signature."
                )

            new_param = new_params[param_name]

            # A required parameter in template cannot become optional in new signature for positional args
            if (
                template_param.default is inspect.Parameter.empty
                and new_param.default is not inspect.Parameter.empty
                and template_param.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
            ):
                raise WorkNodeError(
                    f"Parameter '{param_name}' in '{cls_name}.{method_name}' has a default value, "
                    f"but is a required positional argument in the template."
                )

        # Check that new parameters are acceptable
        for param_name, new_param in new_params.items():
            if param_name == "self":
                continue
            if param_name not in template_params:
                if (
                    new_param.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
                    and new_param.default is inspect.Parameter.empty
                ):
                    raise WorkNodeError(
                        f"New parameter '{param_name}' in '{cls_name}.{method_name}' must be keyword-only "
                        f"or have a default value."
                    )

    @classmethod
    def _get_init(meta_cls: Type[type], cls_name: str, cls_dict: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Retrieves the __init__ parameters for a class. [Docstring Copied & Verified]

        This method inspects the `__init__` method of the class and extracts
        information about its parameters, including their names, kinds, annotations,
        and default values.

        Args:
            meta_cls (type): The metaclass.
            cls_name (str): The name of the class.
            cls_dict (dict): The class dictionary containing its attributes.

        Returns:
            list: A list of dictionaries, each containing information about a parameter.
                  Each dictionary has the following keys:
                  - 'name': The name of the parameter.
                  - 'kind': The kind of the parameter (e.g., positional, keyword).
                  - 'annotation': The annotation of the parameter, if any.
                  - 'default': The default value of the parameter, if any.

        Raises:
            ValueError: If the `__init__` method's signature cannot be determined or parsed.
        """
        init_method = cls_dict.get("__init__")
        if init_method is None:
            init_method = getattr(cls_dict, "__init__", None)

        params_info = []
        if init_method and init_method is not object.__init__:
            try:
                sig = inspect.signature(init_method)
                for param_name, param_obj in sig.parameters.items():
                    # Skip 'self', 'cls', etc. attributes
                    is_bound_method_arg = param_name in ("self", "cls") and param_obj.kind in (
                        inspect.Parameter.POSITIONAL_OR_KEYWORD,
                        inspect.Parameter.POSITIONAL_ONLY,
                    )
                    if is_bound_method_arg and not params_info:  # Only skip if first arg
                        continue

                    params_info.append(
                        {
                            "name": param_obj.name,
                            "kind": param_obj.kind.description,
                            "annotation": None
                            if param_obj.annotation is inspect.Parameter.empty
                            else param_obj.annotation,
                            "default": inspect.Parameter.empty
                            if param_obj.default is inspect.Parameter.empty
                            else param_obj.default,
                        }
                    )
            except (ValueError, TypeError) as e:
                raise ValueError(f"Could not determine/parse __init__ signature for class '{cls_name}'") from e
        return params_info

    @classmethod
    def get_work_node_by_name(meta_cls, name: str) -> Type:
        if name not in meta_cls._name:
            raise WorkNodeError(f"WorkNode with name '{name}' not found in registry.")
        return meta_cls._name[name]

    @classmethod
    def get_work_node_by_identifier(meta_cls, prefix_match: str, suffix: str, tags: tuple = tuple()) -> Type:
        """
        Retrieves a WorkNode class by matching prefix, suffix, and tags.
        """
        # Iterate through stored identifiers (prefix, suffix, tags)
        for identifier_key, work_node_type in meta_cls._identifiers.items():
            stored_prefix = identifier_key[0]
            stored_suffix = identifier_key[1]
            stored_tags = identifier_key[2]

            # Check for match based on original logic (exact suffix/tags, startswith prefix)
            if suffix == stored_suffix and prefix_match.startswith(stored_prefix) and tags == stored_tags:
                return work_node_type

        # Use the new UnknownWorkNodeError exception
        raise UnknownWorkNodeError(
            f"WorkNode matching identifier with prefix start '{prefix_match}', "
            f"suffix '{suffix}', and tags {tags} not found."
        )

    @classmethod
    def get_work_node_name(meta_cls, class_or_name: Union[str, Type]) -> str:
        """Gets the registered name for a WorkNode class or verifies a name."""
        # noinspection PyUnreachableCode
        if isinstance(class_or_name, str):
            name = class_or_name
            if name not in meta_cls._name:
                raise KeyError(f"Class named '{name}' is not part of the work_node registry.")
        elif isinstance(class_or_name, type):
            cls = class_or_name
            name = cls.__name__
            # Verify it's in the registry
            if name not in meta_cls._name or meta_cls._name[name] is not cls:
                raise KeyError(f"Class object {cls} is not part of the work_node registry.")
        else:
            assert False, "This should be unreachable. Input must be a class name (str), or a class object"
        return name

    @classmethod
    def get_init_params(meta_cls, class_or_name: Union[str, Type]) -> List[Dict[str, Any]]:
        """
        Retrieves the list of initialization parameters for a WorkNode class
        identified by name or class object.
        """
        # Use the renamed getter for the name
        name = meta_cls.get_work_node_name(class_or_name)
        try:
            params = meta_cls._init_params[name]
            # Return a copy to prevent external modification? Original didn't.
            return params
        except KeyError as e:
            # This implies an internal inconsistency if name was validated but params are missing
            raise KeyError(
                f"Class '{name}' found in registry but missing __init__ params. This shouldn't happen."
            ) from e

    @classmethod
    def create_work_node_instance_by_name(meta_cls, class_name: str, *args, **kwargs):
        """Creates an instance of a WorkNode class using its name."""
        # Use the renamed getter
        cls = meta_cls.get_work_node_by_name(class_name)
        try:
            # Instantiate the WorkNode class
            return cls(*args, **kwargs)
        except TypeError as e:
            # Provide helpful error message including signature
            err_msg = f"Error creating instance of WorkNode '{cls.__name__}': {e} \n" + meta_cls.display_signature(cls)
            raise TypeError(err_msg) from e

    @classmethod
    def create_instance_by_identifier(meta_cls, prefix_match: str, suffix: str, tags: tuple = tuple(), *args, **kwargs):
        """Creates an instance of a WorkNode class using its identifier components."""
        # Use the renamed getter
        cls = meta_cls.get_work_node_by_identifier(prefix_match, suffix, tags)
        try:
            # Instantiate the WorkNode class
            return cls(*args, **kwargs)
        except TypeError as e:
            # Provide helpful error message including signature
            err_msg = (
                f"Error creating instance of WorkNode '{cls.__name__}' "
                f"(matched by identifier: prefix_start='{prefix_match}', suffix='{suffix}', tags={tags}): {e} \n"
                + meta_cls.display_signature(cls)
            )
            raise TypeError(err_msg) from e

    @classmethod
    def create_work_node_instance_by_filename(meta_cls, filepath: Path, *args, **kwargs):
        """
        Creates an instance of a WorkNode class associated with a filename,
        determining the class via prefix/suffix/tags derived from the path.
        """
        name, suffix = filepath.stem, filepath.suffix
        # Attempt to get tags from kwargs if provided, otherwise match without tags (or default tags)
        tags = kwargs.get("tags")
        # Use the renamed getter
        cls = meta_cls.get_work_node_by_identifier(name, suffix, tags)
        try:
            # Instantiate the WorkNode, potentially passing the filepath itself
            # (Original passed filepath as first arg implicitly, replicating)
            return cls(filepath, *args, **kwargs)
        except TypeError as e:
            # Provide helpful error message including signature
            err_msg = (
                f"Error creating instance of WorkNode '{cls.__name__}' "
                f"(matched by filename: '{filepath.name}'): {e} \n" + meta_cls.display_signature(cls)
            )
            raise TypeError(err_msg) from e

    # noinspection DuplicatedCode
    @classmethod
    def display_signature(meta_cls, class_or_name: Union[str, Type]) -> str:
        """Generates a string representation of the class's __init__ signature."""
        # Implementation Copied & Adapted - No 'artifact' specific terms needed here
        # except in potential error messages from getters, which are handled.
        try:
            # Use the renamed getter to validate and get name
            name = meta_cls.get_work_node_name(class_or_name)
            params_info = meta_cls.get_init_params(name)

            # If no params (besides self/cls), indicate that
            if not params_info:
                return f"\nInitialization signature for {name}\n  __init__(self)"  # Simplified message

            parts = []
            has_var_positional = False
            for param in params_info:
                part = param["name"]
                if param["annotation"]:
                    annotation_name = getattr(param["annotation"], "__name__", repr(param["annotation"]))
                    part += f": {annotation_name}"
                if param["default"] is not inspect.Parameter.empty:
                    default_repr = repr(param["default"])
                    part += f" = {default_repr}"

                kind = param["kind"]
                if kind == "variable positional":
                    part = "*" + part
                    has_var_positional = True
                elif kind == "variable keyword":
                    part = "**" + part
                elif kind == "keyword only" and not has_var_positional and "*" not in parts:
                    prev_param_idx = params_info.index(param) - 1
                    if prev_param_idx < 0 or params_info[prev_param_idx]["kind"] != "variable positional":
                        parts.append("*")
                elif kind == "positional only":
                    next_param_idx = params_info.index(param) + 1
                    if next_param_idx < len(params_info) and params_info[next_param_idx]["kind"] != "positional only":
                        part += " /"

                parts.append(part)

            # Format the output string
            output_msg = f"""
            Initialization signature for {name}
            __init__(self, {", ".join(parts)})
            """
            return output_msg.strip()  # Remove leading/trailing whitespace

        except Exception as e:
            # Catch potential errors during name/param lookup or formatting
            return f"Could not display signature for {class_or_name}. Error: {e}"


class BaseWorkNode(metaclass=WorkNodeRegistryMeta):
    min_cores: int = 1
    min_memory: int = 16
    max_systems: int = 0
    prefix: dict[str, str] = {}
    suffix: dict[str, str] = {}
    tags: dict[str, tuple[str, ...]] = tuple()
    takes_multiple_artifacts: bool = False

    def __init__(
        self,
        wnid: str,
        *args,
        root_dir: Optional[dirpath_t] = None,
        systems: Optional[Sequence[str]] = None,
        out_dir_template="{id}_{nodename}_WorkNode",
        include: Optional[Sequence[str]] = None,
        exclude: Optional[Sequence[str]] = None,
        logger: Union[logging.Logger, str, bool] = "file",
        logging_level: Optional[int] = None,
        logging_filemode: str = "w",
        skippable: Optional[bool] = None,
        command: Optional[BaseCommand] = None,
        command_str: str = "DefaultCommand",
        remote_server: Optional[str] = None,
        remote_base_dir: Optional[str] = None,
        min_cores: int = 1,
        min_memory: int = 16,
        **kwargs,
    ) -> None:
        self.id = wnid
        # When run in a pipeline, `root_dir` will be the root directory for the entire workflow
        self.root_dir = root_dir
        # When run in a pipeline, `cwd` will be the system dir
        self.cwd: Optional[dirpath_t] = None
        # When run in a pipeline, `work_dir` will be the node's working directory, inside the system directory
        self.work_dir: Optional[dirpath_t] = None
        self.out_dirname = out_dir_template.format(id=self.id, nodename=self.__class__.__name__)
        self.out_dir = None
        self.include = include
        self.exclude = exclude
        self.skippable = skippable
        self.systems = systems

        self.status = WorkNodeStatus.PENDING
        # @worknodehelper decorator will set these:
        self.input_artifacts: Optional[Union[ArtifactContainer, BatchArtifacts]] = None
        self.output_artifacts: Optional[Union[ArtifactContainer, BatchArtifacts]] = None
        self.artifact_map: Optional[dict[str, str]] = None
        self.artifact_builder: Optional[dict[str, type]] = None
        self.expects: Optional[tuple[str]] = None
        self.gives: Optional[tuple[str]] = None

        self.logger = logger
        if not logger:
            self.node_logger = get_null_logger()
        elif isinstance(logger, logging.Logger):
            self.node_logger = logger
        elif isinstance(logger, str) and logger == "file":
            # Will be set up later by the WorkNode itself
            self.node_logger = None
        else:
            raise WorkNodeError(f"Bad input logger: {logger}. Must be either None, a logging.Logger or 'file'.")
        self.logging_level = logging_level
        self.logging_filemode = logging_filemode

        self.command = command
        self.command_str = command_str
        self.remote_server = remote_server
        self.remote_base_dir = remote_base_dir

        self.min_cores = min_cores
        self.min_memory = min_memory

        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.elapsed_time: Optional[float] = None

    def run(self, *args, **kwargs) -> None:
        raise NotImplementedError

    def _run(self, *args, **kwargs) -> None:
        raise NotImplementedError

    def set_systems(self, systems: Sequence[str]) -> None:
        """
        Set the systems for the work node.
        """
        self.systems = systems
        if self.include:
            if not set(self.include) <= set(systems):
                err_msg = f"Included systems {self.include} are not part of the available systems {systems}."
                self.logger.error(err_msg)
                raise WorkNodeError(err_msg)

            self.systems = list(self.include)
        elif self.exclude:
            self.systems = list(set(systems) - set(self.exclude))

    def _try_and_skip(self, *args, **kwargs) -> Any:
        raise NotImplementedError

    # Quite hacky, but it works.
    def __str__(self) -> str:
        return str(type(self)).split("'")[1].split(".")[-1] + f" - {self.id}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id='{self.id}', status={self.status.name})"

    def __len__(self) -> int:
        return len(self.output_artifacts)

    # Define equality based on the 'id' attribute
    def __eq__(self, other):
        if not isinstance(other, BaseWorkNode):
            return NotImplemented
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)


class BaseSingleWorkNode(BaseWorkNode):
    min_cores: int = 1
    min_gpus: int = 0

    def run(
        self,
        input_artifacts: ArtifactContainer,
        *args,
        cwd: dirpath_t,
        sysname: str,
        **kwargs,
    ) -> ArtifactContainer:
        raise NotImplementedError

    def _run(
        self,
        *args,
        cwd: dirpath_t,
        sysname: str,
        **kwargs,
    ) -> ArtifactContainer:
        raise NotImplementedError


class BaseBatchWorkNode(BaseWorkNode):
    def run(
        self,
        input_artifacts: BatchArtifacts,
        *args,
        cwd: dirpath_t,
        systems: dict[str, dirpath_t],
        **kwargs,
    ) -> BatchArtifacts:
        raise NotImplementedError

    def _run(
        self,
        *args,
        cwd: dirpath_t,
        **kwargs,
    ) -> BatchArtifacts:
        raise NotImplementedError

    @staticmethod
    def filter_artifacts(
        input_artifacts: BatchArtifacts,
        attr: str,
        val: Any,
    ) -> BatchArtifacts:
        """
        Filter artifacts based on the value of an attribute.
        """
        filtered_data = {}
        for system_name, art_container in input_artifacts.items():
            retained_artifacts = [
                art for arts in art_container for art in arts if hasattr(art, attr) and getattr(art, attr) == val
            ]
            if retained_artifacts:
                filtered_data[system_name] = ArtifactContainer(art_container.id, retained_artifacts)

        return BatchArtifacts(input_artifacts.id, filtered_data)


class WorkNodeStatus(Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
