# -*- coding: utf-8 -*-

"""This file contains metadata describing the results from Thermomechanical step"""

metadata = {}

"""Description of the computational models for Thermomechanical.

Hamiltonians, approximations, and basis set or parameterizations,
only if appropriate for this code. For example::

    metadata["computational models"] = {
        "Hartree-Fock": {
            "models": {
                "PM7": {
                    "parameterizations": {
                        "PM7": {
                            "elements": "1-60,62-83",
                            "periodic": True,
                            "reactions": True,
                            "optimization": True,
                            "code": "mopac",
                        },
                        "PM7-TS": {
                            "elements": "1-60,62-83",
                            "periodic": True,
                            "reactions": True,
                            "optimization": False,
                            "code": "mopac",
                        },
                    },
                },
            },
        },
    }
"""
# metadata["computational models"] = {
# }

"""Description of the Thermomechanical keywords.

(Only needed if this code uses keywords)

Fields
------
description : str
    A human readable description of the keyword.
takes values : int (optional)
    Number of values the keyword takes. If missing the keyword takes no values.
default : str (optional)
    The default value(s) if the keyword takes values.
format : str (optional)
    How the keyword is formatted in the MOPAC input.

For example::
    metadata["keywords"] = {
        "0SCF": {
            "description": "Read in data, then stop",
        },
        "ALT_A": {
            "description": "In PDB files with alternative atoms, select atoms A",
            "takes values": 1,
            "default": "A",
            "format": "{}={}",
        },
    }
"""
# metadata["keywords"] = {
# }

