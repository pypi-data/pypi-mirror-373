"""
Conversion - ``ensemblify.conversion``
======================================

:Author(s): Nuno P. Fernandes
:Year: 2024
:Copyright: GNU Public License v3

.. versionadded:: 1.0.0

This module contains functions for converting an ensemble of protein conformations from a set of
.pdb files into a single compressed .xtc trajectory file and for calculating a theoretical SAXS
curve from a .xtc trajectory file.

Example applications
--------------------

Convert an ensemble to trajectory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``ensemblify.conversion.ensemble2traj`` function can be used to create a .xtc trajectory file
from an ensemble of .pdb files.

For example, we can create a trajectory from the set of .pdb structures of Histatin5 (Hst5), an
intrinsically disordered peptide with 24 aminoacid residues.

Assuming that the path to the directory where Hst5 .pdb structures are stored and the path to
the directory where the created .xtc trajectory file will be stored are assigned to variables
named, respectively, HST5_ENSEMBLE_DIR and HST5_TRAJECTORY_DIR, you should run:

>>> import ensemblify.conversion as ec
>>> ec.ensemble2traj(HST5_ENSEMBLE_DIR, HST5_TRAJECTORY_DIR, 'Hst5')

Calculate a theoretical SAXS curve from a trajectory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``ensemblify.conversion.traj2saxs`` function can be used to back-calculate an average SAXS
curve from a .xtc trajectory file.

For example, we can calculate a SAXS curve from a .xtc trajectory file of Histatin5 (Hst5), an
intrinsically disordered peptide with 24 aminoacid residues.

Assuming the path to the required trajectory, topology and experimental data files are assigned
to the variables HST5_TRAJ_PATH, HST5_TOP_PATH and HST5_EXP_SAXS_DATA, respectively, and your
desired trajectory ID is 'Hst5', you should run:

>>> import ensemblify.conversion as ec
>>> ec.traj2saxs(HST5_TRAJ_PATH, HST5_TOP_PATH, 'Hst5', HST5_EXP_SAXS_DATA)

Available Functions
-------------------

``calc_chi2_fit``
    Calculate the chi-square value and residuals of a fit between experimental and calculated data.
``ensemble2traj``
    Create a .xtc trajectory file from an ensemble of .pdb files.
``traj2saxs``
    Calculate a theoretical SAXS curve from a trajectory file using Pepsi-SAXS.

"""

from ensemblify.conversion.conversion_utils import calc_chi2_fit
from ensemblify.conversion.ensemble2trajectory import ensemble2traj
from ensemblify.conversion.trajectory2saxs import traj2saxs

__all__ = [
    'calc_chi2_fit',
    'ensemble2traj',
    'traj2saxs']
