from typing import Optional

from amberflow.artifacts import (
    BaseTargetStructureFile,
    LigandFrcmod,
    LigandLib,
    BaseComplexStructureFile,
    BaseBinderStructureFile,
    BinderLigandRestart,
    ComplexProteinLigandRestart,
    BinderLigandMol2,
)
from amberflow.artifacts.md import ComplexPeriodicBox, BinderPeriodicBox
from amberflow.flows import BaseFlow
from amberflow.worknodes import (
    Filter,
    AddChainid,
    JoinTargetBinder,
    BuildAFEBoxes,
    GenerateTopology,
    HMR,
    FFPOPT,
    CreateReferenceStructure,
)

__all__ = ("FlowAlt1Build",)


class FlowAlt1Build(BaseFlow):
    """
    This flow parametrizes binders, forms the complex, builds 1 box for all the systems, generates the topologies,
    performs Hydrogen Mass Repartition on both the target and the binder topologies, and optionally runs FFopt
    to fix the binder rotamers.

    Parameters
    ----------
    name : str, optional
        The name of the flow instance, Default: "build".

    to_guess : tuple, optional
        Topology attributes for MDAnalysis to guess when joining the target and binder, used by `JoinTargetBinder`
        and `BuildAFEBoxes`. Default: ("elements",).
    renumber : bool, optional
        Whether to renumber residues sequentially after joining, used by `JoinTargetBinder`. Default: True.
    solvent : str, optional
        The water model to use for solvation in `BuildAFEBoxes` and `GenerateTopology`. Default: "tip4pew".
    ions : str, optional
        The ion model to use in `GenerateTopology`. Default: "jc".
    box_or_oct : str, optional
        The shape of the periodic box (`box` or `oct`) to be specified in `GenerateTopology`. Default: "oct".
    skippable : bool, optional
        If True, allows individual worknodes within the flow to be skipped if their outputs already exist.
        Default: True.
    ffopt : bool, optional
        If True, add a final WorkNode to fix ligand rotamers.
        Works only if the binder ligand has an anionic amide group.
        Default: True.
    """

    def __init__(
        self,
        name: str = "build",
        to_guess: tuple = ("elements",),
        renumber: bool = True,
        solvent: str = "tip4pew",
        ions: str = "jc",
        box_or_oct: str = "oct",
        skippable: bool = True,
        ffopt: bool = True,
    ):
        super().__init__(name)

        wnf_binder_parameters = Filter(
            wnid="wnf_binder_parameters",
            artifact_types=(BinderLigandMol2, LigandFrcmod, LigandLib, BaseBinderStructureFile),
            skippable=skippable,
        )
        wnf1 = Filter(wnid="wnf1", artifact_types=(BaseTargetStructureFile,), skippable=skippable)
        addchainid = AddChainid(wnid="addchainid", skippable=skippable)
        jtb = JoinTargetBinder(wnid="jtb", to_guess=to_guess, renumber=renumber, skippable=skippable)
        bafeb = BuildAFEBoxes(wnid="bafeb", to_guess=to_guess, solvent=solvent, skippable=skippable)
        wnf2 = Filter(wnid="wnf2", artifact_types=(LigandFrcmod, LigandLib), skippable=skippable)
        wnf3_complex = Filter(
            wnid="wnf3_complex", artifact_types=(BaseComplexStructureFile, ComplexPeriodicBox), skippable=skippable
        )
        gtc = GenerateTopology(wnid="gtc", solvent=solvent, ions=ions, box_or_oct=box_or_oct, skippable=skippable)
        # Take the .rst7 from `gtc` to create the reference structure for the complex.
        crs_complex = CreateReferenceStructure(wnid="crs_complex")

        wnf3_binder = Filter(
            wnid="wnf3_binder", artifact_types=(BaseBinderStructureFile, BinderPeriodicBox), skippable=skippable
        )
        gtb = GenerateTopology(wnid="gtb", solvent=solvent, ions=ions, box_or_oct=box_or_oct, skippable=skippable)
        # Take the .rst7 from `gtb` to create the reference structure for the complex.
        crs_binder = CreateReferenceStructure(wnid="crs_binder")

        hmr_binder = HMR(wnid="hmr_binder", skippable=skippable)
        hmr_complex = HMR(wnid="hmr_complex", skippable=skippable)

        ffopt_binder: Optional[FFPOPT] = None
        ffopt_complex: Optional[FFPOPT] = None
        if ffopt:
            ffopt_binder = FFPOPT(wnid="ffopt_binder", skippable=skippable)
            ffopt_complex = FFPOPT(wnid="ffopt_complex", skippable=skippable)
        wnf_binder = Filter(wnid="wnf_binder", artifact_types=(BinderLigandRestart,), skippable=skippable)
        wnf_complex = Filter(wnid="wnf_complex", artifact_types=(ComplexProteinLigandRestart,), skippable=skippable)

        # Add nodes to the DAG
        nodes = [
            wnf_binder_parameters,
            wnf1,
            addchainid,
            jtb,
            bafeb,
            wnf2,
            wnf3_complex,
            gtc,
            crs_complex,
            wnf3_binder,
            gtb,
            crs_binder,
            hmr_binder,
            hmr_complex,
            wnf_binder,
            wnf_complex,
        ]
        if ffopt:
            nodes.append(ffopt_binder)
            nodes.append(ffopt_complex)
        self.dag.add_nodes_from(nodes)

        # Start with the root node
        self.dag.add_edge(self.root, wnf_binder_parameters)
        self.dag.add_edge(self.root, wnf1)
        self.dag.add_edge(wnf_binder_parameters, jtb)
        self.dag.add_edge(wnf_binder_parameters, bafeb)
        self.dag.add_edge(wnf_binder_parameters, wnf2)
        self.dag.add_edge(wnf1, addchainid)
        self.dag.add_edge(addchainid, jtb)
        self.dag.add_edge(jtb, bafeb)
        self.dag.add_edge(bafeb, wnf3_complex)
        self.dag.add_edge(bafeb, wnf3_binder)
        self.dag.add_edge(wnf3_complex, gtc)
        self.dag.add_edge(wnf2, gtc)
        self.dag.add_edge(wnf3_binder, gtb)
        self.dag.add_edge(wnf2, gtb)
        self.dag.add_edge(gtc, hmr_complex)
        self.dag.add_edge(gtc, crs_complex)
        self.dag.add_edge(hmr_complex, ffopt_complex)
        self.dag.add_edge(gtb, hmr_binder)
        self.dag.add_edge(gtb, crs_binder)
        self.dag.add_edge(hmr_binder, ffopt_binder)
        self.dag.add_edge(gtb, wnf_binder)
        self.dag.add_edge(gtc, wnf_complex)

        # End with the leaf node
        # `ffopt_complex` (or `hmr_complex`) and `ffopt_binder` (or `hmr_binder`) have the complex and binder topologies, respectively.
        if ffopt:
            self.dag.add_edge(ffopt_complex, self.leaf)
            self.dag.add_edge(ffopt_binder, self.leaf)
        else:
            self.dag.add_edge(hmr_complex, self.leaf)
            self.dag.add_edge(hmr_binder, self.leaf)
        # `wnf_complex` and `wnf_binder` have the complex and binder restarts, respectively.
        self.dag.add_edge(wnf_complex, self.leaf)
        self.dag.add_edge(wnf_binder, self.leaf)
        # Output the reference structures
        self.dag.add_edge(crs_complex, self.leaf)
        self.dag.add_edge(crs_binder, self.leaf)
