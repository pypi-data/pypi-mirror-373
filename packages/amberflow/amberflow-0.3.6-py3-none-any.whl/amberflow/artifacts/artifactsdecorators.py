import copy
import inspect
import shutil
from pathlib import Path

from amberflow.artifacts import BaseArtifact
from amberflow.primitives import ArtifactError


def userartifact(cls: type) -> type:
    setattr(cls, "_is_user_artifact", True)
    return cls


def fileartifact(cls: type) -> type:
    """
    Class decorator to enforce proper file-based Artifacts:
    - The class must have attributes prefix, suffix, and tags.
    - __init__ must have a specific signature:
        - First argument after self must be 'filepath' (required, positional).
        - All subsequent arguments must be optional (have defaults, be
          keyword-only, *args, or **kwargs).
    And to help the user with helpful methods:
    -  copy_to(self, dest: str):
    """

    if not any([hasattr(base, "prefix") for base in cls.__mro__] + [hasattr(cls, "prefix")]):
        raise ArtifactError(f"User artifact {cls} must have a prefix (str) attribute")
    if not any([hasattr(base, "suffix") for base in cls.__mro__] + [hasattr(cls, "suffix")]):
        raise ArtifactError(f"User artifact {cls} must have a suffix (str) attribute")
    if not any([hasattr(base, "tags") for base in cls.__mro__] + [hasattr(cls, "tags")]):
        raise ArtifactError(f"User artifact {cls} must have a tags (tuple) attribute")
    if not issubclass(cls, BaseArtifact):
        raise ArtifactError(f"User artifact {cls} must inherit from BaseArtifact")

    init_method = getattr(cls, "__init__", None)

    if not init_method or not inspect.isfunction(init_method):
        raise TypeError(f"Class {cls.__name__} must have an __init__ method.")

    try:
        sig = inspect.signature(init_method)
        params = list(sig.parameters.values())
    except ValueError:
        # Handle cases like built-in types that might not have inspectable signatures
        raise TypeError(f"Could not inspect the signature of {cls.__name__}.__init__")

    if len(params) < 2:
        raise TypeError(
            f"{cls.__name__}.__init__ must accept at least one positional argument named 'filepath' after 'self'."
        )

    filepath_param = params[1]
    if filepath_param.name != "filepath":
        raise TypeError(
            f"{cls.__name__}.__init__ first argument after 'self' must be named 'filepath', not '{filepath_param.name}'."
        )

    # Check if 'filepath' is required (no default value) and positional/keyword capable
    is_positional_or_kw = filepath_param.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD
    has_no_default = filepath_param.default == inspect.Parameter.empty

    if not (is_positional_or_kw and has_no_default):
        raise TypeError(
            f"{cls.__name__}.__init__ parameter 'filepath' must be a required positional argument (no default value). Found kind={filepath_param.kind}, default={filepath_param.default!r}"
        )

    # 3. Check all subsequent parameters (from index 2 onwards)
    for i, param in enumerate(params[2:], start=2):
        if param.default == inspect.Parameter.empty and param.kind not in (
            inspect.Parameter.VAR_POSITIONAL,
            inspect.Parameter.VAR_KEYWORD,
        ):
            raise TypeError(
                f"{cls.__name__}.__init__ parameter '{param.name}' (at index {i}) "
                f"must be optional (have a default, be keyword-only, *args, or **kwargs). "
                f"Found kind={param.kind} with no default value."
            )

    # `copy_to` method for all file based artifacts
    def copy_to(self, dest: Path):
        """
        Copies associated files to a destination and returns a new artifact instance.

        Args:
            self (BaseArtifact): The artifact instance.
            dest (Path): The destination directory path.

        Returns:
            A new instance of the artifact class with updated filepath attributes.

        Raises:
            FileNotFoundError: If an attribute starting with 'filepath' points
                             to a non-existent file.
            OSError: If file copying fails (e.g., permissions).
            TypeError: If an attribute starting with 'filepath' is not a Path object.
        """
        if not dest.is_dir():
            raise TypeError(f"{dest} is not a valid directory")

        path_mapping = {}  # Maps original Path object -> new Path object
        # Find all the attributes that start with 'filepath'
        for attr_name, original_path in self.__dict__.items():
            if attr_name.startswith("filepath"):
                if not isinstance(original_path, Path):
                    raise ArtifactError(
                        f"Attribute '{attr_name}' starts with 'filepath' but is not a Path object (type: {type(original_path)})."
                    )
                if not original_path.is_file():
                    raise FileNotFoundError(f"Attribute '{attr_name}' points to non-existent file: {original_path}")

                # Only copy if we haven't copied this exact path object already
                if original_path not in path_mapping:
                    destination_path = dest / original_path.name
                    try:
                        shutil.copy2(original_path, destination_path)
                        path_mapping[attr_name] = destination_path
                    except Exception as e:
                        err_msg = f"Failed to copy {original_path} to {destination_path}: {e}"
                        raise RuntimeError(err_msg) from e

        new_instance = copy.deepcopy(self)
        # Update the filepath attributes on the new instance
        for attr_name, new_filepath in path_mapping.items():
            setattr(new_instance, attr_name, new_filepath)

        return new_instance

    # Inject the copy_to method to the class
    setattr(cls, "copy_to", copy_to)

    def change_base_dir(self, old_base: Path, new_base: Path) -> Path:
        """
        Changes the base directory of the artifact's filepath.

        Args:
            self (BaseArtifact): The artifact instance.
            old_base (Path): The current base directory path.
            new_base (Path): The new base directory path.
        """
        self.filepath = Path(new_base, Path(self.filepath).relative_to(old_base))
        return self.filepath

    # Inject the copy_to method to the class
    setattr(cls, "change_base_dir", change_base_dir)

    return cls
