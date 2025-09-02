import warnings
from pathlib import Path
from typing import Any, Optional

import MDAnalysis as mda
from MDAnalysis.analysis.distances import dist
from MDAnalysis.lib.distances import calc_dihedrals
import numpy as np
from numpy.linalg import norm

from parmed.amber import AmberParm

# noinspection PyProtectedMember
from parmed.tools.actions import HMassRepartition

from amberflow.artifacts import (
    ArtifactContainer,
    ArtifactRegistry,
    BaseComplexTrajectoryFile,
    BoreschRestraints,
)
from amberflow.artifacts.topology import BaseTopologyFile, BaseComplexTopologyFile
from amberflow.primitives import (
    dirpath_t,
    DEFAULT_RESOURCES_PATH,
    filepath_t,
)
from amberflow.worknodes import noderesource, worknodehelper, BaseSingleWorkNode

__all__ = ("HMR", "GetBoresch")


# noinspection DuplicatedCode
@noderesource(DEFAULT_RESOURCES_PATH / "tleap")
@worknodehelper(
    file_exists=True,
    input_artifact_types=(BaseTopologyFile,),
    output_artifact_types=(BaseTopologyFile,),
)
class HMR(BaseSingleWorkNode):
    """
    Perform Hydrogen Mass Repartitioning (HMR) using parmed
    """

    def __init__(
        self,
        wnid: str,
        *args,
        # biomolecule: str = "protein",
        dowater: bool = False,
        new_h_mass: float = 3.024,
        new_ring_h_mass: Optional[float] = None,
        **kwargs,
    ):
        super().__init__(
            wnid=wnid,
            *args,
            # biomolecule=biomolecule,
            **kwargs,
        )
        self.dowater = dowater
        self.new_h_mass = new_h_mass
        self.new_ring_h_mass = float(new_ring_h_mass) if new_ring_h_mass else None

    def _run(
        self,
        *,
        cwd: dirpath_t,
        sysname: str,
        **kwargs,
    ) -> Any:
        in_top = Path(self.input_artifacts["BaseTopology"])
        top_typename = type(self.input_artifacts["BaseTopology"]).__name__
        if self._try_and_skip(sysname, outname=in_top.name, tags=self.tags[top_typename]):
            return self.output_artifacts

        # I have to do this speudo-switch statement due to the weird way in which parmed takes input parameters.
        # I won't use the `inspect` module to do this.
        top = AmberParm(str(in_top))
        if self.dowater:
            if self.new_ring_h_mass:
                # noinspection PyTypeChecker
                HMassRepartition(top, self.new_h_mass, "dowater", ring_hmass=self.new_ring_h_mass).execute()
            else:
                # noinspection PyTypeChecker
                HMassRepartition(top, self.new_h_mass, "dowater").execute()
        else:
            if self.new_ring_h_mass:
                # noinspection PyTypeChecker
                HMassRepartition(top, self.new_h_mass, ring_hmass=self.new_ring_h_mass).execute()
            else:
                # 99% of the time, this is the case.
                # noinspection PyTypeChecker
                HMassRepartition(top, self.new_h_mass).execute()
        top.save(str(self.work_dir / in_top.name), overwrite=True)
        self.output_artifacts = self.fill_output_artifacts(sysname, outname=in_top.name, tags=self.tags[top_typename])
        return self.output_artifacts

    def _try_and_skip(self, sysname: str, *, outname: str, tags: tuple[str, ...]) -> bool:
        if self.skippable:
            try:
                self.output_artifacts = self.fill_output_artifacts(sysname, outname=outname, tags=tags)
                self.node_logger.info(f"Skipped {self.id} WorkNode.")
                return True
            except (FileNotFoundError, ValueError) as e:
                self.node_logger.info(f"Can't skip {self.id} Got: {e}")
        return False

    def fill_output_artifacts(self, sysname: str, *, outname: str, tags: tuple[str, ...]) -> ArtifactContainer:
        return ArtifactContainer(
            sysname,
            (ArtifactRegistry.create_instance_by_filename(self.work_dir / outname, tags=tags),),
        )


