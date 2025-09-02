from typing import Optional

import attrs

from amberflow.flows import BaseFlow
from amberflow.worknodes import MDRun, Filter, CreateReferenceStructure
from amberflow.artifacts import (
    MinRestrainedParameters,
    HeatingParameters,
    MDRestrainedParameters,
    BaseComplexTopologyFile,
    BaseBinderTopologyFile,
    BaseBinderStructureFile,
    BaseComplexStructureFile,
    MDParameters,
    BaseComplexStructureReferenceFile,
    BaseBinderStructureReferenceFile,
)

__all__ = ("FlowRoeRelax1",)


class FlowRoeRelax1(BaseFlow):
    """
    A flow for an MD relaxation protocol.

    This flow runs a relaxation protocol on a pair of complex and ligand
    systems. The protocol involves initial minimization, gradual heating,
    density equilibration, and a series of steps where positional
    restraints are slowly removed. This is loosely based on the protocol
    described by Roe [2].

    The first relaxation WorkNodes use the initial input frame as reference, until the first equilibration is completed,
    `density0`, after which it takes the final frame from `density0`, which is the first time the box gets adjusted,
    and it makes it the final reference. After that, all Worknodes get that frame as the reference structure.
    So,
    - clash minimization
    - minimization
    - densitiy 0
    - density 1

    use the initial frame (that came from the previous step) as a reference.
    After that, it's the output frame from density0 that's used as the actual reference structure.
    `density1` kind of does both things, since its input frame and the reference structure are the same thing.


    Parameters
    ----------
    name : str, optional
        The name of the flow instance, by default "relaxroe".
    complex_full_restraint_mask : str
        Amber mask for applying strong restraints on the whole solute during
        the initial clash-fixing minimization.
    complex_noh_restraint_mask : str
        Amber mask for applying restraints on all heavy atoms during heating,
        density equilibration, and initial relaxation stages.
    strong_restraint_wt : int, optional
        The weight (in kcal/mol·Å²) for the strong heavy-atom restraints,
        by default 50.
    bb_restraint_mask : str
        Amber mask for applying restraints on the protein backbone during the
        final relaxation stage.
    bb_restraint_wt : int, optional
        The weight (in kcal/mol·Å²) for the final backbone restraints,
        by default 5.
    relax_weights : tuple[int], optional
        A tuple of integers representing the restraint weights to be used
        in the gradual relaxation stages, by default (25, 10, 5, 2, 1).
    complex_free_restraint_mask : str, optional
        An optional Amber mask to apply during the final free MD run for the complex.
    complex_free_restraint_wt : int, optional
        The restraint weight for the optional final restraint mask for the complex.
    nstlim : int, optional
        The number of MD steps for most of the relaxation stages,
        by default 50000.
    nstlim_density_equilibration : int, optional
        The number of MD steps for the density equilibration stages
        by default 25000.
    maxcyc : int, optional
        The maximum number of minimization cycles, by default 1000.
    ncyc : int, optional
        The number of steepest descent minimization cycles, by default 100.
    skippable : bool, optional
        If True, allows individual worknodes within the flow to be skipped
        if their outputs already exist, by default True.

    References
    ----------
    1. Amber tutorial: https://ambermd.org/tutorials/basic/tutorial13/index.php
    2. Daniel R. Roe, Bernard R. Brooks;
       A protocol for preparing explicitly solvated systems for stable molecular dynamics simulations.
       J. Chem. Phys. 7 August 2020; 153 (5): 054123. https://doi.org/10.1063/5.0013849
    """

    def __init__(
        self,
        name: str = "relaxroe",
        *,
        complex_full_restraint_mask: str,
        complex_noh_restraint_mask: str,
        binder_full_restraint_mask: str,
        binder_noh_restraint_mask: str,
        strong_restraint_wt: int = 50,
        bb_restraint_mask: str,
        bb_restraint_wt: int = 5,
        relax_weights: tuple[int] = (25, 10, 5, 2, 1),
        complex_free_restraint_mask: Optional[str] = None,
        complex_free_restraint_wt: Optional[int] = None,
        nstlim: int = 1000000,
        ntpr: int = 1000,
        ntpr_pdt: int = 1000,
        nstlim_density_equilibration: int = 500000,
        maxcyc: int = 1000,
        ncyc: int = 100,
        iwrap: int = 0,
        nscm: int = 0,
        skippable: bool = True,
    ):
        super().__init__(name)

        # Filter initial artifacts
        wnf_binder_top = Filter("wnf_binder_top", artifact_types=(BaseBinderTopologyFile,), skippable=skippable)
        wnf_binder_rst = Filter("wnf_binder_rst", artifact_types=(BaseBinderStructureFile,), skippable=skippable)
        wnf_binder_ref = Filter(
            "wnf_binder_ref",
            artifact_types=(BaseBinderStructureReferenceFile,),
            skippable=skippable,
        )
        wnf_complex_top = Filter("wnf_complex_top", artifact_types=(BaseComplexTopologyFile,), skippable=skippable)
        wnf_complex_rst = Filter(
            "wnf_complex_rst",
            artifact_types=(BaseComplexStructureFile,),
            skippable=skippable,
        )
        wnf_complex_ref = Filter(
            "wnf_complex_ref",
            artifact_types=(BaseComplexStructureReferenceFile,),
            skippable=skippable,
        )

        # Relaxation protocol steps
        # Step 0: Very strong restraints on all atoms
        binder_clash0_params = MinRestrainedParameters(
            ncyc=50, maxcyc=200, restraintmask=binder_full_restraint_mask, restraint_wt=100
        )
        clash_fix_binder = MDRun(
            "clash_fix_binder",
            mdin_template="min_restrained",
            mdparameters=binder_clash0_params,
            engine="pmemd",
            skippable=skippable,
        )
        complex_clash0_params = attrs.evolve(binder_clash0_params, restraintmask=complex_full_restraint_mask)
        clash_fix_complex = MDRun(
            "clash_fix_complex",
            mdin_template="min_restrained",
            mdparameters=complex_clash0_params,
            engine="pmemd",
            skippable=skippable,
        )

        # Step 1: Minimize heavy atoms
        binder_min1_params = MinRestrainedParameters(
            restraintmask=binder_noh_restraint_mask,
            maxcyc=maxcyc,
            ncyc=ncyc,
            restraint_wt=strong_restraint_wt,
        )
        min1_binder = MDRun(
            "min_binder",
            mdin_template="min_restrained",
            mdparameters=binder_min1_params,
            skippable=skippable,
        )
        complex_clash0_params = attrs.evolve(binder_min1_params, restraintmask=complex_noh_restraint_mask)
        min1_complex = MDRun(
            "min_complex",
            mdin_template="min_restrained",
            mdparameters=complex_clash0_params,
            skippable=skippable,
        )

        # Create reference structures for cartesian restraints during this flow
        crs_density0_complex = CreateReferenceStructure(wnid="crs_density0_complex")
        crs_density0_binder = CreateReferenceStructure(wnid="crs_density0_binder")

        # Create reference structures for the output
        crs_min_complex = CreateReferenceStructure(wnid="crs_min_complex")
        crs_min_binder = CreateReferenceStructure(wnid="crs_min_binder")

        # Filter out the reference that came from the density0 step
        wnf_binder_ref_density0 = Filter(
            "wnf_binder_ref_density0",
            artifact_types=(BaseBinderStructureReferenceFile,),
            in_or_out="out",
            skippable=skippable,
        )
        wnf_complex_ref_density0 = Filter(
            "wnf_complex_rst_density0",
            artifact_types=(BaseComplexStructureReferenceFile,),
            in_or_out="out",
            skippable=skippable,
        )

        # Step 2: Heat the system
        binder_heat2_params = HeatingParameters(
            nstlim=nstlim,
            ntpr=ntpr,
            restraintmask=binder_noh_restraint_mask,
            restraint_wt=strong_restraint_wt,
        )
        heat2_binder = MDRun(
            "heat2_binder",
            mdin_template="md_restrained_varying",
            mdparameters=binder_heat2_params,
            skippable=skippable,
        )
        complex_heat2_params = attrs.evolve(binder_heat2_params, restraintmask=complex_noh_restraint_mask)
        heat2_complex = MDRun(
            "heat2_complex",
            mdin_template="md_restrained_varying",
            mdparameters=complex_heat2_params,
            skippable=skippable,
        )

        # Step 3: Density equilibration
        density_params_binder = MDRestrainedParameters(
            nstlim=nstlim_density_equilibration,  # Reduced nstlim for density equilibration, so pmemd.cuda doesn't complain
            dt=0.001,
            ntpr=ntpr,
            iwrap=iwrap,
            nscm=nscm,
            gamma_ln=2.0,
            restraintmask=binder_noh_restraint_mask,
            restraint_wt=strong_restraint_wt,
            cut=12.0,
        )
        density0_binder = MDRun(
            "density0_binder",
            mdin_template="md_restrained",
            mdparameters=density_params_binder,
            skippable=skippable,
        )
        density1_binder = MDRun(
            "density1_binder",
            mdin_template="md_restrained",
            mdparameters=density_params_binder,
            skippable=skippable,
        )
        density_params_complex = attrs.evolve(density_params_binder, restraintmask=complex_noh_restraint_mask)
        density0_complex = MDRun(
            "density0_complex",
            mdin_template="md_restrained",
            mdparameters=density_params_complex,
            skippable=skippable,
        )
        density1_complex = MDRun(
            "density1_complex",
            mdin_template="md_restrained",
            mdparameters=density_params_complex,
            skippable=skippable,
        )

        # Step 4: Gradually reduce restraints
        md_nodes = []
        for i, wt in enumerate(relax_weights):
            md_params_binder = MDRestrainedParameters(
                nstlim=nstlim,
                ntpr=ntpr,
                dt=0.001,
                iwrap=iwrap,
                nscm=nscm,
                gamma_ln=4.0,
                restraintmask=binder_noh_restraint_mask,
                restraint_wt=wt,
            )
            step_binder = MDRun(
                f"lower{i}_binder",
                mdin_template="md_restrained",
                mdparameters=md_params_binder,
                skippable=skippable,
            )
            density_params_complex = attrs.evolve(md_params_binder, restraintmask=complex_noh_restraint_mask)
            step_complex = MDRun(
                f"lower{i}_complex",
                mdin_template="md_restrained",
                mdparameters=density_params_complex,
                skippable=skippable,
            )
            md_nodes.append((step_binder, step_complex))

        # Step 5: Final relaxation with backbone restraints
        final_params = MDRestrainedParameters(
            nstlim=nstlim,
            ntpr=ntpr,
            dt=0.002,
            gamma_ln=5.0,
            ntwx=250,
            iwrap=iwrap,
            nscm=nscm,
            restraintmask=bb_restraint_mask,
            restraint_wt=bb_restraint_wt,
        )
        bb_binder = MDRun(
            "bb_binder",
            mdin_template="md_restrained",
            mdparameters=final_params,
            skippable=skippable,
        )
        bb_complex = MDRun(
            "bb_complex",
            mdin_template="md_restrained",
            mdparameters=final_params,
            skippable=skippable,
        )
        # Step 6: Free MD
        free_params = MDParameters(
            nstlim=nstlim,
            ntpr=ntpr_pdt,
            dt=0.004,
            gamma_ln=5.0,
            ntwx=250,
            iwrap=iwrap,
            nscm=nscm,
        )
        free_binder = MDRun(
            "free_binder",
            mdin_template="md",
            mdparameters=free_params,
            skippable=skippable,
        )
        if None in (complex_free_restraint_mask, complex_free_restraint_wt):
            mdin_template = "md"
        else:
            free_params = attrs.evolve(
                free_params, restraintmask=complex_free_restraint_mask, restraint_wt=complex_free_restraint_wt
            )
            mdin_template = "md_restrained"

        free_complex = MDRun(
            "free_complex",
            mdin_template=mdin_template,
            mdparameters=free_params,
            skippable=skippable,
        )

        # Add nodes to DAG
        self.dag.add_nodes_from(
            [
                wnf_binder_top,
                wnf_binder_rst,
                wnf_binder_ref,
                wnf_complex_top,
                wnf_complex_rst,
                wnf_complex_ref,
                clash_fix_binder,
                clash_fix_complex,
                min1_binder,
                min1_complex,
                crs_min_complex,
                crs_min_binder,
                crs_density0_complex,
                crs_density0_binder,
                heat2_binder,
                heat2_complex,
                density0_complex,
                density1_complex,
                density0_binder,
                density1_binder,
                bb_binder,
                bb_complex,
                wnf_binder_ref_density0,
                wnf_complex_ref_density0,
                free_binder,
                free_complex,
            ]
        )

        # Connect the workflow
        self.dag.add_edge(self.root, wnf_binder_top)
        self.dag.add_edge(self.root, wnf_binder_rst)
        self.dag.add_edge(self.root, wnf_binder_ref)
        self.dag.add_edge(self.root, wnf_complex_top)
        self.dag.add_edge(self.root, wnf_complex_rst)
        self.dag.add_edge(self.root, wnf_complex_ref)

        # Binder path
        self.dag.add_edge(wnf_binder_top, clash_fix_binder)
        self.dag.add_edge(wnf_binder_rst, clash_fix_binder)
        self.dag.add_edge(clash_fix_binder, min1_binder)
        self.dag.add_edge(wnf_binder_rst, crs_min_binder)
        self.dag.add_edge(min1_binder, heat2_binder)
        self.dag.add_edge(heat2_binder, density0_binder)
        self.dag.add_edge(density0_binder, crs_density0_binder)
        self.dag.add_edge(density0_binder, density1_binder)
        self.dag.add_edge(crs_density0_binder, density1_binder)

        # Restraints relaxation steps may vary
        previous_binder_step = density1_binder
        for step_binder, _ in md_nodes:
            self.dag.add_edge(previous_binder_step, step_binder)
            previous_binder_step = step_binder
        self.dag.add_edge(previous_binder_step, bb_binder)
        self.dag.add_edge(bb_binder, free_binder)

        # Complex path
        self.dag.add_edge(wnf_complex_top, clash_fix_complex)
        self.dag.add_edge(wnf_complex_rst, clash_fix_complex)
        self.dag.add_edge(clash_fix_complex, min1_complex)
        self.dag.add_edge(wnf_complex_rst, crs_min_complex)
        self.dag.add_edge(min1_complex, heat2_complex)
        self.dag.add_edge(heat2_complex, density0_complex)
        self.dag.add_edge(density0_complex, crs_density0_complex)
        self.dag.add_edge(density0_complex, density1_complex)
        self.dag.add_edge(crs_density0_complex, density1_complex)

        # Restraints relaxation steps may vary
        previous_complex_step = density1_complex
        for _, step_complex in md_nodes:
            self.dag.add_edge(previous_complex_step, step_complex)
            previous_complex_step = step_complex
        self.dag.add_edge(previous_complex_step, bb_complex)
        self.dag.add_edge(bb_complex, free_complex)

        # Connect to leaf
        self.dag.add_edge(crs_min_complex, self.leaf)
        self.dag.add_edge(crs_min_binder, self.leaf)
        self.dag.add_edge(free_binder, wnf_binder_ref_density0)
        self.dag.add_edge(free_complex, wnf_complex_ref_density0)
        self.dag.add_edge(wnf_binder_ref_density0, self.leaf)
        self.dag.add_edge(wnf_complex_ref_density0, self.leaf)
