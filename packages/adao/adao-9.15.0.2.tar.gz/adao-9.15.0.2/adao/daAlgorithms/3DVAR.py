# -*- coding: utf-8 -*-
#
# Copyright (C) 2008-2025 EDF R&D
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 USA
#
# See http://www.salome-platform.org/ or email : webmaster.salome@opencascade.com
#
# Author: Jean-Philippe Argaud, jean-philippe.argaud@edf.fr, EDF R&D

import numpy
from daCore import BasicObjects, NumericObjects
from daAlgorithms.Atoms import std3dvar, van3dvar, incr3dvar, psas3dvar

# ==============================================================================
class ElementaryAlgorithm(BasicObjects.Algorithm):

    def __init__(self):
        BasicObjects.Algorithm.__init__(self, "3DVAR")
        self.defineRequiredParameter(
            name     = "Variant",
            default  = "3DVAR",
            typecast = str,
            message  = "Variant ou formulation de la méthode",
            listval  = [
                "3DVAR",
                "3DVAR-VAN",
                "3DVAR-Incr",
                "3DVAR-PSAS",
            ],
            listadv  = [
                "OneCorrection",
                "3DVAR-Std",
                "Incr3DVAR",
            ],
        )
        self.defineRequiredParameter(
            name     = "Minimizer",
            default  = "LBFGSB",
            typecast = str,
            message  = "Minimiseur utilisé",
            listval  = [
                "LBFGSB",
                "TNC",
                "CG",
                "BFGS",
            ],
            listadv  = [
                "NCG",
            ],
        )
        self.defineRequiredParameter(
            name     = "EstimationOf",
            default  = "Parameters",
            typecast = str,
            message  = "Estimation d'état ou de paramètres",
            listval  = ["State", "Parameters"],
        )
        self.defineRequiredParameter(
            name     = "MaximumNumberOfIterations",
            default  = 15000,
            typecast = int,
            message  = "Nombre maximal de pas d'optimisation",
            minval   = -1,
            oldname  = "MaximumNumberOfSteps",
        )
        self.defineRequiredParameter(
            name     = "CostDecrementTolerance",
            default  = 1.e-7,
            typecast = float,
            message  = "Diminution relative minimale du coût lors de l'arrêt",
            minval   = 0.,
        )
        self.defineRequiredParameter(
            name     = "ProjectedGradientTolerance",
            default  = -1,
            typecast = float,
            message  = "Maximum des composantes du gradient projeté lors de l'arrêt",
            minval   = -1,
        )
        self.defineRequiredParameter(
            name     = "GradientNormTolerance",
            default  = 1.e-05,
            typecast = float,
            message  = "Maximum des composantes du gradient lors de l'arrêt",
            minval   = 0.,
        )
        self.defineRequiredParameter(
            name     = "StoreInternalVariables",
            default  = False,
            typecast = bool,
            message  = "Stockage des variables internes ou intermédiaires du calcul",
        )
        self.defineRequiredParameter(
            name     = "StoreSupplementaryCalculations",
            default  = [],
            typecast = tuple,
            message  = "Liste de calculs supplémentaires à stocker et/ou effectuer",
            listval  = [
                "Analysis",
                "APosterioriCorrelations",
                "APosterioriCovariance",
                "APosterioriStandardDeviations",
                "APosterioriVariances",
                "BMA",
                "CostFunctionJ",
                "CostFunctionJAtCurrentOptimum",
                "CostFunctionJb",
                "CostFunctionJbAtCurrentOptimum",
                "CostFunctionJo",
                "CostFunctionJoAtCurrentOptimum",
                "CurrentIterationNumber",
                "CurrentOptimum",
                "CurrentState",
                "CurrentStepNumber",
                "EnsembleOfSimulations",
                "EnsembleOfStates",
                "ForecastState",
                "IndexOfOptimum",
                "Innovation",
                "InnovationAtCurrentAnalysis",
                "InnovationAtCurrentState",
                "JacobianMatrixAtBackground",
                "JacobianMatrixAtOptimum",
                "KalmanGainAtOptimum",
                "MahalanobisConsistency",
                "OMA",
                "OMB",
                "SampledStateForQuantiles",
                "SigmaObs2",
                "SimulatedObservationAtBackground",
                "SimulatedObservationAtCurrentOptimum",
                "SimulatedObservationAtCurrentState",
                "SimulatedObservationAtOptimum",
                "SimulationQuantiles",
            ],
        )
        self.defineRequiredParameter(
            name     = "Quantiles",
            default  = [],
            typecast = tuple,
            message  = "Liste des valeurs de quantiles",
            minval   = 0.,
            maxval   = 1.,
        )
        self.defineRequiredParameter(
            name     = "SetSeed",
            typecast = numpy.random.seed,
            message  = "Graine fixée pour le générateur aléatoire",
        )
        self.defineRequiredParameter(
            name     = "NumberOfSamplesForQuantiles",
            default  = 100,
            typecast = int,
            message  = "Nombre d'échantillons simulés pour le calcul des quantiles",
            minval   = 1,
        )
        self.defineRequiredParameter(
            name     = "SimulationForQuantiles",
            default  = "Linear",
            typecast = str,
            message  = "Type de simulation en estimation des quantiles",
            listval  = ["Linear", "NonLinear"]
        )
        self.defineRequiredParameter(  # Pas de type
            name     = "Bounds",
            message  = "Liste des paires de bornes",
        )
        self.defineRequiredParameter(  # Pas de type
            name     = "StateBoundsForQuantiles",
            message  = "Liste des paires de bornes pour les états utilisés en estimation des quantiles",
        )
        self.defineRequiredParameter(
            name     = "InitializationPoint",
            typecast = numpy.ravel,
            message  = "État initial imposé (par défaut, c'est l'ébauche si None)",
        )
        self.requireInputArguments(
            mandatory= ("Xb", "Y", "HO", "R", "B"),
            optional = ("U", "EM", "CM", "Q"),
        )
        self.setAttributes(
            tags=(
                "DataAssimilation",
                "NonLinear",
                "Variational",
            ),
            features=(
                "NonLocalOptimization",
                "DerivativeNeeded",
                "ParallelDerivativesOnly",
                "ConvergenceOnBoth",
            ),
        )

    def run(self, Xb=None, Y=None, U=None, HO=None, EM=None, CM=None, R=None, B=None, Q=None, Parameters=None):
        self._pre_run(Parameters, Xb, Y, U, HO, EM, CM, R, B, Q)
        #
        # --------------------------
        if self._parameters["Variant"] in ["3DVAR", "3DVAR-Std"]:
            NumericObjects.multiXOsteps(
                self, Xb, Y, U, HO, EM, CM, R, B, Q, std3dvar.std3dvar
            )
        #
        elif self._parameters["Variant"] == "3DVAR-VAN":
            NumericObjects.multiXOsteps(
                self, Xb, Y, U, HO, EM, CM, R, B, Q, van3dvar.van3dvar
            )
        #
        elif self._parameters["Variant"] in ["3DVAR-Incr", "Incr3DVAR"]:
            NumericObjects.multiXOsteps(
                self, Xb, Y, U, HO, EM, CM, R, B, Q, incr3dvar.incr3dvar
            )
        #
        elif self._parameters["Variant"] == "3DVAR-PSAS":
            NumericObjects.multiXOsteps(
                self, Xb, Y, U, HO, EM, CM, R, B, Q, psas3dvar.psas3dvar
            )
        #
        # --------------------------
        elif self._parameters["Variant"] == "OneCorrection":
            Xini = self._parameters["InitializationPoint"]
            std3dvar.std3dvar(self, Xb, Xini, Y, U, HO, CM, R, B)
        #
        # --------------------------
        else:
            raise ValueError("Error in Variant name: %s" % self._parameters["Variant"])
        #
        self._post_run(HO, EM)
        return 0

# ==============================================================================
if __name__ == "__main__":
    print("\n AUTODIAGNOSTIC\n")