# noinspection PyPep8Naming
@worknodehelper(
    file_exists=True,
    input_artifact_types=(BaseComplexTopologyFile, BaseComplexTrajectoryFile),
    output_artifact_types=(BoreschRestraints,),
)
class GetBoresch(BaseSingleWorkNode):
    """
    Get Boresch restraints
    """

    def __init__(
        self,
        wnid: str,
        *args,
        ligresid: int = 1,
        **kwargs,
    ):
        super().__init__(
            wnid=wnid,
            *args,
            **kwargs,
        )
        self.ligresid = ligresid

    def _run(
        self,
        *,
        cwd: dirpath_t,
        sysname: str,
        **kwargs,
    ) -> Any:
        if self._try_and_skip(sysname):
            return self.output_artifacts

        in_top = Path(self.input_artifacts["BaseComplexTopologyFile"])
        in_trj = Path(self.input_artifacts["BaseComplexTrajectoryFile"])
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            u = mda.Universe(in_top, in_trj)
        lig_heavy = u.select_atoms(f"resid {self.ligresid} and not name H*")
        anchors_dict = {}
        for lig_atom in lig_heavy:
            for prot_atom in u.select_atoms(
                f"(protein or resname PRT) and (around 10 index {lig_atom.index}) and (not name H*)"
            ):  # protein does not recognise PRT
                anchors_dict[(lig_atom.index, prot_atom.index)] = {}
                anchors_dict[(lig_atom.index, prot_atom.index)]["dists"] = []

        for frame in u.trajectory:
            for lig_atom_index, prot_atom_index in anchors_dict.keys():
                # noinspection PyUnresolvedReferences
                distance = dist(
                    mda.AtomGroup([u.atoms[lig_atom_index]]),
                    mda.AtomGroup([u.atoms[prot_atom_index]]),
                    box=frame.dimensions,
                )[2][0]
                anchors_dict[(lig_atom_index, prot_atom_index)]["dists"].append(distance)

        # change lists to numpy arrays
        for pair in anchors_dict.keys():
            anchors_dict[pair]["dists"] = np.array(anchors_dict[pair]["dists"])

        # calculate average and SD
        for pair in anchors_dict.keys():
            anchors_dict[pair]["avg_dist"] = anchors_dict[pair]["dists"].mean()
            anchors_dict[pair]["sd_dist"] = anchors_dict[pair]["dists"].std()

        # get n pairs with lowest SD
        pairs_ordered_sd = []
        for atom_pair in sorted(anchors_dict.items(), key=lambda pair_atms: pair_atms[1]["sd_dist"]):
            pairs_ordered_sd.append(atom_pair[0])

        boresch_dof_list = ["r", "thetaA", "thetaB", "phiA", "phiB", "phiC", "thetaR", "thetaL"]
        boresch_dof_dict = {}
        for pair in pairs_ordered_sd[:200]:
            boresch_dof_dict[pair] = {}
            l1_idx, r1_idx = pair
            _, l2_idx, l3_idx = self.get_anchor_ats(l1_idx, u)
            _, r2_idx, r3_idx = self.get_anchor_ats(r1_idx, u)
            boresch_dof_dict[pair]["anchor_ats"] = [l1_idx, l2_idx, l3_idx, r1_idx, r2_idx, r3_idx]

            # Add sub dictionaries for each Boresch degree of freedom
            for dof in boresch_dof_list:
                boresch_dof_dict[pair][dof] = {}
                boresch_dof_dict[pair][dof]["values"] = []

            # Populate these dictionaries with values from trajectory
            n_frames = len(u.trajectory)

            for i, frame in enumerate(u.trajectory):
                r, thetaA, thetaB, phiA, phiB, phiC, thetaR, thetaL = self.get_boresch_dof(
                    l1_idx, l2_idx, l3_idx, r1_idx, r2_idx, r3_idx, u
                )
                boresch_dof_dict[pair]["r"]["values"].append(r)
                boresch_dof_dict[pair]["thetaA"]["values"].append(thetaA)
                boresch_dof_dict[pair]["thetaB"]["values"].append(thetaB)
                boresch_dof_dict[pair]["phiA"]["values"].append(phiA)
                boresch_dof_dict[pair]["phiB"]["values"].append(phiB)
                boresch_dof_dict[pair]["phiC"]["values"].append(phiC)
                boresch_dof_dict[pair]["thetaR"]["values"].append(thetaR)
                boresch_dof_dict[pair]["thetaL"]["values"].append(thetaL)

                if i == n_frames - 1:
                    boresch_dof_dict[pair]["tot_var"] = 0
                    for dof in boresch_dof_list:
                        boresch_dof_dict[pair][dof]["values"] = np.array(boresch_dof_dict[pair][dof]["values"])
                        boresch_dof_dict[pair][dof]["avg"] = boresch_dof_dict[pair][dof]["values"].mean()
                        # For dihedrals, compute variance and mean based on list of values corrected for periodic boundary at
                        # pi radians, because there is no problem with dihedrals in this region. Should have been done with
                        # circmean from scipy - this is used in later implementations e.g. in BioSimSpace
                        if dof[:3] == "phi":
                            avg = boresch_dof_dict[pair][dof]["avg"]

                            # correct variance - fully rigorous
                            corrected_values_sd = []
                            for val in boresch_dof_dict[pair][dof]["values"]:
                                dtheta = abs(val - avg)
                                corrected_values_sd.append(min(dtheta, 2 * np.pi - dtheta))
                            corrected_values_sd = np.array(corrected_values_sd)
                            boresch_dof_dict[pair][dof]["sd"] = corrected_values_sd.std()

                            # Correct mean (will fail if very well split above and below 2pi)
                            # get middle of interval based on current mean
                            corrected_values_avg = []
                            periodic_bound = avg - np.pi
                            if periodic_bound < -np.pi:
                                periodic_bound += 2 * np.pi
                            # shift vals from below periodic bound to above
                            for val in boresch_dof_dict[pair][dof]["values"]:
                                if val < periodic_bound:
                                    corrected_values_avg.append(val + 2 * np.pi)
                                else:
                                    corrected_values_avg.append(val)
                            corrected_values_avg = np.array(corrected_values_avg)
                            mean_corrected = corrected_values_avg.mean()
                            # shift mean back to normal range
                            if mean_corrected > np.pi:
                                boresch_dof_dict[pair][dof]["avg"] = mean_corrected - 2 * np.pi
                            else:
                                boresch_dof_dict[pair][dof]["avg"] = mean_corrected

                        else:
                            boresch_dof_dict[pair][dof]["sd"] = boresch_dof_dict[pair][dof]["values"].std()
                        # Exclude variance of internal angles as these are not restrained
                        if dof != "thetaR" and dof != "thetaL":
                            boresch_dof_dict[pair]["tot_var"] += boresch_dof_dict[pair][dof]["sd"] ** 2
                        # Assume Gaussian distributions and calculate force constants for harmonic potentials
                        # so as to reproduce these distributions
                        boresch_dof_dict[pair][dof]["k"] = 0.593 / (
                            boresch_dof_dict[pair][dof]["sd"] ** 2
                        )  # RT at 289 K is 0.593 kcal

        pairs_ordered_boresch_var = []
        for atom_pair in sorted(boresch_dof_dict.items(), key=lambda pair_atms: pair_atms[1]["tot_var"]):
            pairs_ordered_boresch_var.append(atom_pair[0])

        # Filter out r <1, theta >150 or < 30
        selected_pairs_boresch = []
        for pair in pairs_ordered_boresch_var:
            cond_dist = boresch_dof_dict[pair]["r"]["avg"] > 1
            avg_angles = []
            # angles = ["thetaA", "thetaB", "thetaR","thetaL"] # also check internal angles
            angles = ["thetaA", "thetaB"]  # May also be good to check internal angles
            for angle in angles:
                avg_angles.append(boresch_dof_dict[pair][angle]["avg"])
            cond_angles = list(map(lambda x: (2.62 > x > 0.52), avg_angles))
            if cond_dist and all(cond_angles):
                selected_pairs_boresch.append(pair)

        self.write_boresch_restraints(boresch_dof_dict, selected_pairs_boresch[0], self.work_dir / "rest.in")
        self.output_artifacts = self.fill_output_artifacts(sysname)
        return self.output_artifacts

    @staticmethod
    def write_boresch_restraints(boresch_dof_dict: dict, pair, output_path: filepath_t) -> None:
        l1 = boresch_dof_dict[pair]["anchor_ats"][0]
        l2 = boresch_dof_dict[pair]["anchor_ats"][1]
        l3 = boresch_dof_dict[pair]["anchor_ats"][2]
        r1 = boresch_dof_dict[pair]["anchor_ats"][3]
        r2 = boresch_dof_dict[pair]["anchor_ats"][4]
        r3 = boresch_dof_dict[pair]["anchor_ats"][5]
        r0 = boresch_dof_dict[pair]["r"]["avg"]
        thetaA0 = boresch_dof_dict[pair]["thetaA"]["avg"]
        thetaB0 = boresch_dof_dict[pair]["thetaB"]["avg"]
        phiA0 = boresch_dof_dict[pair]["phiA"]["avg"]
        phiB0 = boresch_dof_dict[pair]["phiB"]["avg"]
        phiC0 = boresch_dof_dict[pair]["phiC"]["avg"]
        kr = boresch_dof_dict[pair]["r"]["k"] / 2
        kthetaA = boresch_dof_dict[pair]["thetaA"]["k"] / 2
        kthetaB = boresch_dof_dict[pair]["thetaB"]["k"] / 2
        kphiA = boresch_dof_dict[pair]["phiA"]["k"] / 2
        kphiB = boresch_dof_dict[pair]["phiB"]["k"] / 2
        kphiC = boresch_dof_dict[pair]["phiC"]["k"] / 2
        l1i = l1 + 1
        l2i = l2 + 1
        l3i = l3 + 1
        r1i = r1 + 1
        r2i = r2 + 1
        r3i = r3 + 1
        zero = 0.0

        with open(output_path, "w") as fh:
            fh.write(f"&rst iat={r1i},{l1i},0\n")
            fh.write(f"  r1={zero:.5f},r2={r0:.5f},r3={r0:.5f},r4=999.000,rk2={kr:.2f}, rk3={kr:.2f}/\n")
            fh.write(f"&rst iat={r2i},{r1i},{l1i},0\n")
            fh.write(
                f"  r1={-180.0:.5f},r2={np.degrees(thetaA0):.5f},r3={np.degrees(thetaA0):.5f},r4=180.000,rk2={kthetaA:.2f}, rk3={kthetaA:.2f}/\n"
            )
            fh.write(f"&rst iat={r1i},{l1i},{l2i},0\n")
            fh.write(
                f"  r1={-180.0:.5f},r2={np.degrees(thetaB0):.5f},r3={np.degrees(thetaB0):.5f},r4=180.000,rk2={kthetaB:.2f}, rk3={kthetaB:.2f}/\n"
            )
            fh.write(f"&rst iat={r3i},{r2i},{r1i},{l1i},0\n")
            fh.write(
                f"  r1={-180.0:.5f},r2={np.degrees(phiA0):.5f},r3={np.degrees(phiA0):.5f},r4=180.000,rk2={kphiA:.2f}, rk3={kphiA:.2f}/\n"
            )
            fh.write(f"&rst iat={r2i},{r1i},{l1i},{l2i},0\n")
            fh.write(
                f"  r1={-180.0:.5f},r2={np.degrees(phiB0):.5f},r3={np.degrees(phiB0):.5f},r4=180.000,rk2={kphiB:.2f}, rk3={kphiB:.2f}/\n"
            )
            fh.write(f"&rst iat={r1i},{l1i},{l2i},{l3i},0\n")
            fh.write(
                f"  r1={-180.0:.5f},r2={np.degrees(phiC0):.5f},r3={np.degrees(phiC0):.5f},r4=180.000,rk2={kphiC:.2f}, rk3={kphiC:.2f}/\n"
            )

    @staticmethod
    def get_distance(idx1, idx2, u):
        """Distance in Angstroms"""
        # noinspection PyUnresolvedReferences
        distance = dist(mda.AtomGroup([u.atoms[idx1]]), mda.AtomGroup([u.atoms[idx2]]), box=u.dimensions)[2][0]
        return distance

    @staticmethod
    def get_angle(idx1, idx2, idx3, u):
        """Angle in rad"""
        C = u.atoms[idx1].position
        B = u.atoms[idx2].position
        A = u.atoms[idx3].position
        BA = A - B
        BC = C - B
        angle = np.arccos(np.dot(BA, BC) / (norm(BA) * norm(BC)))
        return angle

    @staticmethod
    def get_dihedral(idx1, idx2, idx3, idx4, u):
        """Dihedral in rad"""
        positions = [u.atoms[idx].position for idx in [idx1, idx2, idx3, idx4]]
        dihedral = calc_dihedrals(positions[0], positions[1], positions[2], positions[3], box=u.dimensions)
        return dihedral

    def get_boresch_dof(self, l1, l2, l3, r1, r2, r3, u):
        """Calculate Boresch degrees of freedom from indices of anchor atoms"""
        # Ordering of connection of anchors is r3,r2,r1,l1,l2,l3
        r = self.get_distance(r1, l1, u)
        thetaA = self.get_angle(r2, r1, l1, u)
        thetaB = self.get_angle(r1, l1, l2, u)
        phiA = self.get_dihedral(r3, r2, r1, l1, u)
        phiB = self.get_dihedral(r2, r1, l1, l2, u)
        phiC = self.get_dihedral(r1, l1, l2, l3, u)
        # Not restrained but distance from coolinearity must be checked
        thetaR = self.get_angle(r3, r2, r1, u)  # Receptor internal angle
        thetaL = self.get_angle(l1, l2, l3, u)  # Ligand internal angle
        return r, thetaA, thetaB, phiA, phiB, phiC, thetaR, thetaL

    @staticmethod
    def get_anchor_ats(a1_idx, u):
        """Takes in index of anchor atom 1 and universe and returns
        list of all three anchor atoms, which are chosen to be bonded
        and not H"

        Args:
            a1_idx (int): Index of the first anchor atom
            u (mda universe): The mda universe

        Returns:
            ints: The indices of all three anchor points
        """

        a1_at = u.atoms[a1_idx]
        bonded_heavy_at = a1_at.bonded_atoms.select_atoms("not name H*")
        a2_idx = bonded_heavy_at[0].index

        if len(bonded_heavy_at) > 1:
            # not at end of chain
            a3_idx = bonded_heavy_at[1].index
            # Might be better to return all possible combinations
        else:
            # at end of chain, get next heavy atom along
            a3_idx = bonded_heavy_at[0].bonded_atoms.select_atoms("not name H*")[1].index
            # Check that we have not just moved back to first atom
            if a3_idx == a1_idx:
                a3_idx = bonded_heavy_at[0].bonded_atoms.select_atoms("not name H*")[0].index

        return a1_idx, a2_idx, a3_idx

    def _try_and_skip(self, sysname: str) -> bool:
        if self.skippable:
            try:
                self.output_artifacts = self.fill_output_artifacts(sysname)
                self.node_logger.info(f"Skipped {self.id} WorkNode.")
                return True
            except (FileNotFoundError, ValueError) as e:
                self.node_logger.info(f"Can't skip {self.id} Got: {e}")
        return False

    def fill_output_artifacts(self, sysname: str) -> ArtifactContainer:
        return ArtifactContainer(
            sysname,
            (BoreschRestraints(self.work_dir / "rest.in"),),
        )
