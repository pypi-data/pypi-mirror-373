# -*- coding: utf-8 -*-

"""Non-graphical part of the Thermomechanical step in a SEAMM flowchart"""

from datetime import datetime
import json
import logging
from math import exp, log, log10, atan
from pathlib import Path
import pkg_resources
import pprint  # noqa: F401
import shlex
import sys
import textwrap
import traceback

import numpy as np
from tabulate import tabulate

import thermomechanical_step
import molsystem
import seamm
from seamm_util import getParser, parse_list, Q_, units_class  # noqa: F401
import seamm_util.printing as printing
from seamm_util.printing import FormattedText as __

# In addition to the normal logger, two logger-like printing facilities are
# defined: "job" and "printer". "job" send output to the main job.out file for
# the job, and should be used very sparingly, typically to echo what this step
# will do in the initial summary of the job.
#
# "printer" sends output to the file "step.out" in this steps working
# directory, and is used for all normal output from this step.

logger = logging.getLogger(__name__)
job = printing.getPrinter()
printer = printing.getPrinter("Thermomechanical")

# Add this module's properties to the standard properties
path = Path(pkg_resources.resource_filename(__name__, "data/"))
csv_file = path / "properties.csv"
if path.exists():
    molsystem.add_properties_from_file(csv_file)


def round_value(value, digits=3):
    """Round a value to the given number of digits accuracy"""
    decimals = int(log10(abs(value)))
    if decimals < 0:
        decimals = -decimals + digits
    else:
        decimals = digits - 1 - decimals
        if decimals < 0:
            decimals = 0
    return round(value, decimals)


