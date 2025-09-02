import inspect
from collections import deque
from collections.abc import Mapping
from pathlib import Path
from typing import Union, Sequence, Optional, Any, Iterator

from typing_extensions import override

from amberflow.primitives import (
    ArtifactError,
    UnknownArtifactError,
    filepath_t,
    FileHandle,
    MissingTagsError,
    NonmatchingTagsError,
    DirHandle,
)

__all__ = (
    "BaseArtifact",
    "ArtifactRegistry",
    "ArtifactContainer",
    "BatchArtifacts",
    "BaseArtifactFile",
    "BaseArtifactDir",
)


# noinspection PyMethodParameters
class ArtifactRegistry(type):
    """
    Metaclass to register artifacts and Factory as well.
    It inspects and stores __init__ parameters.
    requiring unique 'prefix' and 'suffix'
    class attributes for identification and lookup.
    """

    # Registry mapping Artifact class name to class object
    name: dict[str, type] = {}
    # Registry mapping identifier tuple (prefix, suffix, tags) to class object
    _presuffixtags: dict[tuple[str, str, tuple], type] = {}
    # Registry mapping identifier tuple (prefix, suffix) to tags. Used just to avoid collisions between artifacts' tags
    _presuffix: dict[tuple[str, str], set[tuple[str]]] = {}
    # Registry mapping Artifact class name to its __init__ parameter info list
    _init_params: dict[str, Sequence] = {}

    # Registry mapping Base Artifact class name to class object
    base: dict[str, type] = {}

    # Registry mapping reference structures to their parent types, that is, the non-reference structure type.
    # Eg: ComplexProteinLigandStructureReferenceRestart -> ComplexProteinLigandStructureRestart
    reference_map: dict[type, type] = {}

    # If you have a base class+tags you can build an object with these 2 data structures
    # Layout: {ParentClass: {frozenset(tags): ChildClass}, ...}.
    _base_tags_map_concrete: dict[type, dict[frozenset[str], type]] = {}
    _inheritance_graph: dict[type, set[type]] = {}

    def __new__(meta_cls, cls_name, bases, cls_dict):
        new_cls = super().__new__(meta_cls, cls_name, bases, cls_dict)

        # We only care about classes inheriting from a registered base
        if bases:
            # Register every class, regardless of whether it has tags.
            meta_cls._inheritance_graph.setdefault(bases[0], set()).add(new_cls)

        if cls_name.startswith("Base"):
            # ArtifactContainer uses this map of base classes between their string form and the type itself.
            meta_cls.base[cls_name] = new_cls
        else:
            # Enforce unique Artifact names
            if cls_name in meta_cls.name:
                raise ArtifactError(f"Artifact {cls_name} already registered")
            meta_cls.name[cls_name] = new_cls

            # Fill up _presuffix and _presuffixtags
            ArtifactRegistry.register_presuffix_presuffixtags(cls_name, cls_dict, new_cls)

            # Fill up _base_tags_map_concrete, _inheritance_graph
            if bases:
                ArtifactRegistry.register_inheritance_tags(bases[0], cls_dict, new_cls)

        # Get the signature of the __init__ method
        meta_cls._init_params[cls_name] = meta_cls._get_init(cls_name, cls_dict)

        # Helper map to create reference structures from non-reference structures.
        if "Reference" in cls_name:
            nonreference_structure_typename = cls_name.replace("Reference", "")
            if nonreference_structure_typename in ArtifactRegistry.name:
                meta_cls.reference_map[ArtifactRegistry.name[nonreference_structure_typename]] = new_cls

        return new_cls

    @classmethod
    def register_inheritance_tags(meta_cls, parent, cls_dict, new_cls):
        # Only register classes that explicitly define a 'tags' attribute
        tags = cls_dict.get("tags")
        if tags is not None:
            tag_key = frozenset(tags)
            meta_cls._base_tags_map_concrete.setdefault(parent, {})
            if tag_key in meta_cls._base_tags_map_concrete[parent]:
                # Multiple concrete classes under this parent class that share tags. It's not possible to build these
                # classes with `_base_tags_map_concrete`
                del meta_cls._base_tags_map_concrete[parent][tag_key]
            else:
                meta_cls._base_tags_map_concrete[parent][tag_key] = new_cls

    @classmethod
    def register_presuffix_presuffixtags(meta_cls, cls_name, cls_dict, new_cls):
        try:
            # Only user file artifacts have a prefix and suffix. `tags` are optional.
            prefix = cls_dict["prefix"]
            suffix = cls_dict["suffix"]
        except KeyError:
            # Artifact not associated to a file
            return
        tags = cls_dict.get("tags", tuple())
        presuffix = (prefix, suffix)
        try:
            old_tags = meta_cls._presuffix[presuffix]
            if tags in old_tags:
                raise ArtifactError(
                    f"Artifact {cls_name} already registered with prefix : {cls_dict['prefix']}, "
                    f"suffix {cls_dict['suffix']}, and tags {cls_dict['tags']}"
                )
            # Add new tags to the existing prefix-suffix pair
            meta_cls._presuffix[presuffix].add(tags)
        except KeyError:
            # The (prefix, suffix) pair is not registered yet
            meta_cls._presuffix[presuffix] = {tags}

        presuffixtag = (prefix, suffix, tags)
        meta_cls._presuffixtags[presuffixtag] = new_cls

    @classmethod
    def concrete_artifact(cls, search_root: type, tags: set[str]) -> Optional[type]:
        """
        Finds a concrete class in the inheritance tree with a matching set of tags.
        This search correctly traverses the entire descendant graph from the root.
        """
        tag_key = frozenset(tags)

        queue = deque([search_root])
        visited = set()

        while queue:
            current_class = queue.popleft()
            if current_class in visited:
                continue
            visited.add(current_class)

            # First, check for a direct child with matching tags for a fast answer
            children_with_tags = cls._base_tags_map_concrete.get(current_class, {})
            if tag_key in children_with_tags:
                return children_with_tags[tag_key]

            # If no direct match, get ALL children from the inheritance graph
            # and add them to the queue to continue the search downwards.
            all_children = cls._inheritance_graph.get(current_class, set())
            queue.extend(all_children)

        return None

    @classmethod
    def _get_init(meta_cls: type, cls_name, cls_dict):
        """
        Retrieves the __init__ parameters for a class.

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
                    if is_bound_method_arg and params_info == []:  # Only skip if first arg
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
                raise ValueError(f"Warning: Could not determine/parse __init__ signature for class '{cls_name}'") from e

        return params_info

    @classmethod
    def get_artifact_by_name(meta_cls, name: str) -> type:
        if name not in meta_cls.name:
            raise ArtifactError(f"Artifact with {name} not found")
        return meta_cls.name[name]

    @classmethod
    def get_artifact_by_presuffix(meta_cls, name: str, suffix: str, tags: Optional[tuple] = None) -> type:
        """
        Retrieves an Artifact class by matching prefix, suffix, and, if necessary, tags.
        """

        matching_pressufix_types = {}
        # TODO: actually use this `relaxed_matching_pressufix_types`. Perhaps to give suggestions?
        relaxed_matching_pressufix_types = {}
        for presuffix, artifact_type in meta_cls._presuffixtags.items():
            if suffix == presuffix[1]:
                if name.split("_")[0] == presuffix[0]:
                    matching_pressufix_types[presuffix] = artifact_type
                else:
                    if name[: len(presuffix[0])] == presuffix[0]:
                        relaxed_matching_pressufix_types[presuffix] = artifact_type
        n_matching = len(matching_pressufix_types)
        if n_matching > 1:
            if tags is None:
                matching_str = " ; ".join(
                    [
                        f"{artifact_type.__name__}({presuffix})"
                        for presuffix, artifact_type in matching_pressufix_types.items()
                    ]
                )
                raise MissingTagsError(
                    f"Artifact with name {name} and suffix {suffix} matches multiple types: {matching_str} and no tags were provided."
                )

            for presuffix, artifact_type in matching_pressufix_types.items():
                if set(presuffix[2]) == set(tags):
                    return artifact_type
            matching_str = " ; ".join(
                [
                    f"{artifact_type.__name__}({presuffix})"
                    for presuffix, artifact_type in matching_pressufix_types.items()
                ]
            )
            raise NonmatchingTagsError(
                f"Artifact with name {name} and suffix {suffix} matches multiple types: {matching_str}, "
                f"but input tags ('{tags}') don't match any of them."
            )

        if n_matching == 0:
            raise UnknownArtifactError(
                f"Artifact with name {name} and suffix {suffix} not found. You may need to define a new Artifact"
            )
        else:
            return next(iter(matching_pressufix_types.values()))

    @classmethod
    def get_artifact_name(meta_cls, class_or_name: Union[str, type]) -> str:
        # noinspection PyUnreachableCode
        if isinstance(class_or_name, str):
            name = class_or_name
            if name not in meta_cls.name:
                raise KeyError(f"Class named {name} is not part of the artifact registry.")
        elif isinstance(class_or_name, type):
            cls = class_or_name
            # Verify it's in the registry
            if cls.__name__ not in meta_cls.name:
                raise KeyError(f"Class object {cls} is not part of the artifact registry.")
            name = cls.__name__
        else:
            raise TypeError("Input must be a class name (str), or a class object")
        return name

    @classmethod
    def get_init_params(meta_cls, class_or_name: Union[str, type]):
        """
        Retrieves the list of initialization parameters for a class identified
        by name or class object.
        """
        name = meta_cls.get_artifact_name(class_or_name)
        try:
            params = meta_cls._init_params[name]
        except KeyError as e:
            raise KeyError(f"Class {name} doesn't have __init__ params. This shouldn't happen.") from e
        return params

    @classmethod
    def create_instance_by_name(meta_cls, class_name: str, *args, **kwargs):
        cls = meta_cls.get_artifact_by_name(class_name)
        try:
            return cls(*args, **kwargs)
        except TypeError as e:
            err_msg = f"Error creating instance of {cls.__name__}: {e} \n" + meta_cls.display_signature(cls)
            raise TypeError(err_msg) from e

    @classmethod
    def create_instance_by_presufix(meta_cls, name, suffix, *args, **kwargs):
        cls = meta_cls.get_artifact_by_presuffix(name, suffix)
        try:
            return cls(*args, **kwargs)
        except TypeError as e:
            err_msg = (
                f"Error creating instance of {cls.__name__}, with filename {name}{suffix}: {e} \n"
                + meta_cls.display_signature(cls)
            )
            raise TypeError(err_msg) from e

    @classmethod
    def create_instance_by_filename(meta_cls, filepath: Path, *args, **kwargs):
        name, suffix = filepath.stem, filepath.suffix
        cls = meta_cls.get_artifact_by_presuffix(name, suffix, kwargs.get("tags"))
        try:
            return cls(filepath, *args, **kwargs)
        except TypeError as e:
            err_msg = (
                f"Error creating instance of {cls.__name__}, with filename {name}{suffix}: {e} \n"
                + meta_cls.display_signature(cls)
            )
            raise TypeError(err_msg) from e

    # noinspection DuplicatedCode
    @classmethod
    def display_signature(meta_cls, class_or_name: Union[str, type]) -> str:
        """Prints the initialization signature for a registered class."""
        try:
            name = meta_cls.get_artifact_name(class_or_name)
            params_info = meta_cls.get_init_params(name)

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
                    # Check if previous param was not var positional
                    prev_param_idx = params_info.index(param) - 1
                    if prev_param_idx < 0 or params_info[prev_param_idx]["kind"] != "variable positional":
                        parts.append("*")
                elif kind == "positional only":
                    # Check if '/' separator is needed
                    next_param_idx = params_info.index(param) + 1
                    if next_param_idx < len(params_info) and params_info[next_param_idx]["kind"] != "positional only":
                        part += " /"  # Add separator after last positional-only arg

                parts.append(part)

            output_msg = f"""
            Initialization signature for {name}
            __init__({", ".join(parts)})
            """
            return output_msg

        except Exception as e:
            raise e


class BaseArtifact(metaclass=ArtifactRegistry):
    name: Optional[str] = None

    @staticmethod
    def _check_file(filepath: Path, prefix: str, suffix: str) -> None:
        if filepath.suffix != suffix:
            raise ArtifactError(f"File {filepath} is not a {suffix} file")
        if filepath.name[0 : len(prefix)] != prefix:
            raise ArtifactError(f"File {filepath} is not a {prefix} file")


# noinspection PyUnresolvedReferences
class ArtifactContainer:
    """
    An immutable container class for managing a collection of artifacts.

    Attributes:

        id (str): Unique identifier for the container.
        _hash (int): Cached hash value of the container identifier.
        _data (dict[str, list[BaseArtifact]]): Internal storage mapping artifact type names to a list of artifact instances.
        _initialized (bool): Flag indicating whether the container has been initialized.
    Methods:
        __setattr__(name, value): Prevents modification of attributes after initialization.
        __delattr__(name): Prevents deletion of attributes after initialization.
    """

    __slots__ = ("id", "_hash", "_data", "_initialized")

    def __init__(self, art_id: str, artifacts: Sequence[BaseArtifact]):
        super().__setattr__("_initialized", False)
        super().__setattr__("id", art_id)
        super().__setattr__("_hash", hash(art_id))

        data: dict[str, list[BaseArtifact]] = {}
        for artifact in artifacts:
            type_name = type(artifact).__name__
            if type_name not in data:
                data[type_name] = []
            data[type_name].append(artifact)
        super().__setattr__("_data", data)
        super().__setattr__("_initialized", True)

    def __setattr__(self, name: str, value: BaseArtifact) -> None:
        if self._initialized:
            raise AttributeError(f"'{self.__class__.__name__}' instances are immutable.")
        return super().__setattr__(name, value)

    # Define custom serialization methods for pickling and unpickling, since __slots__ + immutability are being used
    def __getstate__(self) -> dict[str, Any]:
        state = {}
        for slot in self.__slots__:
            if hasattr(self, slot):
                state[slot] = getattr(self, slot)
        return state

    def __setstate__(self, state: dict[str, Any]) -> None:
        for key, value in state.items():
            super().__setattr__(key, value)
        object.__setattr__(self, "_initialized", True)

    def __delattr__(self, name: str) -> None:
        raise AttributeError(f"'{self.__class__.__name__}' instances are immutable.")

    def __getitem__(self, key):
        if key.startswith("Base"):
            base_class = ArtifactRegistry.base[key]
            all_artifacts = [art for sublist in self._data.values() for art in sublist]
            matching_arts = [art for art in all_artifacts if isinstance(art, base_class)]
            if not matching_arts:
                raise KeyError(f"No subtype of {key} found in {self.id} - Available artifacts: {self.keys()}")
            return matching_arts[0] if len(matching_arts) == 1 else matching_arts

        try:
            matching_list = self._data[key]
            return matching_list[0] if len(matching_list) == 1 else matching_list
        except KeyError:
            raise KeyError(f"Artifact type '{key}' not found in {self.id}. Available types: {list(self.keys())}")

    def __iter__(self) -> Iterator[BaseArtifact]:
        return iter(art for sublist in self._data.values() for art in sublist)

    def __len__(self) -> int:
        return sum(len(sublist) for sublist in self._data.values())

    def __str__(self) -> str:
        lines = []
        for art_type, artifacts in self._data.items():
            if len(artifacts) == 1:
                lines.append(f"{art_type}: {artifacts[0]}")
            else:
                lines.append(f"{art_type}:")
                for i, artifact in enumerate(artifacts):
                    lines.append(f"  [{i}]: {artifact}")
        return "\n".join(lines)

    def __repr__(self) -> str:
        return self._data.__repr__()

    def __hash__(self):
        return self._hash

    def __or__(self, other):
        if not isinstance(other, ArtifactContainer):
            raise TypeError(f"Cannot combine {type(self)} with {type(other)}")

        all_self_artifacts = [art for sublist in self._data.values() for art in sublist]
        # noinspection PyProtectedMember
        all_other_artifacts = [art for sublist in other._data.values() for art in sublist]

        result = ArtifactContainer(self.id, all_self_artifacts + all_other_artifacts)
        return result

    def __contains__(self, key: Union[str, BaseArtifact]):
        if isinstance(key, str):
            if key.startswith("Base"):
                try:
                    # Look up the actual base class from the registry
                    base_class = ArtifactRegistry.base[key]
                    # Check if any artifact in the container is an instance of this base class
                    for artifact in self:
                        if isinstance(artifact, base_class):
                            return True
                    return False
                except KeyError:
                    # The provided base class name doesn't exist in the registry
                    return False
            else:
                # Case 2: Check for a specific class name in the data keys
                return key in self._data
        return False

    def values(self):
        # return [art for sublist in self._data.values() for art in sublist]
        return self._data.values()

    def keys(self):
        return self._data.keys()

    def items(self):
        return self._data.items()

    def get(self, key, default=None) -> Union[BaseArtifact, list[BaseArtifact], None]:
        try:
            return self[key]
        except KeyError:
            return default

    def get_as_list(self, key, default=None) -> list[BaseArtifact]:
        element = self.get(key, default)
        if isinstance(element, list):
            return element
        if element is default:
            return default
        else:
            return [element]


class BatchArtifacts(Mapping):
    """A container class for managing collections of ArtifactContainers.

    The class is not immutable, but it doesn't make it easy to modify it.

    Attributes:
        id (str): Unique identifier for this batch of artifacts.
        _data (dict[str, ArtifactContainer]): Internal storage of artifact containers.
        _hash (int): Cached hash value of the batch identifier.

    Methods:
        __or__(other): Combines two BatchArtifacts instances into a new one.
        update_inplace(other): Updates the current instance with artifacts from another BatchArtifacts.
        get_selection(selection, artifact_types, throw_if_missing, unique): Returns a new BatchArtifacts
            with selected systems and artifacts.
    """

    __slots__ = ("id", "_data", "_hash")

    def __init__(self, art_id: str, data: dict[str, ArtifactContainer]):
        self.id = art_id
        self._data = {k: v for k, v in data.items()}
        self._hash: int = hash(self.id)

    @classmethod
    def from_another(cls, other: "BatchArtifacts"):
        return cls(other.id, other._data)

    @override
    def __getitem__(self, __key):
        return self._data[__key]

    @override
    def __iter__(self) -> Iterator[ArtifactContainer]:
        return iter(self._data.values())

    @override
    def __len__(self) -> int:
        return len(self._data)

    def values(self):
        return self._data.values()

    def keys(self):
        return self._data.keys()

    def items(self):
        return self._data.items()

    def get(self, key, default=None):
        return self._data.get(key, default)

    def __or__(self, other: "BatchArtifacts") -> "BatchArtifacts":
        result = BatchArtifacts(self.id, self._data.copy() | other._data)
        return result

    def update_inplace(self, other: "BatchArtifacts") -> "BatchArtifacts":
        self._data.update(other._data)
        return self

    def get_selection(
        self,
        *,
        artifact_types: Sequence[type] = (BaseArtifact,),
        selection: Optional[Sequence[str]] = None,
        throw_if_missing: bool = True,
        unique: bool = False,
    ) -> "BatchArtifacts":
        """
        Returns a new BatchArtifacts instance with only the selected systems and artifacts of the specified type.
        """
        if selection is None:
            selection = set(self.keys())

        if throw_if_missing:
            # noinspection PyTypeChecker
            selected_data = {
                sysname: ArtifactContainer(
                    self.id,
                    [
                        art
                        for arts in self._data[sysname].values()
                        for art in arts
                        if isinstance(art, required_art_type)
                    ],
                )
                for sysname in selection
                for required_art_type in artifact_types
            }
        else:
            # noinspection PyTypeChecker
            selected_data = {
                sysname: ArtifactContainer(
                    self.id,
                    [
                        art
                        for arts in self._data[sysname].values()
                        for art in arts
                        if isinstance(art, required_art_type)
                    ],
                )
                for sysname in selection
                for required_art_type in artifact_types
            }
        if unique:
            for artifacts in selected_data.values():
                if len(artifacts) != 1:
                    raise ArtifactError(f"Found {len(artifacts)} artifacts of type {artifact_types} in {self}")
        return BatchArtifacts(self.id, selected_data)

    def __str__(self) -> str:
        return "\n".join(f"{sysname}: {artifact}" for sysname, artifact in self._data.items())

    def __repr__(self) -> str:
        return self._data.__repr__()

    def __hash__(self):
        return self._hash


class BaseArtifactFile(BaseArtifact):
    # noinspection PyUnusedLocal
    def __init__(self, filepath: filepath_t, *args, prefix, suffix, **kwargs) -> None:
        self.filepath = Path(FileHandle(filepath))
        self.name: str = self.filepath.stem[len(prefix) :]
        super()._check_file(self.filepath, prefix, suffix)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(filepath={self.filepath})"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(filepath={self.filepath})"

    def __fspath__(self) -> Union[str, bytes, Path]:
        return str(self.filepath)


class BaseArtifactDir(BaseArtifact):
    # noinspection PyUnusedLocal
    def __init__(self, filepath: filepath_t, *args, prefix, suffix, **kwargs) -> None:
        self.filepath = Path(DirHandle(filepath))
        self.name: str = self.filepath.stem[len(prefix) :]
        super()._check_file(self.filepath, prefix, suffix)

    def __str__(self) -> str:
        return str(self.filepath)

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
        new_path = self.filepath / key
        if new_path.is_file():
            return FileHandle(new_path)
        elif new_path.is_dir():
            return DirHandle(new_path, make=False)
        else:
            raise FileNotFoundError(f"{new_path} doesn't exist.")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(dirpath={self.filepath})"