"""Properties that Thermomechanical produces.
`metadata["results"]` describes the results that this step can produce. It is a
dictionary where the keys are the internal names of the results within this step, and
the values are a dictionary describing the result. For example::

    metadata["results"] = {
        "total_energy": {
            "calculation": [
                "energy",
                "optimization",
            ],
            "description": "The total energy",
            "dimensionality": "scalar",
            "methods": [
                "ccsd",
                "ccsd(t)",
                "dft",
                "hf",
            ],
            "property": "total energy#Psi4#{model}",
            "type": "float",
            "units": "E_h",
        },
    }

Fields
______

calculation : [str]
    Optional metadata describing what subtype of the step produces this result.
    The subtypes are completely arbitrary, but often they are types of calculations
    which is why this is name `calculation`. To use this, the step or a substep
    define `self._calculation` as a value. That value is used to select only the
    results with that value in this field.

description : str
    A human-readable description of the result.

dimensionality : str
    The dimensions of the data. The value can be "scalar" or an array definition
    of the form "[dim1, dim2,...]". Symmetric tringular matrices are denoted
    "triangular[n,n]". The dimensions can be integers, other scalar
    results, or standard parameters such as `n_atoms`. For example, '[3]',
    [3, n_atoms], or "triangular[n_aos, n_aos]".

methods : str
    Optional metadata like the `calculation` data. `methods` provides a second
    level of filtering, often used for the Hamiltionian for *ab initio* calculations
    where some properties may or may not be calculated depending on the type of
    theory.

property : str
    An optional definition of the property for storing this result. Must be one of
    the standard properties defined either in SEAMM or in this steps property
    metadata in `data/properties.csv`.

type : str
    The type of the data: string, integer, or float.

units : str
    Optional units for the result. If present, the value should be in these units.
"""
metadata["results"] = {
    "P": {
        "description": "Pressure",
        "dimensionality": "[nPs]",
        "property": "P#Thermomechanical#{model}",
        "type": "float",
        "units": "atm",
        "format": ".2f",
    },
    "T": {
        "description": "Temperature",
        "dimensionality": "[nTs]",
        "property": "T#Thermomechanical#{model}",
        "type": "float",
        "units": "K",
        "format": ".2f",
    },
    "alpha(V)": {
        "description": "volumetric coefficient of thermal expansion",
        "dimensionality": "scalar",
        "type": "float",
        "units": "1/K",
        "format": ".2g",
    },
    "alpha(a)": {
        "description": "linear coefficient of thermal expansion in cell a",
        "dimensionality": "scalar",
        "type": "float",
        "units": "1/K",
        "format": ".2g",
    },
    "alpha(b)": {
        "description": "linear coefficient of thermal expansion in cell b",
        "dimensionality": "scalar",
        "type": "float",
        "units": "1/K",
        "format": ".2g",
    },
    "alpha(c)": {
        "description": "linear coefficient of thermal expansion in cell c",
        "dimensionality": "scalar",
        "type": "float",
        "units": "1/K",
        "format": ".2g",
    },
    "stress": {
        "description": "stress",
        "dimensionality": "[6]",
        "type": "float",
        "units": "GPa",
    },
    "Cij": {
        "description": "elastic constants",
        "dimensionality": "[6][6]",
        "type": "float",
        "units": "GPa",
    },
    "Sij": {
        "description": "compliance matrix",
        "dimensionality": "[6][6]",
        "type": "float",
        "units": "1/GPa",
    },
    "Kv": {
        "description": "Voigt bulk modulus",
        "dimensionality": "scalar",
        "type": "float",
        "units": "GPa",
    },
    "Gv": {
        "description": "Voigt shear modulus",
        "dimensionality": "scalar",
        "type": "float",
        "units": "GPa",
    },
    "Ev": {
        "description": "Voigt Young modulus",
        "dimensionality": "scalar",
        "type": "float",
        "units": "GPa",
    },
    "mu_v": {
        "description": "Voigt Poisson ratio",
        "dimensionality": "scalar",
        "type": "float",
        "units": "GPa",
    },
    "Kr": {
        "description": "Reuss bulk modulus",
        "dimensionality": "scalar",
        "type": "float",
        "units": "GPa",
    },
    "Gr": {
        "description": "Reuss shear modulus",
        "dimensionality": "scalar",
        "type": "float",
        "units": "GPa",
    },
    "Er": {
        "description": "Reuss Young modulus",
        "dimensionality": "scalar",
        "type": "float",
        "units": "GPa",
    },
    "mu_r": {
        "description": "Reuss Poisson ratio",
        "dimensionality": "scalar",
        "type": "float",
        "units": "GPa",
    },
    "Kh": {
        "description": "Hill bulk modulus",
        "dimensionality": "scalar",
        "property": "bulk modulus#Thermomechanical#{model}",
        "type": "float",
        "units": "GPa",
    },
    "Gh": {
        "description": "Hill shear modulus",
        "dimensionality": "scalar",
        "property": "shear modulus#Thermomechanical#{model}",
        "type": "float",
        "units": "GPa",
    },
    "Eh": {
        "description": "Hill Young modulus",
        "dimensionality": "scalar",
        "property": "Young modulus#Thermomechanical#{model}",
        "type": "float",
        "units": "GPa",
    },
    "mu_h": {
        "description": "Hill Poisson ratio",
        "dimensionality": "scalar",
        "property": "Poisson ratio#Thermomechanical#{model}",
        "type": "float",
        "units": "GPa",
    },
    "vt": {
        "description": "transverse sound velocity",
        "dimensionality": "scalar",
        "property": "transverse sound velocity#Thermomechanical#{model}",
        "type": "float",
        "units": "m/s",
    },
    "vl": {
        "description": "longitudinal sound velocity",
        "dimensionality": "scalar",
        "property": "longitudinal sound velocity#Thermomechanical#{model}",
        "type": "float",
        "units": "m/s",
    },
    "vm": {
        "description": "mean sound velocity",
        "dimensionality": "scalar",
        "property": "mean sound velocity#Thermomechanical#{model}",
        "type": "float",
        "units": "m/s",
    },
    "Td": {
        "description": "Debye temperature",
        "dimensionality": "scalar",
        "property": "Debye temperature#Thermomechanical#{model}",
        "type": "float",
        "units": "K",
    },
    "k_pugh": {
        "description": "Pugh's ductility criterion",
        "dimensionality": "scalar",
        "property": "Pugh's ductility criterion#Thermomechanical#{model}",
        "type": "float",
        "units": "",
    },
    "Pcauchy": {
        "description": "Cauchy pressure",
        "dimensionality": "scalar",
        "property": "Cauchy pressure#Thermomechanical#{model}",
        "type": "float",
        "units": "GPa",
    },
    "Hv_chen": {
        "description": "Vickers hardness [Chen]",
        "dimensionality": "scalar",
        "property": "Vickers hardness [Chen]#Thermomechanical#{model}",
        "type": "float",
        "units": "",
    },
    "Hv_tian": {
        "description": "Vickers hardness [Tian]",
        "dimensionality": "scalar",
        "property": "Vickers hardness [Tian]#Thermomechanical#{model}",
        "type": "float",
        "units": "",
    },
    "Gruneisen parameter": {
        "description": "Gruneisen parameter",
        "dimensionality": "scalar",
        "property": "Gruneisen parameter#Thermomechanical#{model}",
        "type": "float",
        "units": "",
    },
    "Cv": {
        "description": "Constant volume heat capacity",
        "dimensionality": "nTs",
        "property": "Cv#Thermomechanical#{model}",
        "type": "json",
        "units": "J/mol/K",
    },
    "U - U0": {
        "description": "Internal energy",
        "dimensionality": "nTs",
        "property": "U - U0#Thermomechanical#{model}",
        "type": "json",
        "units": "kJ/mol",
    },
    "S": {
        "description": "Entropy",
        "dimensionality": "nTs",
        "property": "S#Thermomechanical#{model}",
        "type": "json",
        "units": "J/mol/K",
    },
    "A - U0": {
        "description": "Helmholtz free energy",
        "dimensionality": "nTs",
        "property": "A#Thermomechanical#{model}",
        "type": "json",
        "units": "kJ/mol",
    },
    "alpha": {
        "description": "Linear coefficient of thermal expansion",
        "dimensionality": "nTs",
        "property": "alpha#Thermomechanical#{model}",
        "type": "json",
        "units": "1/K",
    },
}
