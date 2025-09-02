import mmap
import warnings
from logging import Logger
from pathlib import Path
from string import Template
from typing import Optional

import numpy as np
from MDAnalysis import Universe, AtomGroup, Merge
from MDAnalysis.lib.distances import distance_array

from amberflow.artifacts.md import ComplexPeriodicBox, BinderPeriodicBox

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    # ignore `BiopythonDeprecationWarning` warning
    from MDAnalysis.analysis import align

from amberflow.artifacts import ArtifactContainer, BaseStructureFile, ArtifactRegistry
from amberflow.artifacts import BatchArtifacts
from amberflow.artifacts.structure import BinderLigandPDB, BaseComplexStructureFile, get_biomolecule
from amberflow.primitives import (
    filepath_t,
    dirpath_t,
    DEFAULT_RESOURCES_PATH,
)
from amberflow.worknodes import BaseBatchWorkNode, noderesource, worknodehelper, check_leap_log, TleapMixin, AddChainid

__all__ = ("BuildAFEBoxes", "BuildBoxes")

from amberflow.worknodes.worknodeutils import runiverse


def get_num_ions(input_file: filepath_t, concentration: float):
    """Get the number of ions needed for the system.

    Parameters
    ----------
    input_file : filepath_t
        The path to the input (pdb) file.
    concentration : float
        The concentration of the ions.

    Returns
    -------
    int
        The number of NA or CL ions.
    Raises
    ------
    ValueError
        If the concentration of ions is negative.
    """
    if not 0 < concentration < 1:
        raise ValueError("Invalid input concentration ({concentration}). Concentration must be between 0 and 1")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        u = Universe(input_file)
    num_waters = len(u.select_atoms("resname WAT").residues)
    num_ions = num_waters * concentration / 55.0  # 55.0 is the conc of water in mol/L
    return int(num_ions)


