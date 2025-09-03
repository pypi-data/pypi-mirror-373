# -*- coding: utf-8 -*-
"""
Control parameters for the Thermomechanical step in a SEAMM flowchart
"""

import logging
import seamm

logger = logging.getLogger(__name__)


class ThermomechanicalParameters(seamm.Parameters):
    """
    The control parameters for Thermomechanical.

    You need to replace the "time" entry in dictionary below these comments with the
    definitions of parameters to control this step. The keys are parameters for the
    current plugin,the values are dictionaries as outlined below.

    Examples
    --------
    ::

        parameters = {
            "time": {
                "default": 100.0,
                "kind": "float",
                "default_units": "ps",
                "enumeration": tuple(),
                "format_string": ".1f",
                "description": "Simulation time:",
                "help_text": ("The time to simulate in the dynamics run.")
            },
        }

    parameters : {str: {str: str}}
        A dictionary containing the parameters for the current step.
        Each key of the dictionary is a dictionary that contains the
        the following keys:

    parameters["default"] :
        The default value of the parameter, used to reset it.

    parameters["kind"] : enum()
        Specifies the kind of a variable. One of  "integer", "float", "string",
        "boolean", or "enum"

        While the "kind" of a variable might be a numeric value, it may still have
        enumerated custom values meaningful to the user. For instance, if the parameter
        is a convergence criterion for an optimizer, custom values like "normal",
        "precise", etc, might be adequate. In addition, any parameter can be set to a
        variable of expression, indicated by having "$" as the first character in the
        field. For example, $OPTIMIZER_CONV.

    parameters["default_units"] : str
        The default units, used for resetting the value.

    parameters["enumeration"] : tuple
        A tuple of enumerated values.

    parameters["format_string"] : str
        A format string for "pretty" output.

    parameters["description"] : str
        A short string used as a prompt in the GUI.

    parameters["help_text"] : str
        A longer string to display as help for the user.

    See Also
    --------
    Thermomechanical, TkThermomechanical, Thermomechanical
    ThermomechanicalParameters, ThermomechanicalStep
    """

    parameters = {
        "state point definition": {
            "default": "as given",
            "kind": "enum",
            "default_units": "",
            "enumeration": ("as given", "lists of Ps and Ts", "list of P, T pairs"),
            "format_string": "",
            "description": "Enter state points as:",
            "help_text": "How the state points will be defined",
        },
        "state points": {
            "default": "(298.15 K, 1 atm)",
            "kind": "string",
            "default_units": "",
            "enumeration": tuple(),
            "format_string": "",
            "description": "Temperatures:",
            "help_text": "The temperatures for the thermomechanical properties.",
        },
        "T": {
            "default": "298.15",
            "kind": "string",
            "default_units": "K",
            "enumeration": tuple(),
            "format_string": "",
            "description": "Temperatures:",
            "help_text": "The temperatures for the thermomechanical properties.",
        },
        "P": {
            "default": "1.0",
            "kind": "string",
            "default_units": "atm",
            "enumeration": tuple(),
            "format_string": "",
            "description": "Pressures:",
            "help_text": "The pressures for the thermomechanical properties.",
        },
        "elastic constants": {
            "default": "no",
            "kind": "boolean",
            "default_units": "",
            "enumeration": ("yes", "no"),
            "format_string": "",
            "description": "Calculate elastic constants:",
            "help_text": "Whether to calculate the elastic constants.",
        },
        "step size": {
            "default": 0.01,
            "kind": "float",
            "default_units": "",
            "enumeration": tuple(),
            "format_string": ".2f",
            "description": "Strain step:",
            "help_text": "The size of the step in strain for elastic constants.",
        },
        "thermochemistry Ts": {
            "default": "1:10,20:100:10,125:275:25,298.15,300:1000:50,1100:3000:100",
            "kind": "string",
            "default_units": "K",
            "enumeration": tuple(),
            "format_string": "",
            "description": "Temperatures for thermochemistry:",
            "help_text": "The temperatures for the thermochemistryproperties.",
        },
        "on success": {
            "default": "keep last subdirectory",
            "kind": "enum",
            "default_units": "",
            "enumeration": (
                "keep last subdirectory",
                "keep all subdirectories",
                "delete all subdirectories",
            ),
            "format_string": "",
            "description": "On success:",
            "help_text": "Which subdirectories to keep.",
        },
        "on error": {
            "default": "keep all subdirectories",
            "kind": "enum",
            "default_units": "",
            "enumeration": (
                "keep last subdirectory",
                "keep all subdirectories",
                "delete all subdirectories",
            ),
            "format_string": "",
            "description": "On error:",
            "help_text": "Which subdirectories to keep if there is an error.",
        },
        "results": {
            "default": {},
            "kind": "dictionary",
            "default_units": None,
            "enumeration": tuple(),
            "format_string": "",
            "description": "results",
            "help_text": "The results to save to variables or in tables.",
        },
    }

    def __init__(self, defaults={}, data=None):
        """
        Initialize the parameters, by default with the parameters defined above

        Parameters
        ----------
        defaults: dict
            A dictionary of parameters to initialize. The parameters
            above are used first and any given will override/add to them.
        data: dict
            A dictionary of keys and a subdictionary with value and units
            for updating the current, default values.

        Returns
        -------
        None
        """

        logger.debug("ThermomechanicalParameters.__init__")

        super().__init__(
            defaults={
                **ThermomechanicalParameters.parameters,
                **defaults,
            },
            data=data,
        )
