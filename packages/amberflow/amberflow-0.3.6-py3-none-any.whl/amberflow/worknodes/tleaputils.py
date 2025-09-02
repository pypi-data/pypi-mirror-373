from string import Template
from collections import UserDict


# noinspection PyProtectedMember
class TLeapSourcesGenerator(UserDict):
    """
    Holds the sources for Tleap and then builds the tLeap script header to load them.

    The order of the parameters in the dictionary determines the order of the
    lines in the generated script.
    """

    _LINE_MAP = {
        "water": "source leaprc.water.$water",
        "force_field": (
            "source leaprc.protein.ff$force_field",
            "source leaprc.phosaa$force_field",
            "loadamberparams frcmod.ff$force_field",
        ),
        "atom_type": "source leaprc.$atom_type",
        "water_frcmod": "loadamberparams frcmod.$water_frcmod",
        "ions_frcmod": "loadamberparams frcmod.$ions_frcmod",
    }

    SUPPORTS = {
        "water": ("opc", "tip3p", "tip4pew", "spce"),
        "ions": ("jc", "1lm_1264", "1lm_126", "234lm_1264", "234lm_126", "234lm_hfe", "234lm_iod"),
        "force_field": ("14SB", "19SB"),
        "atom_type": ("gaff", "gaff2"),
    }

    SOLVENT_TO_BOX = {
        "tip3p": "TIP3PBOX",
        "opc": "OPCBOX",
        "tip4pew": "TIP4PEWBOX",
        "spce": "SPCEBOX",
    }

    SOLVENT_ION_PAIR = {
        ("tip4pew", "jc"): "ionsjc_tip4pew",
        ("tip4pew", "1lm_1264"): "1lm_1264",
        ("tip4pew", "1lm_126"): "1lm_126",
        ("tip4pew", "234lm_1264"): "234lm_1264",
        ("tip4pew", "234lm_126"): "234lm_126",
        ("tip4pew", "234lm_hfe"): "234lm_hfe",
        ("tip4pew", "234lm_iod"): "234lm_iod",
    }
    SOLVENT_FRCMOD = {
        "tip4pew": "tip4pew",
    }

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            if k not in self.SUPPORTS:
                raise RuntimeError(f"Unrecognized keyword argument: {k}")
            if v not in self.SUPPORTS[k]:
                raise ValueError(f"Unsupported type for {k}: {type(v)}. Supported options: {self.SUPPORTS[k]}")

        if "water" in kwargs:
            if kwargs["water"] in self.SOLVENT_FRCMOD:
                kwargs["water_frcmod"] = self.SOLVENT_FRCMOD[kwargs["water"]]
            kwargs["box"] = self.SOLVENT_TO_BOX[kwargs["water"]]

        if (kwargs.get("water"), kwargs.get("ions")) in self.SOLVENT_ION_PAIR:
            kwargs["ions_frcmod"] = self.SOLVENT_ION_PAIR[(kwargs["water"], kwargs["ions"])]

        super().__init__(kwargs)

    def to_string(self) -> str:
        """Generates the tLeap script from the set parameters in their defined order."""
        lines = []

        for key in self.data.keys():
            if key in self._LINE_MAP:
                entry = self._LINE_MAP[key]
                if isinstance(entry, str):
                    lines.append(entry)
                elif len(entry) > 1:
                    lines.extend(entry)
                else:
                    raise ValueError(f"Unknown entry type. {entry=} of type: {type(entry)}")

        # Remove potential duplicates while preserving order
        unique_lines = list(dict.fromkeys(lines))

        template_string = "\n".join(unique_lines) + "\n"
        return Template(template_string).safe_substitute(self.data)

    # noinspection PyUnreachableCode
    def to_lines(self) -> list[str]:
        """Generates a list of tLeap script lines from the set parameters."""
        template_lines = []
        for key in self.data.keys():
            if key in self._LINE_MAP:
                entry = self._LINE_MAP[key]
                if isinstance(entry, str):
                    template_lines.append(entry)
                elif isinstance(entry, tuple):
                    template_lines.extend(entry)
                else:
                    raise ValueError(f"Unknown entry type. {entry=} of type: {type(entry)}")

        unique_templates = list(dict.fromkeys(template_lines))
        # Substitute the values into each template line
        substituted_lines = [Template(line).safe_substitute(self.data) for line in unique_templates]
        return substituted_lines

    def __str__(self) -> str:
        return self.to_string()

    def __iter__(self):
        """Allows the object to be used as an iterable (e.g., in list())."""
        yield from self.to_lines()