class Thermomechanical(seamm.Node):
    """
    The non-graphical part of a Thermomechanical step in a flowchart.

    Attributes
    ----------
    parser : configargparse.ArgParser
        The parser object.

    options : tuple
        It contains a two item tuple containing the populated namespace and the
        list of remaining argument strings.

    subflowchart : seamm.Flowchart
        A SEAMM Flowchart object that represents a subflowchart, if needed.

    parameters : ThermomechanicalParameters
        The control parameters for Thermomechanical.

    See Also
    --------
    TkThermomechanical,
    Thermomechanical, ThermomechanicalParameters
    """

    def __init__(
        self,
        flowchart=None,
        title="Thermomechanical",
        namespace="org.molssi.seamm",
        extension=None,
        logger=logger,
    ):
        """A step for Thermomechanical in a SEAMM flowchart.

        You may wish to change the title above, which is the string displayed
        in the box representing the step in the flowchart.

        Parameters
        ----------
        flowchart: seamm.Flowchart
            The non-graphical flowchart that contains this step.

        title: str
            The name displayed in the flowchart.
        namespace : str
            The namespace for the plug-ins of the subflowchart
        extension: None
            Not yet implemented
        logger : Logger = logger
            The logger to use and pass to parent classes

        Returns
        -------
        None
        """
        logger.debug(f"Creating Thermomechanical {self}")
        self.subflowchart = seamm.Flowchart(
            parent=self, name="Thermomechanical", namespace=namespace
        )  # yapf: disable

        super().__init__(
            flowchart=flowchart,
            title="Thermomechanical",
            extension=extension,
            module=__name__,
            logger=logger,
        )  # yapf: disable

        self._metadata = thermomechanical_step.metadata
        self.parameters = thermomechanical_step.ThermomechanicalParameters()
        self._data = {}

    @property
    def version(self):
        """The semantic version of this module."""
        return thermomechanical_step.__version__

    @property
    def git_revision(self):
        """The git version of this module."""
        return thermomechanical_step.__git_revision__

    def analyze(self, indent="", **kwargs):
        """Do any analysis of the output from this step.

        Also print important results to the local step.out file using
        "printer".

        Parameters
        ----------
        indent: str
            An extra indentation for the output
        """
        # Get the first real node
        node = self.subflowchart.get_node("1").next()

        # Loop over the subnodes, asking them to do their analysis
        while node is not None:
            for value in node.description:
                printer.important(value)
                printer.important(" ")

            node.analyze()

            node = node.next()

    def _calculate_elastic_constants(self, _P):
        """The driver for calculating elastic constants.

        Parameters
        ----------
        _P : dict(str, any)
            The control parameters for this step

        Returns
        -------
        None
        """
        data = {}  # Results to be stored if chosen by user
        _, configuration = self.get_system_configuration()

        # Save the cell and coordinates so that we can recreate the structure
        cell0 = configuration.cell.parameters
        fractionals0 = configuration.coordinates

        # First run the unstrained system
        results = {}
        results[0] = self._run_subflowchart(name="unstrained")
        configuration.cell.parameters = cell0
        configuration.coordinates = fractionals0

        # Find the units of the stress
        if "Sxx,units" in results[0]:
            units = results[0]["Sxx,units"]
            factor = Q_(1.0, units).m_as("GPa")
        else:
            units = "GPa"
            factor = 1

        # Save the stress
        data["stress"] = [
            results[0][key] * factor
            for key in ("Sxx", "Syy", "Szz", "Syz", "Sxz", "Sxy")
        ]

        # And the strains, + & -
        step = _P["step size"]
        for indx, strain in enumerate(("xx", "yy", "zz", "yz", "xz", "xy")):
            strn = [0.0] * 6
            if indx > 2:
                # Voigt off-diagonals have factor of 2
                strn[indx] = -2 * step
            else:
                strn[indx] = -step
            configuration.strain(strn)
            results[(indx, "-")] = self._run_subflowchart(name=f"e{strain} -{step}")
            configuration.cell.parameters = cell0
            configuration.coordinates = fractionals0

            if indx > 2:
                # Voigt off-diagonals have factor of 2
                strn[indx] = 2 * step
            else:
                strn[indx] = step
            configuration.strain(strn)
            results[(indx, "+")] = self._run_subflowchart(name=f"e{strain} +{step}")
            configuration.cell.parameters = cell0
            configuration.coordinates = fractionals0

        # Create the elastic constant matrix, converting to GPa on the way
        C = []
        for i in range(6):
            plus = results[(i, "+")]
            minus = results[(i, "-")]
            row = []
            for j, strain in enumerate(("Sxx", "Syy", "Szz", "Syz", "Sxz", "Sxy")):
                Cij = factor * (plus[strain] - minus[strain]) / (2 * step)
                row.append(Cij)
            C.append(row)

        # Print the unsymmetrized matrix
        table = {}
        table[""] = ["xx", "yy", "zz", "yz", "xz", "xy"]

        for row, strain in zip(C, ["xx", "yy", "zz", "yz", "xz", "xy"]):
            table[strain] = [*row]

        tmp = tabulate(
            table,
            headers="keys",
            tablefmt="rounded_outline",
            floatfmt=".2f",
        )
        length = len(tmp.splitlines()[0])
        text_lines = []
        header = "Unsymmetrized elastic constant matrix (GPa)"
        text_lines.append(header.center(length))
        text_lines.append(tmp)
        text = textwrap.indent("\n".join(text_lines), self.indent + 8 * " ")
        printer.normal(text)
        printer.normal("")

        # Symmetrize the matrix
        for i in range(6):
            for j in range(i):
                Cij = C[i][j]
                Cji = C[j][i]
                C[j][i] = (Cij + Cji) / 2
                C[i][j] = Cij - Cji

        # Print the symmetrized matrix
        table = {}
        table[""] = ["xx", "yy", "zz", "yz", "xz", "xy"]

        for row, strain in zip(C, ["xx", "yy", "zz", "yz", "xz", "xy"]):
            table[strain] = [*row]

        tmp = tabulate(
            table,
            headers="keys",
            tablefmt="rounded_outline",
            floatfmt=".1f",
        )
        length = len(tmp.splitlines()[0])
        text_lines = []
        header = "Elastic constant matrix (lower) and error (upper) (GPa)"
        text_lines.append(header.center(length))
        text_lines.append(tmp)
        text = textwrap.indent("\n".join(text_lines), self.indent + 8 * " ")
        printer.normal(text)
        printer.normal("")

        # Make full square matrix
        for i in range(6):
            for j in range(i):
                C[i][j] = C[j][i]
        data["Cij"] = C

        # Invert to get compliance
        tmp = np.array(C)
        S = np.linalg.inv(tmp).tolist()
        data["Sij"] = S

        # Print the compliance matrix
        table = {}
        table[""] = ["xx", "yy", "zz", "yz", "xz", "xy"]

        for row, strain in zip(S, ["xx", "yy", "zz", "yz", "xz", "xy"]):
            table[strain] = [1000 * v for v in row]

        tmp = tabulate(
            table,
            headers="keys",
            tablefmt="rounded_outline",
            floatfmt=".1f",
        )
        length = len(tmp.splitlines()[0])
        text_lines = []
        header = "Compliance matrix (1/TPa)"
        text_lines.append(header.center(length))
        text_lines.append(tmp)
        text = textwrap.indent("\n".join(text_lines), self.indent + 8 * " ")
        printer.normal(text)
        printer.normal("")

        # The polycrystalline moduli

        # Voigt
        Kv = ((C[0][0] + C[1][1] + C[2][2]) + 2 * (C[0][1] + C[1][2] + C[0][2])) / 9
        Gv = (
            (C[0][0] + C[1][1] + C[2][2])
            - (C[0][1] + C[1][2] + C[0][2])
            + 3 * (C[3][3] + C[4][4] + C[5][5])
        ) / 15
        Ev = 9 * Kv * Gv / (3 * Kv + Gv)
        mu_v = (3 * Kv - 2 * Gv) / (6 * Kv + 2 * Gv)

        data["Kv"] = Kv
        data["Gv"] = Gv
        data["Ev"] = Ev
        data["mu_v"] = mu_v

        # Reuss
        Kr = 1 / ((S[0][0] + S[1][1] + S[2][2]) + 2 * (S[0][1] + S[1][2] + S[0][2]))
        Gr = 15 / (
            4 * (S[0][0] + S[1][1] + S[2][2])
            - 4 * (S[0][1] + S[1][2] + S[0][2])
            + 3 * (S[3][3] + S[4][4] + S[5][5])
        )
        Er = 9 * Kr * Gr / (3 * Kr + Gr)
        mu_r = (3 * Kr - 2 * Gr) / (6 * Kr + 2 * Gr)

        data["Kr"] = Kr
        data["Gr"] = Gr
        data["Er"] = Er
        data["mu_r"] = mu_r

        # Hill
        Kh = (Kv + Kr) / 2
        Gh = (Gv + Gr) / 2
        Eh = 9 * Kh * Gh / (3 * Kh + Gh)
        mu_h = (3 * Kh - 2 * Gh) / (6 * Kh + 2 * Gh)

        data["Kh"] = Kh
        data["Gh"] = Gh
        data["Eh"] = Eh
        data["mu_h"] = mu_h

        # And print as a table
        table = {
            "Modulus": ["Bulk (K)", "Shear (G)", "Young (E)", "Poisson ratio"],
            "Voigt": [f"{Kv:.1f}", f"{Gv:.1f}", f"{Ev:.1f}", f"{mu_v:.3f}"],
            "Reuss": [f"{Kr:.1f}", f"{Gr:.1f}", f"{Er:.1f}", f"{mu_r:.3f}"],
            "Hill": [f"{Kh:.1f}", f"{Gh:.1f}", f"{Eh:.1f}", f"{mu_h:.3f}"],
        }

        tmp = tabulate(
            table,
            headers="keys",
            tablefmt="rounded_outline",
        )
        length = len(tmp.splitlines()[0])
        text_lines = []
        header = "Polycrystalline Moduli (GPa) and Poisson Ratio"
        text_lines.append(header.center(length))
        text_lines.append(tmp)
        text = textwrap.indent("\n".join(text_lines), self.indent + 8 * " ")
        printer.normal(text)
        printer.normal("")

        # Gruneisen parameter
        gamma = 3 / 2 * ((1 + mu_h) / (2 - 3 * mu_h))

        # Pugh's ratio
        k_pugh = Gh / Kh
        data["k_pugh"] = k_pugh

        # Cauchy pressure
        Pcauchy = C[1][2] - C[4][4]
        data["Pcauchy"] = Pcauchy

        # Vickers hardness
        Hv_chen = 2 * (k_pugh**2 / Gh) ** 0.585 - 3
        Hv_tian = 0.92 * k_pugh**1.137 * Gh**0.708
        data["Hv_chen"] = Hv_chen
        data["Hv_tian"] = Hv_tian

        # Sound velocity and Debye temperature. Let pint take care of units
        Kh = Q_(Kh, "GPa")
        Gh = Q_(Gh, "GPa")
        Eh = Q_(Eh, "GPa")
        rho = Q_(configuration.density, "g/ml")
        vl = ((3 * Kh + 4 * Gh) / (3 * rho)) ** 0.5
        vt = (Gh / rho) ** 0.5
        vl.ito("m/s")
        vt.ito("m/s")
        vm = (((2 / vt**3) + 1 / vl**3) / 3) ** (-1 / 3)

        h = Q_(1, "planck_constant")
        kb = Q_(1, "boltzmann_constant")
        pi = Q_(1, "pi")
        Na = Q_(1, "avogadro_constant")
        R = (kb * Na).m_as("J/mol/K")
        n_atoms = configuration.n_atoms
        mass = Q_(configuration.mass, "g/mol")

        Td = h / kb * (3 * n_atoms / (4 * pi) * Na * rho / mass) ** (1 / 3) * vm
        Td.ito("K")

        # N is the number of atoms in the empirical formula unit
        formula, empirical_formula, Z = configuration.formula
        N = n_atoms / Z
        Ezp = 9 / 8 * N * R * Td
        Ezp.ito("kJ/mol")

        data["vl"] = vl.magnitude
        data["vt"] = vt.magnitude
        data["vm"] = vm.magnitude
        data["Td"] = Td.magnitude
        data["Ezp"] = Ezp.magnitude
        data["Gruneisen parameter"] = gamma

        # And print as a table
        table = {
            "Property": [
                "Pugh's ductility criterion (k) <0.57 ductile",
                'Cauchy pressure (C") >0 ductile',
                "Vickers hardness (Hv) [Chen]",
                "Vickers hardness (Hv) [Tian]",
                "Transverse sound velocity (vt)",
                "Longitudinal sound velocity (vl)",
                "Average sound velocity (vm)",
                "Debye temperature (Td)",
                "Zero-point energy",
                "Gruneisen parameter",
            ],
            "Value": [
                f"{k_pugh:.2f}",
                f"{Pcauchy:.2f}",
                f"{Hv_chen:.1f}",
                f"{Hv_tian:.1f}",
                f"{vt.magnitude:.0f}",
                f"{vl.magnitude:.0f}",
                f"{vm.magnitude:.0f}",
                f"{Td.magnitude:.1f}",
                f"{Ezp.magnitude:.1f}",
                f"{gamma:.2f}",
            ],
            "Units": ["", "", "", "", "m/s", "m/s", "m/s", "K", "kJ/mol", ""],
        }

        tmp = tabulate(
            table,
            headers="keys",
            tablefmt="rounded_outline",
        )
        length = len(tmp.splitlines()[0])
        text_lines = []
        header = "Other Properties"
        text_lines.append(header.center(length))
        text_lines.append(tmp)
        text = textwrap.indent("\n".join(text_lines), self.indent + 8 * " ")
        printer.normal(text)
        printer.normal("")

        text = "The zero-point energy above and thermodynamic functions below "
        text += f"correspond to the empirical formula {empirical_formula}."
        if Z > 1:
            text += f" There are {Z} units of that formula in the cell."
        printer.normal(__(text, indent=self.indent + 4 * " "))
        printer.normal("")

        # Evaluate the termochemistry using the Debye model
        Ts = parse_list(_P["thermochemistry Ts"])

        results = self.debye_model(Td.magnitude, Ts, N=N)

        # And get the approximate linear coefficient of thermal expansion
        V = Q_(configuration.volume / Z, "Å^3")  # Volume per formula unit
        a_factor = Q_(1, "J/mol/K") * gamma / (Kh * V * Na) / 3  # 3 for volume > linear
        a_factor = a_factor.m_as("1/K") * 1.0e6
        alpha = [round_value(v * a_factor) for v in results["Cv"]]

        table = {
            "T": Ts,
            "Cv (J/mol*K)": results["Cv"],
            "U - U₀ (kJ/mol)": results["U"],
            "S (J/mol/K)": results["S"],
            "A - U₀ (kJ/mol)": results["A"],
            "alpha (10^-6/K)": alpha,
        }
        tmp = tabulate(
            table,
            headers="keys",
            tablefmt="rounded_outline",
            disable_numparse=False,
        )
        length = len(tmp.splitlines()[0])
        text_lines = []
        header = "Thermodynamic functions"
        text_lines.append(header.center(length))
        text_lines.append(tmp)

        # And save the data as dictionaries...
        data["Cv"] = {T: v for T, v in zip(Ts, results["Cv"])}
        data["U - U0"] = {T: v for T, v in zip(Ts, results["U"])}
        data["S"] = {T: v for T, v in zip(Ts, S)}
        data["A - U0"] = {T: v for T, v in zip(Ts, results["A"])}
        data["alpha"] = {T: v for T, v in zip(Ts, alpha)}

        text = textwrap.indent("\n".join(text_lines), self.indent + 8 * " ")
        printer.normal(text)
        printer.normal("")

        # Put any requested results into variables or tables
        self.store_results(configuration=configuration, data=data)

        # And graph the thermodynamic functions
        figure = self.create_figure(
            module_path=(self.__module__.split(".")[0], "seamm"),
            template="line.graph_template",
            fontsize=self.options["graph_fontsize"],
            title=f"Thermodynamic functions for {empirical_formula}",
        )
        plot = figure.add_plot("thermodynamics")

        x_axis = plot.add_axis("x", label="T (K)")
        y_axis = plot.add_axis(
            "y",
            anchor=x_axis,
            label="Cv, S (J/mol/K)",
            rangemode="tozero",
        )
        x_axis.anchor = y_axis
        plot.add_trace(
            x_axis=x_axis,
            y_axis=y_axis,
            name="Cv",
            x=Ts,
            xlabel="T",
            xunits="K",
            y=results["Cv"],
            ylabel="Cv",
            yunits="J/mol/K",
            color="#4dbd74",
            width=2,
        )
        plot.add_trace(
            x_axis=x_axis,
            y_axis=y_axis,
            name="S",
            x=Ts,
            xlabel="T",
            xunits="K",
            y=results["S"],
            ylabel="S",
            yunits="J/mol/K",
            color="red",
            width=2,
        )

        y2_axis = plot.add_axis(
            "y",
            anchor=x_axis,
            gridcolor="pink",
            label="U - U₀, -(A - U₀) (kJ/mol)",
            overlaying="y",
            rangemode="tozero",
            side="right",
            tickmode="sync",
        )
        plot.add_trace(
            x_axis=x_axis,
            y_axis=y2_axis,
            name="U - U₀",
            x=Ts,
            xlabel="T",
            xunits="K",
            y=results["U"],
            ylabel="U - U₀",
            yunits="kJ/mol",
            color="black",
            width=2,
        )
        plot.add_trace(
            x_axis=x_axis,
            y_axis=y2_axis,
            name="-(A - U₀)",
            x=Ts,
            xlabel="T",
            xunits="K",
            y=[-v for v in results["A"]],
            ylabel="-(A - U₀)",
            yunits="kJ/mol",
            color="blue",
            width=2,
        )

        figure.grid_plots("thermodynamics")

        path = self.wd / "ThermodynamicFunctions.graph"
        figure.write_file(path)

        # Other requested formats
        if "graph_formats" in self.options:
            formats = self.options["graph_formats"]
            # If from seamm.ini, is a single string so parse.
            if isinstance(formats, str):
                formats = shlex.split(formats)
            for _format in formats:
                figure.write_file(
                    path.with_suffix("." + _format),
                    width=int(self.options["graph_width"]),
                    height=int(self.options["graph_height"]),
                )

        # And the linear coefficient of thermal expansion
        figure = self.create_figure(
            module_path=(self.__module__.split(".")[0], "seamm"),
            template="line.graph_template",
            fontsize=self.options["graph_fontsize"],
            title=f"Linear thermal expansion for {empirical_formula}",
        )
        plot = figure.add_plot("alpha")

        x_axis = plot.add_axis("x", label="T (K)")
        y_axis = plot.add_axis(
            "y",
            anchor=x_axis,
            label="1/K (x 10⁻⁶)",
            rangemode="tozero",
        )
        x_axis.anchor = y_axis
        plot.add_trace(
            x_axis=x_axis,
            y_axis=y_axis,
            name="Cv",
            x=Ts,
            xlabel="T",
            xunits="K",
            y=alpha,
            ylabel="𝛼",
            yunits="1/K (x 10⁻⁶)",
            hovertemplate="%{x} K, %{y} x 10⁻⁶/K}",
            color="black",
            width=2,
        )

        figure.grid_plots("alpha")

        path = self.wd / "ThermalExpansion.graph"
        figure.write_file(path)

        # Other requested formats
        if "graph_formats" in self.options:
            formats = self.options["graph_formats"]
            # If from seamm.ini, is a single string so parse.
            if isinstance(formats, str):
                formats = shlex.split(formats)
            for _format in formats:
                figure.write_file(
                    path.with_suffix("." + _format),
                    width=int(self.options["graph_width"]),
                    height=int(self.options["graph_height"]),
                )

    def create_parser(self):
        """Setup the command-line / config file parser"""
        parser_name = "thermomechanical-step"
        parser = getParser()

        # Remember if the parser exists ... this type of step may have been
        # found before
        parser_exists = parser.exists(parser_name)

        # Create the standard options, e.g. log-level
        super().create_parser(name=parser_name)

        if not parser_exists:
            # Any options for thermomechanical step itself
            parser.add_argument(
                parser_name,
                "--graph-formats",
                default=tuple(),
                choices=("html", "png", "jpeg", "webp", "svg", "pdf"),
                nargs="+",
                help="extra formats to write for graphs",
            )
            parser.add_argument(
                parser_name,
                "--graph-fontsize",
                default=15,
                help="Font size in graphs, defaults to 15 pixels",
            )
            parser.add_argument(
                parser_name,
                "--graph-width",
                default=1024,
                help="Width of graphs in formats that support it, defaults to 1024",
            )
            parser.add_argument(
                parser_name,
                "--graph-height",
                default=1024,
                help="Height of graphs in formats that support it, defaults to 1024",
            )

        # Now need to walk through the steps in the subflowchart...
        self.subflowchart.reset_visited()
        node = self.subflowchart.get_node("1").next()
        while node is not None:
            node = node.create_parser()

        return self.next()

    def description_text(self, P=None):
        """Create the text description of what this step will do.
        The dictionary of control values is passed in as P so that
        the code can test values, etc.

        Parameters
        ----------
        P: dict
            An optional dictionary of the current values of the control
            parameters.
        Returns
        -------
        str
            A description of the current step.
        """
        # Make sure the subflowchart has the data from the parent flowchart
        self.subflowchart.root_directory = self.flowchart.root_directory
        self.subflowchart.executor = self.flowchart.executor
        self.subflowchart.in_jobserver = self.subflowchart.in_jobserver

        if P is None:
            P = self.parameters.values_to_dict()

        # Describe what we are going to do
        result = self.header + "\n\n"
        text = ""

        elastic = P["elastic constants"]
        step = P["step size"]
        if isinstance(elastic, bool) and elastic or elastic == "yes":
            text += (
                "The elastic constants will be calculated using a strain step of "
                f"{step}. "
            )
        elif self.is_expr(elastic):
            text += (
                f"The expression {elastic} will determine whether to calculate the "
                f"elastic constants. If so, a strain step of {step} will be used. "
            )

        spdef = P["state point definition"]
        if self.is_expr(spdef):
            text += (
                "The expression {spdef} will determine what state points will be used. "
            )
        elif spdef == "as given":
            text += (
                "The current structure will be used as is, with the temperature set "
                "in the subflowchart if needed."
            )
        elif spdef == "lists of Ps and Ts":
            text += (
                "The state points will be generated by using each pressure {P} for "
                "each temperature {T}."
            )
        else:
            text += "The state points given by {state points} will be used."

        result += str(__(text, indent=4 * " ", **P))
        result += "\n\n"

        # Get the first real node
        node = self.subflowchart.get_node("1").next()

        text = ""
        while node is not None:
            try:
                text += __(node.description_text(), indent=8 * " ").__str__()
            except Exception as e:
                print(f"Error describing thermomechanical flowchart: {e} in {node}")
                logger.critical(
                    f"Error describing thermomechanical flowchart: {e} in {node}"
                )
                raise
            except Exception:
                print(
                    "Unexpected error describing thermomechanical flowchart: "
                    f"{sys.exc_info()[0]} in {str(node)}"
                )
                logger.critical(
                    "Unexpected error describing thermomechanical flowchart: "
                    f"{sys.exc_info()[0]} in {str(node)}"
                )
                raise
            text += "\n"
            node = node.next()

        result += text

        return result

    def run(self):
        """Run the Thermomechanical step.

        Parameters
        ----------
        None

        Returns
        -------
        seamm.Node
            The next node object in the flowchart.
        """
        next_node = super().run(printer)

        # Get the values of the parameters, dereferencing any variables
        _P = self.parameters.current_values_to_dict(
            context=seamm.flowchart_variables._data
        )

        # Fix the formatting of units for printing...
        _PP = dict(_P)
        for key in _PP:
            if isinstance(_PP[key], units_class):
                _PP[key] = "{:~P}".format(_PP[key])

        # Print what we are doing
        printer.important(__(self.description_text(_PP), indent=self.indent))

        if _P["elastic constants"]:
            self._calculate_elastic_constants(_P)

        return next_node

    def _run_subflowchart(self, name=None):
        """Run the subflowchart for training.

        Parameters
        ----------
        name : str, default = None
            The name of the run, used to create the subdirectory and name in the output.
            The default of None indicates use the current directory as is.

        Returns
        -------
        results : {str: any}
            A dictionary of the results from the subflowchart
        """
        super().run(printer)

        # Make sure the subflowchart has the data from the parent flowchart
        self.subflowchart.root_directory = self.flowchart.root_directory
        self.subflowchart.executor = self.flowchart.executor
        self.subflowchart.in_jobserver = self.subflowchart.in_jobserver

        job_handler = None
        out_handler = None
        if name is None:
            iter_dir = self.wd
            iter_dir.mkdir(parents=True, exist_ok=True)

            # Ensure the nodes have the correct id
            self.set_subids(self._id)
        else:
            iter_dir = self.wd / name
            iter_dir.mkdir(parents=True, exist_ok=True)

            # Find the handler for job.out and set the level up
            for handler in job.handlers:
                if (
                    isinstance(handler, logging.FileHandler)
                    and "job.out" in handler.baseFilename
                ):
                    job_handler = handler
                    job_level = job_handler.level
                    job_handler.setLevel(printing.JOB)
                elif isinstance(handler, logging.StreamHandler):
                    out_handler = handler
                    out_level = out_handler.level
                    out_handler.setLevel(printing.JOB)

            # Setup the output for this pass
            path = iter_dir / "Step.out"
            path.unlink(missing_ok=True)
            file_handler = logging.FileHandler(path)
            file_handler.setLevel(printing.NORMAL)
            formatter = logging.Formatter(fmt="{message:s}", style="{")
            file_handler.setFormatter(formatter)
            job.addHandler(file_handler)

            # Ensure the nodes have the correct id
            self.set_subids((*self._id, name))

        # Get the first real node in the subflowchart
        first_node = self.subflowchart.get_node("1").next()

        # Set up the options for the subflowchart
        node = first_node
        self.subflowchart.reset_visited()
        while node is not None:
            node.all_options = self.all_options
            node = node.next()

        # Run through the steps in the subflowchart
        node = first_node
        try:
            while node is not None:
                try:
                    node = node.run()
                except DeprecationWarning as e:
                    printer.normal("\nDeprecation warning: " + str(e))
                    traceback.print_exc(file=sys.stderr)
                    traceback.print_exc(file=sys.stdout)
        except Exception as e:
            printer.job(f"Caught exception in subflowchart: {str(e)}")
            with open(self.wd / "stderr.out", "a") as fd:
                traceback.print_exc(file=fd)
            raise
        finally:
            if job_handler is not None:
                job_handler.setLevel(job_level)
            if out_handler is not None:
                out_handler.setLevel(out_level)

            # Remove any redirection of printing.
            if file_handler is not None:
                file_handler.close()
                job.removeHandler(file_handler)
                file_handler = None

        # Get the results
        paths = sorted(iter_dir.glob("**/Results.json"))
        if len(paths) == 0:
            if name is None:
                raise RuntimeError(
                    "There are no properties stored in properties.json "
                    f"for this step, running in {iter_dir}."
                )
            else:
                raise RuntimeError(
                    "There are no properties stored in properties.json "
                    f"for step {name} running in {iter_dir}."
                )
        data = {}
        for path in paths:
            with path.open() as fd:
                tmp = json.load(fd)
            time = datetime.fromisoformat(tmp["iso time"])
            data[time] = tmp
        times = sorted(data.keys())
        results = data[times[0]]

        # Add other citations here or in the appropriate place in the code.
        # Add the bibtex to data/references.bib, and add a self.reference.cite
        # similar to the above to actually add the citation to the references.

        return results

    def set_id(self, node_id=()):
        """Sequentially number the subnodes"""
        self.logger.debug("Setting ids for subflowchart {}".format(self))
        if self.visited:
            return None
        else:
            self.visited = True
            self._id = node_id
            self.set_subids(self._id)
            return self.next()

    def set_subids(self, node_id=()):
        """Set the ids of the nodes in the subflowchart"""
        self.subflowchart.reset_visited()
        node = self.subflowchart.get_node("1").next()
        n = 1
        while node is not None:
            node = node.set_id((*node_id, str(n)))
            n += 1

    def debye_model(self, Td, Ts, N=1):
        """Compute the thermodynamic functions from the Debye model"""
        kb = Q_(1, "boltzmann_constant")
        Na = Q_(1, "avogadro_constant")
        R = (kb * Na).m_as("J/mol/K")
        pi = Q_(1, "pi").to_base_units().magnitude

        Tmin = min(Ts)
        Tmax = max(Ts)

        # for T in Ts[::-1]:
        #     print(f"{T:9.2f} {Td / T:9.4f}")

        # Bootstrap the integral in one degree increments from Tmax + 2 to Tmin - 1 or 0
        U_sum = 0
        Cv_sum = 0
        U1 = {}
        Cv1 = {}
        n_steps = 100  # Number of points in each integral over 1 degree

        x = 0
        xmin = 0
        for T in range(Tmax + 2, Tmin - 1 if Tmin - 1 >= 0 else 0, -1):
            xmax = Td / T
            if x == 0:
                # First chunk from 0 to xmax needs a finer grid because it is long
                step = (xmax - xmin) / n_steps / 10000
            else:
                step = (xmax - xmin) / n_steps
            while x <= xmax:
                if x == 0:
                    U_sum = 0
                    Cv_sum = 0
                else:
                    xp = x + step / 2
                    xm = x - step / 2
                    try:
                        U_sum += (
                            (xm**3 / (exp(xm) - 1) + xp**3 / (exp(xp) - 1)) / 2 * step
                        )
                    except OverflowError:
                        print(f"U_int overflowed: {T=} {x=}")
                        U_sum = pi**4 / 15

                    try:
                        Cv_sum += (
                            (
                                xm**4 * exp(xm) / (exp(xm) - 1) / (exp(xm) - 1)
                                + xm**4 * exp(xp) / (exp(xp) - 1) / (exp(xp) - 1)
                            )
                            / 2
                            * step
                        )
                    except OverflowError:
                        print(f"Cv_int overflowed: {T=} {x=}")
                        Cv_sum = 4 * pi**4 / 15
                x += step
            xmin = xmax
            prefactor = 9 * N * R * (T / Td) ** 3
            U1[T] = prefactor * T * U_sum / 1000  # kJ/mol, not J/mol
            Cv1[T] = prefactor * Cv_sum

        # Entropy = integral Cv/T 0..T
        S1 = {}
        S_sum = Cv1[T + 1] / (T + 1) / 2
        S1[1] = S_sum
        for T in range(2, Tmax + 2):
            S_sum += (Cv1[T - 1] / (T - 1) + Cv1[T + 1] / (T + 1)) / 2
            S1[T] = S_sum

        # Now find the desired values
        U = []
        Cv = []
        S = []
        Ehelmholtz = []
        for T in Ts:
            Tm = int(T)
            Tp = Tm + 1

            value = U1[Tm] + (U1[Tp] - U1[Tm]) * (T - Tm)
            decimals = int(log10(value))
            if decimals < 0:
                decimals = -decimals + 3
            else:
                decimals = 2 - decimals
                if decimals < 0:
                    decimals = 0
            U.append(round(value, decimals))

            value = Cv1[Tm] + (Cv1[Tp] - Cv1[Tm]) * (T - Tm)
            decimals = int(log10(value))
            if decimals < 0:
                decimals = -decimals + 3
            else:
                decimals = 2 - decimals
                if decimals < 0:
                    decimals = 0
            Cv.append(round(value, decimals))

            value = S1[Tm] + (S1[Tp] - S1[Tm]) * (T - Tm)
            decimals = int(log10(value))
            if decimals < 0:
                decimals = -decimals + 3
            else:
                decimals = 2 - decimals
                if decimals < 0:
                    decimals = 0
            S.append(round(value, decimals))

            value = U[-1] - T * S[-1] / 1000  # kJ/mol, not J/mol
            decimals = int(log10(abs(value)))
            if decimals < 0:
                decimals = -decimals + 3
            else:
                decimals = 2 - decimals
                if decimals < 0:
                    decimals = 0
            Ehelmholtz.append(round(value, decimals))

        # The fit equation
        #
        # William W. Anderson; An analytic expression approximating the Debye heat
        # capacity function. AIP Advances 1 July 2019; 9 (7): 075108.
        # https://doi.org/10.1063/1.5110279
        #
        A = [0.61833, 0.89246]
        B = [0.18112, -0.18189, 4.4259e-3]
        C = [0.14816, 0.0978, 0.117461]
        ni = [2, 2, 3]

        Cv_fit = []
        U_fit = []
        S_fit = []
        A_fit = []
        for T in Ts:
            x = T / Td

            eAx = [exp(A[0] / x), exp(A[1] / x)]
            Cx2 = [C[0] ** 2 + x**2, C[1] ** 2 + x**2, C[2] ** 2 + x**2]

            # Cv
            tmp1 = 0
            for i in range(2):
                tmp1 += (A[i] / x) ** 2 * eAx[i] / (eAx[i] - 1) / (eAx[i] - 1)
            tmp1 /= 2

            tmp2 = 0
            for i in range(3):
                tmp2 += B[i] / Cx2[i] ** ni[i]
            tmp2 *= x**3

            value = 3 * N * R * (tmp1 + tmp2)
            Cv_fit.append(round(value, decimals))

            # U
            tmp = 0
            for i in range(2):
                tmp += A[i] / (eAx[i] - 1) + B[i] * (
                    log(1 + x**2 / C[i] ** 2) - x**2 / Cx2[i]
                )
            tmp /= 2 * x
            tmp += B[2] / (4 * C[2] ** 2) * x**3 / Cx2[2] ** 2

            U_fit.append(3 * N * R * T * tmp / 1000)  # kJ/mol, not J/mol

            # S
            tmp = 0
            for i in range(2):
                tmp += (
                    A[i] / x * eAx[i] / (eAx[i] - 1)
                    - log(eAx[i] - 1)
                    + B[i] * (atan(x / C[i]) / C[i] - x / (C[i] ** 2 + x**2))
                ) / 2
            tmp += (
                B[2]
                / (8 * C[2] ** 2)
                * (
                    (x**3 - C[2] ** 2 * x) / (C[2] ** 2 + x**2) ** 2
                    + atan(x / C[2]) / C[2]
                )
            )

            value = 3 * N * R * tmp
            S_fit.append(round_value(value))

            value = U_fit[-1] - T * S_fit[-1] / 1000  # kJ/mol, not J/mol
            A_fit.append(round_value(value))

        return {
            "Cv": Cv,
            "U": U,
            "S": S,
            "A": Ehelmholtz,
            "Cv fit": Cv_fit,
            "U fit": U_fit,
            "S fit": S_fit,
            "A fit": A_fit,
        }
