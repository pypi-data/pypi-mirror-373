from typing import Optional, Sequence

import attrs

from amberflow.artifacts import (
    AnhilateParameters,
    LambdaParameters,
    BaseComplexTopologyFile,
    BaseBinderTopologyFile,
    BaseBinderStructureFile,
    BaseComplexStructureFile,
    BoreschRestraints,
    BaseComplexStructureReferenceFile,
    BaseBinderStructureReferenceFile,
)
from amberflow.flows import BaseFlow
from amberflow.worknodes import (
    QuickLambdaSchedule,
    LambdaAnhilation,
    LambdaMDRun,
    Amber2Dats,
    GetXML,
    EdgeMBAR,
    Filter,
    GenerateLambdaScheduleFile,
)

__all__ = ("FlowABFE1",)


class FlowABFE1(BaseFlow):
    """
    An end-to-end flow for Alchemical Free Energy (AFE) calculations.

    This flow orchestrates the entire AFE workflow for both a complex and a
    ligand system. It begins by preparing the systems (annihilation), then
    runs a multi-stage MD simulation (heating, equilibration, production)
    across a series of lambda windows. Finally, it post-processes the
    trajectories and performs MBAR analysis to calculate the free energy.

    The ligand is assumed to be the first residue in the complex topology.

    Parameters
    ----------
    name : str, optional
        The name of the flow instance (default: "abfe1").
    binder_nlambdas : int, optional
        The number of lambda windows for the binder (default: 12).
    binder_schedule : str, optional
        The lambda schedule type for the binder (default: "s2inverse").
    complex_nlambdas : int, optional
        The number of lambda windows for the complex (default: 12).
    complex_schedule : str, optional
        The lambda schedule type for the complex (default: "s2inverse").
    heating_restraint_mask : str
        Amber mask for applying restraints during the heating phase.
    heating_restraint_wt : int, optional
        The weight for the heating restraints (default: 5).
    complex_restraint_mask : Optional[str], optional
        Amber mask for positional restraints on the complex during equilibration
        (default: None).
    complex_restraint_wt : Optional[int], optional
        Weight for the complex positional restraints (default: None).
    complex_rmsd_mask : Optional[str], optional
        Amber mask for a single RMSD restraint on the complex (default: None).
    complex_rmsd_strength : float, optional
        Strength for the single RMSD restraint on the complex (default: 5).
    complex_rmsd_ti : int, optional
        Time interval for the single RMSD restraint on the complex (default: 2).
    complex_rmsd_mask1 : Optional[str], optional
        Amber mask for the first of a dual RMSD restraint pair on the complex
        (default: None).
    complex_rmsd_strength1 : float, optional
        Strength for the first dual RMSD restraint (default: 5).
    complex_rmsd_ti1 : int, optional
        Time interval for the first dual RMSD restraint (default: 2).
    complex_rmsd_mask2 : Optional[str], optional
        Amber mask for the second of a dual RMSD restraint pair on the complex
        (default: None).
    complex_rmsd_strength2 : float, optional
        Strength for the second dual RMSD restraint (default: 5).
    complex_rmsd_ti2 : int, optional
        Time interval for the second dual RMSD restraint (default: 1).
    complex_rmsd_type : int, optional
        Type of RMSD restraint for the complex (default: 0).
    binder_rmsd_mask : Optional[str]
        Amber mask for a single RMSD restraint on the binder (default: None).
    binder_rmsd_strength : float, optional
        Strength for the single RMSD restraint on the binder (default: 5).
    binder_rmsd_ti : int, optional
        Time interval for the single RMSD restraint on the binder (default: 2).
    binder_rmsd_mask1 : Optional[str]
        Amber mask for the first of a dual RMSD restraint pair on the binder
        (default: None).
    binder_rmsd_strength1 : float, optional
        Strength for the first dual RMSD restraint (default: 5).
    binder_rmsd_ti1 : int, optional
        Time interval for the first dual RMSD restraint (default: 2).
    binder_rmsd_mask2 : Optional[str], optional
        Amber mask for the second of a dual RMSD restraint pair on the binder
        (default: None).
    binder_rmsd_strength2 : float, optional
        Strength for the second dual RMSD restraint (default: 5).
    binder_rmsd_ti2 : int, optional
        Time interval for the second dual RMSD restraint (default: 1).
    binder_rmsd_type : int, optional
        Type of RMSD restraint for the binder (default: 0).
    nstlim : int, optional
        Number of steps for MD heating and equilibration runs (default: 100000).
    nstlim_pdt : int, optional
        Number of steps for the final production MD run (default: 125).
    ntwx_pdt: int, optional
        Frequency of trajectory writing during production
    numexchg : int, optional
        Number of exchange attempts between lambda windows (default: 10000).
    nmropt : bool, optional
        If True, enables NMR restraints for the complex system (default: False).
    max_systems_binder : int, optional
        Maximum number of binder systems to run in parallel (default: 1).
    max_systems_complex : int, optional
        Maximum number of complex systems to run in parallel (default: 1).
    skippable : bool, optional
        If True, allows individual worknodes to be skipped if their outputs
        already exist (default: True).
    skip_analysis : bool, optional
        If True, skips the final analysis steps (default: False).
    """

    def __init__(
        self,
        name: str = "abfe1",
        *,
        binder_nlambdas: Optional[int] = None,
        binder_schedule: str = "s2inverse",
        complex_nlambdas: Optional[int] = None,
        complex_schedule: str = "s2inverse",
        binder_windows: Optional[Sequence[float]] = None,
        complex_windows: Optional[Sequence[float]] = None,
        heating_restraint_mask: str,
        heating_restraint_wt: int = 5,
        complex_restraint_mask: Optional[str] = None,
        complex_restraint_wt: Optional[int] = None,
        complex_rmsd_mask: Optional[str] = None,
        complex_rmsd_strength: float = 5,
        complex_rmsd_ti: int = 2,
        complex_rmsd_mask1: Optional[str] = None,
        complex_rmsd_strength1: float = 5,
        complex_rmsd_ti1: int = 2,
        complex_rmsd_mask2: Optional[str] = None,
        complex_rmsd_strength2: float = 5,
        complex_rmsd_ti2: int = 1,
        complex_rmsd_type: int = 0,
        binder_rmsd_mask: Optional[str] = None,
        binder_rmsd_strength: float = 5,
        binder_rmsd_ti: int = 2,
        binder_rmsd_mask1: Optional[str] = None,
        binder_rmsd_strength1: float = 5,
        binder_rmsd_ti1: int = 2,
        binder_rmsd_mask2: Optional[str] = None,
        binder_rmsd_strength2: float = 5,
        binder_rmsd_ti2: int = 1,
        binder_rmsd_type: int = 0,
        nstlim: int = 100000,
        nstlim_pdt: int = 125,
        ntwx_pdt: int = 0,
        numexchg: int = 10000,
        nmropt: bool = False,
        edgembar_mode: str = "BAR",
        max_systems_binder: int = 1,
        max_systems_complex: int = 1,
        trials: int = 1,
        skippable: bool = True,
        skip_analysis: bool = False,
    ):
        super().__init__(name)
        # Set all parameters as attributes
        for name, value in locals().items():
            if name != "self":
                setattr(self, name, value)

        # Filter for the final relaxed structures and topologies
        wnf_binder_top = Filter(f"wnf_binder_top_{self.name}", artifact_types=(BaseBinderTopologyFile,))
        wnf_binder_rst = Filter(f"wnf_binder_rst_{self.name}", artifact_types=(BaseBinderStructureFile,))
        wnf_complex_top = Filter(f"wnf_complex_top_{self.name}", artifact_types=(BaseComplexTopologyFile,))
        wnf_complex_rst = Filter(f"wnf_complex_rst_{self.name}", artifact_types=(BaseComplexStructureFile,))
        wnf_complex_ref = Filter(
            "wnf_complex_lambda_ref",
            artifact_types=(BaseComplexStructureReferenceFile,),
            skippable=skippable,
        )
        wnf_binder_ref = Filter(
            "wnf_binder_lambda_ref",
            artifact_types=(BaseBinderStructureReferenceFile,),
            skippable=skippable,
        )
        wnf_complex_nmr_restraints = Filter("wnf_complex_nmr_restraints", artifact_types=(BoreschRestraints,))
        restrained_str = (
            "_restrained" if complex_restraint_mask is not None and complex_restraint_wt is not None else ""
        )
        nmropt_str = "_nmropt" if nmropt else ""

        complex_rmsd_str = self._setup_rmsd(complex_rmsd_mask, complex_rmsd_mask1, complex_rmsd_mask2)
        binder_rmsd_str = self._setup_rmsd(binder_rmsd_mask, binder_rmsd_mask1, binder_rmsd_mask2)

        # Lambda schedule generation
        if binder_windows is None:
            qls_binder = QuickLambdaSchedule(wnid="qls_binder", nlambdas=binder_nlambdas, schedule=binder_schedule)
        else:
            qls_binder = QuickLambdaSchedule(wnid="qls_binder", lambdas=binder_windows)
        if complex_windows is None:
            qls_complex = QuickLambdaSchedule(wnid="qls_complex", nlambdas=complex_nlambdas, schedule=complex_schedule)
        else:
            qls_complex = QuickLambdaSchedule(wnid="qls_complex", lambdas=complex_windows)

        # Annihilation step
        anhilate_params = AnhilateParameters(timask1=":1", timask2="", scmask1=":1", scmask2="")

        anhilate_binder = LambdaAnhilation(
            wnid="anhilate_binder",
            mdin_template="min_icfe",
            mdparameters=anhilate_params,
            engine="pmemd.cuda",
            skippable=skippable,
        )

        anhilate_complex = LambdaAnhilation(
            wnid="anhilate_complex",
            mdin_template=f"min_icfe{restrained_str}{nmropt_str}",
            mdparameters=anhilate_params,
            engine="pmemd.cuda",
            skippable=skippable,
        )

        # Generate LambdaScheduleFile
        glsch = GenerateLambdaScheduleFile(
            wnid="gen_lambda_schedule_file",
            lambda_type="TypeRestBA",
            function_type="smooth_step2",
            match_type="symmetric",
            parameter1=1.0,
            parameter2=0.0,
        )

        # Heating
        heat_params = LambdaParameters(
            nstlim=nstlim,
            irest=0,
            ntx=1,
            timask1=":1",
            timask2="",
            scmask1=":1",
            scmask2="",
            iwrap=0,
            dt=0.001,
            tempi=100,
            temp0=298,
            restraintmask=heating_restraint_mask,
            restraint_wt=heating_restraint_wt,
        )
        # Get the binder MD parameters
        binder_heat_params = self._evolve_binder_rmsd_params(heat_params)
        heat_binder = LambdaMDRun(
            wnid="heat_binder",
            mdin_template=f"md_icfe{binder_rmsd_str}_varying",
            engine="pmemd.cuda.MPI",
            mdparameters=binder_heat_params,
            max_systems=max_systems_binder,
            skippable=skippable,
        )

        # Get the binder MD parameters
        complex_heat_params = self._evolve_complex_rmsd_params(heat_params)
        heat_complex = LambdaMDRun(
            wnid="heat_complex",
            mdin_template=f"md_icfe{restrained_str}{complex_rmsd_str}{nmropt_str}_varying",
            ifmbar=True,
            engine="pmemd.cuda.MPI",
            mdparameters=complex_heat_params,
            max_systems=max_systems_complex,
            skippable=skippable,
        )

        ### Equilibration ###
        # 1 #
        equil_params = LambdaParameters(
            nstlim=nstlim,
            irest=1,
            ntx=5,
            timask1=":1",
            timask2="",
            scmask1=":1",
            scmask2="",
            iwrap=0,
            dt=0.001,
            numexchg=numexchg,
        )

        binder_equil_params = self._evolve_binder_rmsd_params(equil_params)
        equil1_binder = LambdaMDRun(
            wnid="equil1_binder",
            mdin_template=f"md_icfe{binder_rmsd_str}",
            engine="pmemd.cuda.MPI",
            mdparameters=binder_equil_params,
            max_systems=max_systems_binder,
            skippable=skippable,
        )

        if restrained_str != "":
            # noinspection PyTypeChecker
            equil_params = attrs.evolve(
                equil_params, restraintmask=complex_restraint_mask, restraint_wt=complex_restraint_wt
            )

        complex_equil_params = self._evolve_complex_rmsd_params(equil_params)
        equil1_complex = LambdaMDRun(
            wnid="equil1_complex",
            mdin_template=f"md_icfe{restrained_str}{complex_rmsd_str}{nmropt_str}",
            engine="pmemd.cuda.MPI",
            mdparameters=complex_equil_params,
            max_systems=max_systems_complex,
            skippable=skippable,
        )

        # 2 #
        equil_params = attrs.evolve(equil_params, dt=0.002)
        binder_equil_params = self._evolve_binder_rmsd_params(equil_params)
        equil2_binder = LambdaMDRun(
            wnid="equil2_binder",
            mdin_template=f"md_icfe{binder_rmsd_str}",
            engine="pmemd.cuda.MPI",
            mdparameters=binder_equil_params,
            max_systems=max_systems_binder,
            skippable=skippable,
        )

        complex_equil_params = self._evolve_complex_rmsd_params(equil_params)
        equil2_complex = LambdaMDRun(
            wnid="equil2_complex",
            mdin_template=f"md_icfe{restrained_str}{complex_rmsd_str}{nmropt_str}",
            engine="pmemd.cuda.MPI",
            mdparameters=complex_equil_params,
            max_systems=max_systems_complex,
            skippable=skippable,
        )
        # 3 #
        equil_params = attrs.evolve(equil_params, dt=0.004)
        binder_equil_params = self._evolve_binder_rmsd_params(equil_params)
        equil3_binder = LambdaMDRun(
            wnid="equil3_binder",
            mdin_template=f"md_icfe{binder_rmsd_str}",
            engine="pmemd.cuda.MPI",
            mdparameters=binder_equil_params,
            max_systems=max_systems_binder,
            skippable=skippable,
        )

        complex_equil_params = self._evolve_complex_rmsd_params(equil_params)
        equil3_complex = LambdaMDRun(
            wnid="equil3_complex",
            mdin_template=f"md_icfe{restrained_str}{complex_rmsd_str}{nmropt_str}",
            engine="pmemd.cuda.MPI",
            mdparameters=complex_equil_params,
            max_systems=max_systems_complex,
            skippable=skippable,
        )

        ### Production ###
        # Create reference structures
        pdt_params = attrs.evolve(
            equil_params,
            nstlim=nstlim_pdt,
            ntwx=ntwx_pdt,
            irest=0,
            ntx=1,
        )
        pdt_nodes = []
        for i in range(1, trials + 1):
            binder_pdt_params = self._evolve_binder_rmsd_params(pdt_params)
            pdt_binder = LambdaMDRun(
                wnid=f"t{i}_binder",
                mdin_template=f"ti_exch_mbar{binder_rmsd_str}",
                ifmbar=True,
                exchange=True,
                engine="pmemd.cuda.MPI",
                mdparameters=binder_pdt_params,
                max_systems=max_systems_binder,
                skippable=skippable,
            )

            complex_pdt_params = self._evolve_complex_rmsd_params(pdt_params)
            pdt_complex = LambdaMDRun(
                wnid=f"t{i}_complex",
                mdin_template=f"ti_exch_mbar{restrained_str}{complex_rmsd_str}{nmropt_str}",
                ifmbar=True,
                exchange=True,
                engine="pmemd.cuda.MPI",
                mdparameters=complex_pdt_params,
                max_systems=max_systems_complex,
                skippable=skippable,
            )
            pdt_nodes.append((pdt_binder, pdt_complex))

        # Post-processing and analysis
        a2d = Amber2Dats(wnid="a2d", skippable=skip_analysis)
        xml = GetXML(wnid="xml", skippable=skip_analysis)
        mbar = EdgeMBAR(wnid="edge_mbar", mode=edgembar_mode, skippable=skip_analysis)

        # Add nodes to the DAG
        self.dag.add_nodes_from(
            [
                wnf_binder_top,
                wnf_binder_rst,
                wnf_complex_top,
                wnf_complex_rst,
                wnf_complex_ref,
                wnf_binder_ref,
                qls_binder,
                qls_complex,
                anhilate_binder,
                anhilate_complex,
                heat_binder,
                heat_complex,
                equil1_binder,
                equil1_complex,
                equil2_binder,
                equil2_complex,
                equil3_binder,
                equil3_complex,
                a2d,
                xml,
                mbar,
            ]
        )
        if nmropt:
            self.dag.add_node(wnf_complex_nmr_restraints)

        # Connect the workflow
        self.dag.add_edge(self.root, wnf_binder_top)
        self.dag.add_edge(self.root, wnf_binder_rst)
        self.dag.add_edge(self.root, wnf_complex_top)
        self.dag.add_edge(self.root, wnf_complex_rst)
        self.dag.add_edge(self.root, wnf_complex_ref)
        self.dag.add_edge(self.root, wnf_binder_ref)
        self.dag.add_edge(self.root, qls_binder)
        self.dag.add_edge(self.root, qls_complex)
        self.dag.add_edge(self.root, glsch)
        if nmropt:
            self.dag.add_edge(self.root, wnf_complex_nmr_restraints)

        # Binder path
        # Anhilation
        self.dag.add_edge(wnf_binder_top, anhilate_binder)
        self.dag.add_edge(wnf_binder_rst, anhilate_binder)
        self.dag.add_edge(qls_binder, anhilate_binder)
        # Heating

        self.dag.add_edge(anhilate_binder, heat_binder)
        self.dag.add_edge(wnf_binder_ref, heat_binder)
        # Equilibration 1
        self.dag.add_edge(heat_binder, equil1_binder)
        # Equilibration 2
        self.dag.add_edge(equil1_binder, equil2_binder)
        # Equilibration 3
        self.dag.add_edge(equil2_binder, equil3_binder)
        # Production trials
        for pdt_binder, _ in pdt_nodes:
            self.dag.add_edge(equil3_binder, pdt_binder)
            self.dag.add_edge(pdt_binder, a2d)

        # Complex path
        # Anhilation
        if nmropt:
            self.dag.add_edge(wnf_complex_nmr_restraints, anhilate_complex)
        self.dag.add_edge(wnf_complex_top, anhilate_complex)
        self.dag.add_edge(wnf_complex_rst, anhilate_complex)
        self.dag.add_edge(qls_complex, anhilate_complex)
        # Heating
        self.dag.add_edge(anhilate_complex, heat_complex)
        self.dag.add_edge(glsch, heat_complex)
        self.dag.add_edge(wnf_complex_ref, heat_complex)
        # Equilibration 1
        self.dag.add_edge(heat_complex, equil1_complex)
        # Equilibration 2
        self.dag.add_edge(equil1_complex, equil2_complex)
        # Equilibration 3
        self.dag.add_edge(equil2_complex, equil3_complex)
        # Production trials
        for _, pdt_complex in pdt_nodes:
            self.dag.add_edge(equil3_complex, pdt_complex)
            # self.dag.add_edge(pdt_complex, a2d_complex)
            self.dag.add_edge(pdt_complex, a2d)

        # Analysis path
        self.dag.add_edge(a2d, xml)
        self.dag.add_edge(xml, mbar)
        self.dag.add_edge(mbar, self.leaf)

    @staticmethod
    def _setup_rmsd(rmsd_mask, rmsd_mask1, rmsd_mask2) -> str:
        if rmsd_mask is not None:
            return "_rmsd"
        elif rmsd_mask1 is not None and rmsd_mask2 is not None:
            return "_rmsd2"
        else:
            return ""

    def _get_rmsd_kwargs(self, prefix: str) -> dict:
        """Helper to get rmsd attributes based on a prefix."""
        attr_suffixes = [
            "rmsd_mask",
            "rmsd_strength",
            "rmsd_ti",
            "rmsd_mask1",
            "rmsd_strength1",
            "rmsd_ti1",
            "rmsd_mask2",
            "rmsd_strength2",
            "rmsd_ti2",
            "rmsd_type",
        ]

        # Build the keyword arguments dynamically
        kwargs = {suffix: getattr(self, f"{prefix}_{suffix}") for suffix in attr_suffixes}
        return kwargs

    def _evolve_binder_rmsd_params(self, params: LambdaParameters) -> LambdaParameters:
        kwargs = self._get_rmsd_kwargs("binder")
        return attrs.evolve(params, **kwargs)

    def _evolve_complex_rmsd_params(self, params: LambdaParameters) -> LambdaParameters:
        kwargs = self._get_rmsd_kwargs("complex")
        return attrs.evolve(params, **kwargs)