# noinspection DuplicatedCode
@noderesource(DEFAULT_RESOURCES_PATH / "tleap")
@worknodehelper(file_exists=True, input_artifact_types=(BaseComplexStructureFile,))
class BuildAFEBoxes(BaseBatchWorkNode, TleapMixin):
    """
    Builds a consistent set of solvated and salted boxes for AFE calculations.

    This WorkNode takes a batch of protein-ligand complexes, and for each,
    it generates two PDB files: one for the solvated complex and one for the
    solvated ligand (binder).

    The core strategy is to create a consistent solvent box for all systems.
    It achieves this by:
    1.  Extracting all ligands and all complexes from the input files.
    2.  Creating two "superuniverse" PDB files:
        - One containing all ligands.
        - One containing a representative receptor plus all ligands.
    3.  Building a single, large solvated and salted box for each superuniverse
        using Amber's `tleap`. The complex box uses `com_buffer` and the ligand
        (aqueous) box uses `aq_buffer`. The solute will be centered in the box,
        but it's principal axes will not be aligned with the cartesian axes, nor
        the axes required by pmemd PME, so a later step will be needed to do this.
    4.  For each individual system, it reconstructs the final PDB by merging
        the original solute (complex or ligand) with the corresponding
        superuniverse's solvent box.

    This ensures that all related simulations start from a solvent configuration
    that is as similar as possible, which is crucial for free energy calculations.

    Known issues:
        - IT ONLY WORKS WITH IDENTICAL TARGETS SET TO TRUE, IF MORE THAN 1 TARGET, THEN MDANALYSIS ALIGN CALL
          (`align.alignto(sys_atoms, v.atoms, selection)`) in `rejoin_with_box()` won't work
        -

    Attributes:
        id (str): The WorkNode's unique identifier.
        boxshape (str): The shape of the solvent box (e.g., 'truncated_octahedron').
            Must be a supported tleap box type.
        com_buffer (float): The buffer distance (in Angstroms) between the solute
            and the box edge for the complex systems.
        aq_buffer (float): The buffer distance (in Angstroms) for the aqueous
            (ligand-only) systems.
        neutralize (bool): Whether to neutralize the system with counter-ions.
        salt_concentration (float): The molar concentration of salt (NaCl) to add.
        na_count (int): A specific number of Na+ ions to add, overriding salt concentration logic.
        cl_count (int): A specific number of Cl- ions to add, overriding salt concentration logic.
        solvent (str): The water model to use (e.g., 'opc'). Must be a supported model.
        resname (str): The residue name of the ligand/binder in the input PDB files.
        solvent_selection (str): argument `watname` is added to HOH, Na+ and Cl- as the solvent selection string.
        identical_targets (bool): If True, assumes all protein targets are identical
            and uses only one of them to build the complex superuniverse, optimizing the process.
        pick_target (Optional[str]): If `identical_targets` is True, specifies which
            system's target to use as the template.
        to_guess (Optional[tuple]): A tuple of topology attributes for MDAnalysis to
            guess when loading structures (e.g., ('bonds', 'angles')).
        debug (bool): If True, enables debug mode.
    """

    ALIGN_CENTER_SCRIPT = """source leaprc.protein.ff19SB
source leaprc.RNA.OL3
source leaprc.phosaa19SB
loadamberparams frcmod.ff19SB
source leaprc.gaff2
$NEUTRALIZE
source leaprc.water.opc
mol = loadpdb $INPUT_PDB_FILENAME
solvateoct mol OPCBOX 0 999999
savepdb mol $OUTPUT_PDB_FILENAME
quit
"""

    def __init__(
        self,
        wnid: str,
        *args,
        boxshape: str = "truncated_octahedron",
        com_buffer: float = 10,
        aq_buffer: float = 16,
        neutralize: bool = True,
        salt_concentration: float = 0.14,
        na_count: int = 0,
        cl_count: int = 0,
        solvent: str = "opc",
        resname: str = "LIG",
        watname: str = "WAT",
        identical_targets: bool = True,
        pick_target: Optional[str] = None,
        to_guess: Optional[tuple] = None,
        debug: bool = True,
        **kwargs,
    ) -> None:
        super().__init__(
            wnid=wnid,
            *args,
            **kwargs,
        )

        super().check_supported(solvent, "water")
        self.solvent = solvent

        super().check_supported(boxshape, "boxshape")
        self.boxshape = boxshape

        self.com_buffer = float(com_buffer)
        self.aq_buffer = float(aq_buffer)
        self.neutralize = neutralize
        self.salt_concentration = float(salt_concentration)
        self.na_count = na_count
        self.cl_count = cl_count
        self.resname = resname
        self.solvent_selection = f"(resname {watname} or resname HOH or name Na+ Cl-)"
        self.identical_targets = identical_targets
        self.pick_target = pick_target
        self.debug = debug
        self.tleap = None
        self.to_guess = to_guess

        self.out_dirs: list[Path] = []
        self.binders = {}
        self.binders_resnum = {}
        self.complexes = {}
        self.complexes_binders = {}

    def _run(
        self,
        *,
        cwd: dirpath_t,
        binpath: Optional[filepath_t] = None,
        **kwargs,
    ) -> BatchArtifacts:
        # Init paths
        all_complexes_filepath = self.work_dir / "superuniverse_complexes.pdb"
        boxed_complexes_filepath = all_complexes_filepath.with_name(f"box_{all_complexes_filepath.stem}.pdb")

        all_binders_filepath = self.work_dir / "superuniverse_binders.pdb"
        boxed_binders_filepath = all_binders_filepath.with_name(f"box_{all_binders_filepath.stem}.pdb")

        if self._try_and_skip(boxed_complexes_filepath, boxed_binders_filepath):
            return self.output_artifacts
        biomolecule = get_biomolecule(self.input_artifacts, self.node_logger)
        centered_aligned_complexes, centered_aligned_binders = self.center_align_complexes_and_binders(
            self.input_artifacts, biomolecule
        )
        self.write_superuniverses(
            centered_aligned_complexes, centered_aligned_binders, all_binders_filepath, all_complexes_filepath
        )
        # Build the box for the binders and the complexes (`aq` and `com`).
        boxed_salted_binders = self.box_water_salt(
            all_binders_filepath,
            self.work_dir,
            self.node_logger,
            boxed_filepath=boxed_binders_filepath,
            boxshape=self.boxshape,
            solvent=self.solvent,
            salt_concentration=self.salt_concentration,
            buffer=self.aq_buffer,
        )

        boxed_salted_complexes = self.box_water_salt(
            all_complexes_filepath,
            self.work_dir,
            self.node_logger,
            boxed_filepath=boxed_complexes_filepath,
            boxshape=self.boxshape,
            solvent=self.solvent,
            salt_concentration=self.salt_concentration,
            buffer=self.com_buffer,
        )

        for sysname in self.input_artifacts.keys():
            self.out_dirs[sysname].mkdir(exist_ok=True)
            complex_out_filepath = self.out_dirs[sysname] / f"complex_{sysname}.pdb"
            self.rejoin_with_box(
                self.complexes[sysname],
                boxed_salted_complexes,
                self.solvent_selection,
                biomolecule,
                selection=biomolecule,
                out_filepath=complex_out_filepath,
            )

            binder_out_filepath = self.out_dirs[sysname] / f"binder_{sysname}.pdb"
            self.rejoin_with_box(
                self.binders[sysname],
                boxed_salted_binders,
                self.solvent_selection,
                biomolecule,
                selection=f"resnum {self.binders_resnum[sysname]}",
                out_filepath=binder_out_filepath,
            )

        self.output_artifacts = self.fill_output_artifacts(boxed_complexes_filepath, boxed_binders_filepath)
        return self.output_artifacts

    def fill_output_artifacts(self, boxed_complexes: filepath_t, boxed_binders: filepath_t) -> BatchArtifacts:
        outdata: dict[str, ArtifactContainer] = {}

        box_cpx = ComplexPeriodicBox(self.get_periodic_box_parameters(boxed_complexes))
        box_lig = BinderPeriodicBox(self.get_periodic_box_parameters(boxed_binders))

        for sysname, in_complexes in self.input_artifacts.items():
            complex_out_filepath = self.out_dirs[sysname] / f"complex_{sysname}.pdb"
            cpx_type = ArtifactRegistry.name[self.artifact_map["BaseComplexStructureFile"]]
            out_cpx = cpx_type(complex_out_filepath)

            binder_out_filepath = self.out_dirs[sysname] / f"binder_{sysname}.pdb"
            #  BuildAfeBoxes is hardcoded to use BinderLigand for now. I can use `artifact_map`
            #  to get the type of the complex, but not the type of the binder, and there's no mechanism to get "related"
            #  artifact types.
            out_lig = BinderLigandPDB(binder_out_filepath)

            outdata[sysname] = ArtifactContainer(sysname, (out_cpx, out_lig, box_cpx, box_lig))
        return BatchArtifacts(art_id=self.id, data=outdata)

    @staticmethod
    def get_periodic_box_parameters(boxed_pdb: filepath_t) -> list[float]:
        with open(boxed_pdb, "rb") as f:
            with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                # Find the end of the first line
                line_end = mm.find(b"\n")
                first_line = mm[:line_end].decode()

                if not first_line.startswith("CRYST1"):
                    raise ValueError(f"{boxed_pdb} irst line ({first_line}) is not a CRYST1 record")

                try:
                    # Split the line and slice the 6 numbers corresponding to the box dimensions
                    parts = first_line.split()
                    if len(parts) < 7:
                        raise ValueError("CRYST1 line is malformed or has too few values.")

                    # Convert the relevant parts to floats
                    return [float(x) for x in parts[1:7]]
                except (ValueError, IndexError) as e:
                    raise ValueError(f"Failed to parse CRYST1 line: {first_line}") from e

    @staticmethod
    def merge_without_clash(
        solute: AtomGroup,
        solvent: AtomGroup,
        biomolecule: str,
        node_logger: Logger,
        clash_cutoff: float = 0.9,
    ) -> Universe:
        """
        Merges the original complex with the solvent box, ensuring no clashes between the solute and solvent.

        If the complexes had crystallographic waters or ions, they're going to show up twice, since we didn't discard them
        in the complexes.

        Parameters
        ----------
        solute
        solvent
        biomolecule
        node_logger
        clash_cutoff

        Returns
        -------

        """

        non_clashing_waters_ions = []
        extra_solute_atoms = solute.select_atoms(f"not {biomolecule}")
        node_logger.debug(
            f"Found {len(extra_solute_atoms)} atoms in the solute that are not part of the {biomolecule=}"
        )

        for water_ion in solvent.residues:
            # Calculate all distances between the solvent box water atoms and the water/ion atoms in the solute
            dist_matrix = distance_array(water_ion.atoms.positions, extra_solute_atoms.positions)
            # If the minimum distance is greater than the cutoff, there is no clash
            if np.min(dist_matrix) > clash_cutoff:
                non_clashing_waters_ions.append(water_ion)

        node_logger.debug(
            f"Found {len(non_clashing_waters_ions)} out of {len(solvent.residues)} non-clashing water/ions to add."
        )

        non_clashing_solvent = AtomGroup([atom for res in non_clashing_waters_ions for atom in res.atoms])

        return Merge(solute, non_clashing_solvent)

    def rejoin_with_box(
        self,
        sys_atoms: AtomGroup,
        box_filepath: Path,
        box_selection: str,
        biomolecule: str,
        *,
        selection: str,
        out_filepath: Path,
    ):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")

            v = Universe(box_filepath)
            # This is necessary because tleap rotates systems around when building the box, and adding the waters.
            # TODO: fix for different targets
            align.alignto(sys_atoms, v.atoms, selection)
            # else:
            #     # Or systems are centered in the origin, tleeap will center the solute, but then also put it in
            #     solute_atoms = v.select_atoms(f" not {box_selection}")
            #     sys_atoms.positions = sys_atoms.atoms.positions + (solute_atoms.centroid() - sys_atoms.centroid())

            solvent_ions_box = v.select_atoms(box_selection)
            full_system = self.merge_without_clash(sys_atoms, solvent_ions_box, biomolecule, self.node_logger)

            try:
                full_system.add_TopologyAttr("elements")
                full_system.atoms.elements = np.pad(
                    sys_atoms.elements,
                    pad_width=(0, len(full_system.atoms) - len(sys_atoms.elements)),
                    mode="constant",
                    constant_values="",
                )
            except AttributeError:
                # No elements attribute in the original complex
                pass
            full_system.residues.resids = np.arange(1, len(full_system.residues.resids) + 1)
            full_system.atoms.write(out_filepath)

    def center_align_principal_axes(self, pdb_in: filepath_t, cwd: dirpath_t, neutralize_first: bool = False) -> Path:
        cwd.mkdir(exist_ok=True)
        oriented_nochainid_pdb = cwd / f"oriented_nochainid_{Path(pdb_in).name}"
        oriented_pdb = cwd / f"oriented_{Path(pdb_in).name}"

        tleap_script = Template(self.ALIGN_CENTER_SCRIPT).substitute(
            {
                "INPUT_PDB_FILENAME": str(pdb_in),
                "OUTPUT_PDB_FILENAME": str(oriented_nochainid_pdb),
                "NEUTRALIZE": "addions2 mol Na+ 0\naddions2 mol Cl- 0" if neutralize_first else "",
            }
        )
        tleap_script_fn = cwd / f"tleap_orient_{pdb_in.stem}.in"
        with open(tleap_script_fn, "w") as outfile:
            outfile.write(tleap_script)

        logleap_orient = "logleap_orient"
        self.command.run(
            ["tleap", "-f", str(tleap_script_fn), ">", logleap_orient],
            cwd=cwd,
            logger=self.node_logger,
            expected=(oriented_nochainid_pdb,),
        )
        check_leap_log(cwd / logleap_orient, node_logger=self.node_logger)

        # Fix the missing chain IDs that tleap removed
        AddChainid.assign_chain_ids_mmap(oriented_nochainid_pdb, oriented_pdb)
        return oriented_pdb

    def center_align_complexes_and_binders(
        self, input_artifacts: BatchArtifacts, biomolecule: str
    ) -> tuple[dict[str, Path], dict[str, Path]]:
        """
        Center-aligns the principal axes of the complexes and binders in the input artifacts.

        A consequence of using tleap to do this one by one, is that when the target is identical across systems,
        the superposition of all complex will yield aligned complexes and ligands, but the superposition of binders
        will show them differently aligned, since they had different axii of inertia.
        In any case, this is irrelevant.

        Parameters
        ----------
        input_artifacts
        biomolecule

        Returns
        -------

        """
        centered_aligned_complexes: dict[str, Path] = {}
        centered_aligned_binders: dict[str, Path] = {}
        i = 1
        for sysname, art_container in input_artifacts.items():
            if sysname not in self.systems:
                continue
            for arts in art_container.values():
                for art in arts:
                    if isinstance(art, BaseComplexStructureFile):
                        orient_dir = self.work_dir / f"{sysname}_orient"
                        neutralize_first = biomolecule == "nucleic"  # nucleic acids need to be neutralized first

                        # First do the complex
                        centered_aligned_complexes[sysname] = self.center_align_principal_axes(
                            art.filepath, orient_dir, neutralize_first
                        )

                        # Now do the binder
                        u = runiverse(Path(art.filepath), to_guess=self.to_guess)
                        lig = u.select_atoms(f"resname {self.resname}")
                        if len(lig.residues) != 1:
                            err_msg = f"""Found {len(lig.residues)} residues with resname {self.resname} in input file {art.filepath},
                        expected 1. Check the complex for the system {sysname}"""
                            self.node_logger.error(err_msg)
                            raise ValueError(err_msg)
                        lig_pdb = Path(orient_dir, f"binder_{sysname}.pdb")
                        with warnings.catch_warnings():
                            warnings.simplefilter("ignore")
                            lig.write(lig_pdb)
                        oriented_lig_pdb = self.center_align_principal_axes(lig_pdb, orient_dir)

                        # set a different resnum for each binder, so that tleap can handle them correctly
                        with warnings.catch_warnings():
                            warnings.simplefilter("ignore")
                            u = Universe(oriented_lig_pdb, in_memory=True)
                            u.atoms.residues.resnums = i
                            u.atoms.residues.resids = i
                            i += 1
                            u.atoms.write(oriented_lig_pdb)
                        centered_aligned_binders[sysname] = oriented_lig_pdb

        return centered_aligned_complexes, centered_aligned_binders

    def write_superuniverses(
        self,
        complexes: dict[str, Path],
        binders: dict[str, Path],
        out_binders_pdb: Path,
        out_complexes_pdb: Path,
    ) -> None:
        """Joins all the ligands and all the complexes into 2 superuniverses and writes them to a file.
        Optionally, the complex universe can be comprised of all the ligands and just 1 target, in case all the
        complexes have the same target with the same conformation.

        An inspection of both superuniverses may show that the one for the complex is completely aligned,
        while the superuniverse for the binders shows them misaligned.
        his is due to tleap alignment on a previous step.
        """
        binder_resnum = 1
        for sysname, pdb in complexes.items():
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                u = runiverse(Path(pdb), to_guess=self.to_guess)
            # Get the complex, keep any chrystallographic waters or ions as part of the solute.
            # I used to discard them: self.complexes.append(u.select_atoms(f"not {self.solvent_selection}"))
            self.complexes[sysname] = u.atoms
            # Get the binders out of the complexes. We can't use the free binders because those were aligned differently.
            binder_atoms = u.select_atoms(f"resname {self.resname}")
            # Renumber binders so that tleap can handle them correctly.
            if binder_resnum == 0:
                # First complex should come with a ligand with resnum 1
                binder_atoms.residues.resnums = 1
                binder_atoms.residues.resids = 1
                self.binders_resnum[sysname] = binder_resnum
                # Make it so that the next binder gets a resnum that goes after the whole target + first binder
                binder_resnum = len(u.residues)
            else:
                binder_atoms.residues.resnums = binder_resnum
                binder_atoms.residues.resids = binder_resnum
                self.binders_resnum[sysname] = binder_resnum
                binder_resnum += 1
            self.complexes_binders[sysname] = binder_atoms

        for sysname, pdb in binders.items():
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                u = runiverse(Path(pdb), to_guess=self.to_guess)
            self.binders[sysname] = u.atoms

        binder_superuniverse = Merge(*self.binders.values())
        if self.identical_targets:
            some_target = next(iter(complexes.keys())) if self.pick_target is None else self.pick_target
            # whatever target we choose, we're gonna end up with its ligand duplicated in the superuniverse. Who cares.
            complex_superuniverse = Merge(self.complexes[some_target], *self.complexes_binders.values())
        else:
            complex_superuniverse = Merge(*[atoms for atoms in self.complexes.values()])

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            binder_superuniverse.atoms.write(out_binders_pdb)
            complex_superuniverse.atoms.write(out_complexes_pdb)

    def write_tleap(
        self,
        template_script: str,
        input_path: filepath_t,
        output_path: filepath_t,
        node_logger: Logger,
        *,
        solvent: str = "tip3p",
        buffer: float = 16,
        na_count: int = 0,
        cl_count: int = 0,
    ) -> Path:
        """
        Generates a tleap input script based on a template and writes it to a file sitting right next to the input PDB.

        Args:
            template_script (str): The name of the tleap template script to use.
            input_path (filepath_t): The path to the input PDB file.
            output_path (filepath_t): The path to the output PDB file.
            node_logger (Logger): Logger instance for logging errors or information.
            solvent (str, optional): The solvent model to use. Defaults to "tip3p".
            buffer (float, optional): The buffer size for the box. Defaults to 16.
            na_count (int, optional): The number of sodium ions to add. Defaults to 0.
            cl_count (int, optional): The number of chloride ions to add. Defaults to 0.

        Returns:
            Path: The path to the generated tleap script.

        Raises:
            ValueError: If the provided template_script is not found in the available templates.
        """

        try:
            tleap_template_txt = Template(self.resources[template_script])
        except KeyError:
            err_msg = f"write_tleap(): Invalid template {template_script}. Must be one of {self.resources.keys()}"
            node_logger.error(err_msg)
            raise ValueError(err_msg)

        replacements = {
            "SOLVENT_MODEL": solvent,
            "SOLVENT_BOX_TYPE": self.SOLVENT_TO_BOX[solvent],
            "NUM_CL_IONS": cl_count,
            "NUM_NA_IONS": na_count,
            "INPUT_PDB_FILENAME": input_path.name,
            "BOX_BUFFER_SIZE": buffer,
            "SEPARATION": np.clip(buffer // 3, 3, 10),
            "OUTPUT_PDB_FILENAME": output_path.name,
        }

        tleap_script = tleap_template_txt.substitute(replacements)

        output_path = input_path.parent / f"tleap_{template_script}_{input_path.stem}.in"
        with open(output_path, "w") as outfile:
            outfile.write(tleap_script)

        return output_path

    def box_water_salt(
        self,
        solute_filepath: Path,
        cwd: Path,
        node_logger: Logger,
        *,
        boxed_filepath: filepath_t,
        boxshape: str = "orthorhombic",
        solvent: str = "tip3p",
        buffer: float = 16,
        salt_concentration: float = 0.14,
    ) -> Path:
        # Add water box
        tleap_script = self.write_tleap(
            boxshape,
            solute_filepath,
            boxed_filepath,
            node_logger=node_logger,
            solvent=solvent,
            buffer=buffer,
        )
        logleap_box = "logleap_box"
        self.command.run(
            ["tleap", "-f", str(tleap_script), ">", logleap_box],
            cwd=cwd,
            logger=node_logger,
            expected=(boxed_filepath,),
        )
        check_leap_log(cwd / logleap_box, node_logger=node_logger)

        # Add salt
        ion_count = get_num_ions(boxed_filepath, salt_concentration)
        salted_filepath = solute_filepath.with_name(f"ions_{solute_filepath.stem}.pdb")
        tleap_script = self.write_tleap(
            "salt",
            boxed_filepath,
            salted_filepath,
            node_logger=node_logger,
            buffer=buffer,
            na_count=ion_count // 2 + 1,
            cl_count=ion_count // 2 + 1,
        )
        logleap_ion = "logleap_ion"
        self.command.run(
            ["tleap", "-f", str(tleap_script), ">", logleap_ion],
            cwd=cwd,
            logger=node_logger,
            expected=(salted_filepath,),
        )
        check_leap_log(cwd / logleap_ion, node_logger=node_logger)

        return salted_filepath

    def _try_and_skip(self, boxed_complexes: filepath_t, boxed_binders: filepath_t) -> bool:
        if self.skippable:
            try:
                self.output_artifacts = self.fill_output_artifacts(boxed_complexes, boxed_binders)
                self.node_logger.info(f"Skipped {self.id} WorkNode.")
                return True
            except (FileNotFoundError, ValueError) as e:
                self.node_logger.info(f"Can't skip {self.id} Got: {e}")
        return False


# noinspection DuplicatedCode
@noderesource(DEFAULT_RESOURCES_PATH / "tleap")
@worknodehelper(file_exists=True, input_artifact_types=(BaseStructureFile,), input_suffix=".pdb")
class BuildBoxes(BaseBatchWorkNode, TleapMixin):
    """Class for building consistent simulation boxes around all systems.

    This class provides functionality to create periodic boundary boxes, add solvent and ions.

    Attributes:
        solvent (str): The water model to use for solvation (e.g. 'opc', 'tip3p')
        boxshape (str): The shape of the simulation box ('truncated_octahedron', 'orthorhombic', etc.)
        buffer (float): The minimum distance between solute and box edge in Angstroms
        neutralize_system (bool): Whether to neutralize the system by adding counterions
        salt_concentration (float): Target salt concentration in M (mol/L)
        additional_leaprc (list[str], optional): Additional leaprc files to source
        resname (str): Residue name of the ligand
        solvent_selection (str): MDAnalysis selection string to identify solvent and ions
        identical_targets (bool): Whether all targets are identical in structure
        to_guess (tuple): MDAnalysis parameter. Which atom topology attr should be guessed. Eg: ("elements", ).
        debug (bool): Whether to enable debug logging
        out_dirs (list[Path]): Output directories for each system
    """

    def __init__(
        self,
        wnid: str,
        *args,
        boxshape: str = "truncated_octahedron",
        buffer: float = 16,
        neutralize: bool = True,
        salt_concentration: float = 0.14,
        solvent: str = "opc",
        additional_leaprc: Optional[list[str]] = None,
        resname: str = "LIG",
        watname: str = "WAT",
        identical_targets: bool = True,
        to_guess: Optional[tuple] = None,
        debug: bool = True,
        **kwargs,
    ) -> None:
        super().__init__(
            wnid=wnid,
            *args,
            **kwargs,
        )

        super().check_supported(solvent, "water")
        self.solvent = solvent

        super().check_supported(boxshape, "boxshape")
        self.boxshape = boxshape
        self.buffer = float(buffer)
        self.neutralize_system = neutralize
        self.salt_concentration = float(salt_concentration)
        # TODO: not using this yet
        self.additional_leaprc = additional_leaprc
        self.resname = resname
        self.solvent_selection = f"(resname {watname} or resname HOH or name Na+ Cl-)"
        self.identical_targets = identical_targets
        self.debug = debug
        self.tleap = None
        self.to_guess = to_guess

        self.out_dirs: list[Path] = []
        self.structs = []

    def _run(
        self,
        *,
        cwd: dirpath_t,
        binpath: Optional[filepath_t] = None,
        **kwargs,
    ) -> BatchArtifacts:
        prefix = next(iter(self.prefix.values()))
        if self._try_and_skip(prefix):
            return self.output_artifacts

        all_structs_filepath = self.work_dir / "superuniverse_complexes.pdb"
        self.write_superuniverse(self.input_artifacts, all_structs_filepath)
        # Build the box for the system
        boxed_structs = self.box_water_salt(
            all_structs_filepath,
            self.work_dir,
            self.node_logger,
            boxshape=self.boxshape,
            solvent=self.solvent,
            salt_concentration=self.salt_concentration,
            buffer=self.buffer,
        )

        for sysname in self.input_artifacts.keys():
            self.out_dirs[sysname].mkdir(exist_ok=True)
            struct_out_filepath = self.out_dirs[sysname] / f"{prefix}_{sysname}.pdb"
            self.rejoin_with_box(self.structs[sysname], boxed_structs, self.solvent_selection, struct_out_filepath)

        self.output_artifacts = self.fill_output_artifacts(prefix)
        return self.output_artifacts

    def _try_and_skip(self, prefix: str, suffix: str = "pdb") -> bool:
        if self.skippable:
            try:
                self.output_artifacts = self.fill_output_artifacts(prefix, suffix)
                self.node_logger.info(f"Skipped {self.id} WorkNode.")
                return True
            except (FileNotFoundError, ValueError) as e:
                self.node_logger.info(f"Can't skip {self.id} Got: {e}")
        return False

    def fill_output_artifacts(self, prefix: str, suffix: str = "pdb") -> BatchArtifacts:
        outdata: dict[str, ArtifactContainer] = {}
        for sysname, in_structs in self.input_artifacts.items():
            structs_out_filepath = self.out_dirs[sysname] / f"{prefix}_{sysname}.{suffix}"
            struct_type = ArtifactRegistry.name[self.artifact_map["BaseComplexStructureFile"]]
            out_struct = struct_type(structs_out_filepath)
            outdata[sysname] = ArtifactContainer(sysname, (out_struct,))
        return BatchArtifacts(art_id=self.id, data=outdata)

    @staticmethod
    def rejoin_with_box(sys_atoms: AtomGroup, box_filepath: Path, box_selection: str, out_filepath: Path):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")

            v = Universe(box_filepath)
            solvent_ions_box = v.select_atoms(box_selection)
            # Center it, since tleap will do that, and we need to put each complex back into tleap's box
            sys_atoms.positions = sys_atoms.atoms.positions - sys_atoms.atoms.centroid()
            # TODO: if something big like a Mg was removed and tleap placed a water in its place, then we'll get quite an error.
            full_system = Merge(sys_atoms, solvent_ions_box)
            try:
                full_system.add_TopologyAttr("elements")
                full_system.atoms.elements = np.pad(
                    sys_atoms.elements,
                    pad_width=(0, len(full_system.atoms) - len(sys_atoms.elements)),
                    mode="constant",
                    constant_values="",
                )
            except AttributeError:
                # No elements attribute in the original complex
                pass
            full_system.atoms.write(out_filepath)

    def write_superuniverse(
        self,
        input_artifacts: BatchArtifacts,
        out_structs_pdb: Path,
    ) -> None:
        """Joins all the structures into a superuniverse and writes it to a file."""
        for sysname, art_container in input_artifacts.items():
            if sysname not in self.systems:
                continue
            for arts in art_container.values():
                for art in arts:
                    u = runiverse(Path(art), to_guess=self.to_guess)
                    self.structs.append(u.atoms)
        superuniverse = Merge(*self.structs)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            superuniverse.atoms.write(out_structs_pdb)

    def write_tleap(
        self,
        template_script: str,
        input_path: filepath_t,
        output_path: filepath_t,
        node_logger: Logger,
        *,
        solvent: str = "tip3p",
        buffer: float = 16,
        na_count: int = 0,
        cl_count: int = 0,
    ) -> Path:
        """
        Generates a tleap input script based on a template and writes it to a file sitting right next to the input PDB.

        Args:
            template_script (str): The name of the tleap template script to use.
            input_path (filepath_t): The path to the input PDB file.
            output_path (filepath_t): The path to the output PDB file.
            node_logger (Logger): Logger instance for logging errors or information.
            solvent (str, optional): The solvent model to use. Defaults to "tip3p".
            buffer (float, optional): The buffer size for the box. Defaults to 16.
            na_count (int, optional): The number of sodium ions to add. Defaults to 0.
            cl_count (int, optional): The number of chloride ions to add. Defaults to 0.

        Returns:
            Path: The path to the generated tleap script.

        Raises:
            ValueError: If the provided template_script is not found in the available templates.
        """

        try:
            tleap_template_txt = Template(self.resources[template_script])
        except KeyError:
            err_msg = f"write_tleap(): Invalid template {template_script}. Must be one of {self.resources.keys()}"
            node_logger.error(err_msg)
            raise ValueError(err_msg)

        replacements = {
            "SOLVENT_MODEL": solvent,
            "SOLVENT_BOX_TYPE": self.SOLVENT_TO_BOX[solvent],
            "NUM_CL_IONS": cl_count,
            "NUM_NA_IONS": na_count,
            "INPUT_PDB_FILENAME": input_path.name,
            "BOX_BUFFER_SIZE": buffer,
            "SEPARATION": np.clip(buffer // 3, 3, 10),
            "OUTPUT_PDB_FILENAME": output_path.name,
        }

        tleap_script = tleap_template_txt.substitute(replacements)

        output_path = input_path.parent / f"tleap_{template_script}_{input_path.stem}.in"
        with open(output_path, "w") as outfile:
            outfile.write(tleap_script)

        return output_path

    def box_water_salt(
        self,
        solute_filepath: Path,
        cwd: Path,
        node_logger: Logger,
        *,
        boxshape: str = "orthorhombic",
        solvent: str = "tip3p",
        buffer: float = 16,
        salt_concentration: float = 0.14,
    ) -> Path:
        # Add water box
        boxed_filepath = solute_filepath.with_name(f"box_{solute_filepath.stem}.pdb")
        tleap_script = self.write_tleap(
            boxshape,
            solute_filepath,
            boxed_filepath,
            node_logger=node_logger,
            solvent=solvent,
            buffer=buffer,
        )
        logleap_box = "logleap_box"
        self.command.run(
            ["tleap", "-f", str(tleap_script), ">", logleap_box],
            cwd=cwd,
            logger=node_logger,
            expected=(boxed_filepath,),
        )
        check_leap_log(cwd / logleap_box, node_logger=node_logger)

        # Add salt
        ion_count = get_num_ions(boxed_filepath, salt_concentration)
        salted_filepath = solute_filepath.with_name(f"ions_{solute_filepath.stem}.pdb")
        tleap_script = self.write_tleap(
            "salt",
            boxed_filepath,
            salted_filepath,
            node_logger=node_logger,
            buffer=buffer,
            na_count=ion_count // 2 + 1,
            cl_count=ion_count // 2 + 1,
        )
        logleap_ion = "logleap_ion"
        self.command.run(
            ["tleap", "-f", str(tleap_script), ">", logleap_ion],
            cwd=cwd,
            logger=node_logger,
            expected=(salted_filepath,),
        )
        check_leap_log(cwd / logleap_ion, node_logger=node_logger)

        return salted_filepath
