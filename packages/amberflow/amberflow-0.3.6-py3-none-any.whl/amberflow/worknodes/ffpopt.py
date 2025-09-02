from pathlib import Path
from typing import Any, Union

from parmed import load_file

# noinspection PyProtectedMember
from parmed.tools.actions import deleteDihedral, addDihedral

from amberflow.artifacts import ArtifactContainer, BatchArtifacts, BaseTopologyFile
from amberflow.primitives import dirpath_t, filepath_t
from amberflow.worknodes import BaseSingleWorkNode, worknodehelper

__all__ = ("FFPOPT",)


# noinspection DuplicatedCode,PyTypeChecker
@worknodehelper(
    file_exists=True,
    input_artifact_types=(BaseTopologyFile,),
    output_artifact_types=(BaseTopologyFile,),
)
class FFPOPT(BaseSingleWorkNode):
    def __init__(
        self,
        wnid: str,
        *args,
        resname: str = "LIG",
        scee: float = 1.2,
        scnb: float = 2.0,
        **kwargs,
    ) -> None:
        super().__init__(
            wnid=wnid,
            *args,
            **kwargs,
        )
        self.resname = resname
        self.scee = scee
        self.scnb = scnb

    def _run(
        self,
        *,
        cwd: dirpath_t,
        sysname: str,
        **kwargs,
    ) -> Any:
        intop = self.input_artifacts["BaseTopologyFile"]
        outparm = self.work_dir / intop.filepath.name
        if self.skippable:
            if self._try_and_skip(sysname, outparm=outparm):
                return self.output_artifacts

        scee = self.scee
        scnb = self.scnb
        p = load_file(str(intop.filepath))
        raise_on_empty_ne_atoms = True
        print_debug_statements = True

        # find the ne atoms
        ne_atoms = [atom for atom in p.atoms if (atom.type.lower() == "ne" or atom.type.lower() == "nf")]

        if len(ne_atoms) == 0 and raise_on_empty_ne_atoms:
            err_msg = "Invalid 'ne' atom count found in residue. Please ensure there is exactly one 'ne' or 'nf' atom."
            raise Exception(err_msg)
        elif len(ne_atoms) > 1:
            err_msg = "Invalid 'ne' atom count found in residue. Please ensure there is exactly one 'ne' or 'nf' atom."
            raise Exception(err_msg)

        carbonyl_c = None
        carbonyl_o = None
        ring_c = None
        ring_s = None
        ring_n = None
        final_c = None

        ne_atom = ne_atoms[0]
        if len(ne_atom.bond_partners) != 2 and raise_on_empty_ne_atoms:
            raise Exception("Invalid ne atom found, connected to too many things!")

        # find the carbonyl atoms
        for neighbor in ne_atom.bond_partners:
            if neighbor.type.lower().startswith("c") and len(neighbor.bond_partners) == 3:
                for second_neighbor in neighbor.bond_partners:
                    if second_neighbor.type.lower().startswith("o") and len(second_neighbor.bond_partners) == 1:
                        carbonyl_c = neighbor
                        carbonyl_o = second_neighbor
                        break

        # This finds the next atom in the chain away from the carbonyl
        for atom in carbonyl_c.bond_partners:
            if atom != ne_atom and atom != carbonyl_o:
                # Option 1
                # if atom.type.lower() == "c":
                #    final_c = atom
                # Option 2
                if print_debug_statements and not atom.type.lower().startswith("c"):
                    err_msg = f"The atom bonded to the carbonyl carbon is not a carbon. It is a {atom.type}."
                    self.node_logger.warn(err_msg)
                final_c = atom

        # This finds the two ring atoms. Right now assumed to be n and s.
        for neighbor in ne_atom.bond_partners:
            if neighbor.type.lower().startswith("c") and neighbor != carbonyl_c:
                if len(neighbor.bond_partners) == 3:
                    ring_c = neighbor

        # find the aromatic atom bonded to this carbon
        for atom in ring_c.bond_partners:
            if atom != ne_atom and atom != carbonyl_c:
                if atom.type.lower().startswith("s"):
                    ring_s = atom
                if atom.type.lower().startswith("n") and len(atom.bond_partners) == 2:
                    ring_n = atom

        # test that all atoms were found
        _flag_found_all_atoms = False
        if None in [ne_atom, carbonyl_c, carbonyl_o, ring_c, ring_s, ring_n, final_c]:
            if raise_on_empty_ne_atoms:
                self.node_logger.error(f"ne_atom: {ne_atom}")
                self.node_logger.error(f"{carbonyl_c=}, {carbonyl_o=}, {ring_c=}, {ring_s=}, {ring_n=}, {final_c=}")
                raise Exception("Not all required atoms were found.")
        else:
            self.node_logger.info(
                f"Found: {carbonyl_c.name}, {carbonyl_o.name}, {ring_c.name}, {ring_s.name}, {ring_n.name}, {final_c.name}."
            )
            _flag_found_all_atoms = True

        if _flag_found_all_atoms:
            deleteDihedral(
                p,
                f":{self.resname}@{carbonyl_c.name}",
                f":{self.resname}@{ne_atom.name}",
                f":{self.resname}@{ring_c.name}",
                f":{self.resname}@{ring_s.name}",
            ).execute()
            addDihedral(
                p,
                f":{self.resname}@{carbonyl_c.name}",
                f":{self.resname}@{ne_atom.name}",
                f":{self.resname}@{ring_c.name}",
                f":{self.resname}@{ring_s.name}",
                1.3597545801351958,
                1,
                0,
                scee,
                scnb,
            ).execute()
            addDihedral(
                p,
                f":{self.resname}@{carbonyl_c.name}",
                f":{self.resname}@{ne_atom.name}",
                f":{self.resname}@{ring_c.name}",
                f":{self.resname}@{ring_s.name}",
                -2.9811554633118313,
                2,
                0,
                scee,
                scnb,
            ).execute()
            addDihedral(
                p,
                f":{self.resname}@{carbonyl_c.name}",
                f":{self.resname}@{ne_atom.name}",
                f":{self.resname}@{ring_c.name}",
                f":{self.resname}@{ring_s.name}",
                -0.9600490972636792,
                3,
                0,
                scee,
                scnb,
            ).execute()

            deleteDihedral(
                p,
                f":{self.resname}@{carbonyl_c.name}",
                f":{self.resname}@{ne_atom.name}",
                f":{self.resname}@{ring_c.name}",
                f":{self.resname}@{ring_n.name}",
            ).execute()
            addDihedral(
                p,
                f":{self.resname}@{carbonyl_c.name}",
                f":{self.resname}@{ne_atom.name}",
                f":{self.resname}@{ring_c.name}",
                f":{self.resname}@{ring_n.name}",
                3.6097657099773444,
                1,
                0,
                scee,
                scnb,
            ).execute()
            addDihedral(
                p,
                f":{self.resname}@{carbonyl_c.name}",
                f":{self.resname}@{ne_atom.name}",
                f":{self.resname}@{ring_c.name}",
                f":{self.resname}@{ring_n.name}",
                -1.7303328398258357,
                2,
                0,
                scee,
                scnb,
            ).execute()
            addDihedral(
                p,
                f":{self.resname}@{carbonyl_c.name}",
                f":{self.resname}@{ne_atom.name}",
                f":{self.resname}@{ring_c.name}",
                f":{self.resname}@{ring_n.name}",
                0.0010349225389669648,
                3,
                0,
                scee,
                scnb,
            ).execute()

            deleteDihedral(
                p,
                f":{self.resname}@{final_c.name}",
                f":{self.resname}@{carbonyl_c.name}",
                f":{self.resname}@{ne_atom.name}",
                f":{self.resname}@{ring_c.name}",
            ).execute()
            addDihedral(
                p,
                f":{self.resname}@{final_c.name}",
                f":{self.resname}@{carbonyl_c.name}",
                f":{self.resname}@{ne_atom.name}",
                f":{self.resname}@{ring_c.name}",
                2.96453479338014,
                1,
                0,
                scee,
                scnb,
            ).execute()
            addDihedral(
                p,
                f":{self.resname}@{final_c.name}",
                f":{self.resname}@{carbonyl_c.name}",
                f":{self.resname}@{ne_atom.name}",
                f":{self.resname}@{ring_c.name}",
                -6.635583558045419,
                2,
                0,
                scee,
                scnb,
            ).execute()
            addDihedral(
                p,
                f":{self.resname}@{final_c.name}",
                f":{self.resname}@{carbonyl_c.name}",
                f":{self.resname}@{ne_atom.name}",
                f":{self.resname}@{ring_c.name}",
                -0.4059171494562503,
                3,
                0,
                scee,
                scnb,
            ).execute()

            deleteDihedral(
                p,
                f":{self.resname}@{carbonyl_o.name}",
                f":{self.resname}@{carbonyl_c.name}",
                f":{self.resname}@{ne_atom.name}",
                f":{self.resname}@{ring_c.name}",
            ).execute()
            addDihedral(
                p,
                f":{self.resname}@{carbonyl_o.name}",
                f":{self.resname}@{carbonyl_c.name}",
                f":{self.resname}@{ne_atom.name}",
                f":{self.resname}@{ring_c.name}",
                4.9925119886996,
                1,
                0,
                scee,
                scnb,
            ).execute()
            addDihedral(
                p,
                f":{self.resname}@{carbonyl_o.name}",
                f":{self.resname}@{carbonyl_c.name}",
                f":{self.resname}@{ne_atom.name}",
                f":{self.resname}@{ring_c.name}",
                -3.0659172479984433,
                2,
                0,
                scee,
                scnb,
            ).execute()
            addDihedral(
                p,
                f":{self.resname}@{carbonyl_o.name}",
                f":{self.resname}@{carbonyl_c.name}",
                f":{self.resname}@{ne_atom.name}",
                f":{self.resname}@{ring_c.name}",
                -0.7245466635303205,
                3,
                0,
                scee,
                scnb,
            ).execute()

        # noinspection PyUnresolvedReferences
        p.save(str(outparm), overwrite=True)
        self.output_artifacts = self.fill_output_artifacts(sysname, outparm=outparm)
        return self.output_artifacts

    def _try_and_skip(self, sysname: str, *, outparm: Path) -> bool:
        if self.skippable:
            try:
                self.output_artifacts = self.fill_output_artifacts(sysname, outparm=outparm)
                self.node_logger.info(f"Skipped {self.id} WorkNode.")
                return True
            except (FileNotFoundError, ValueError) as e:
                self.node_logger.info(f"Can't skip {self.id} Got: {e}")
        return False

    def fill_output_artifacts(self, sysname: str, *, outparm: filepath_t) -> Union[ArtifactContainer, BatchArtifacts]:
        return ArtifactContainer(sysname, (self.artifact_builder["BaseTopologyFile"](outparm),))
