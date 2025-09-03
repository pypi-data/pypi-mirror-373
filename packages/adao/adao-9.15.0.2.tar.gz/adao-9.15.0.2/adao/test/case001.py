# -*- coding: utf-8 -*-
#
# Copyright (C) 2008-2019 EDF R&D
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
"Elementary test case"

import sys
import unittest
class InTest(unittest.TestCase):
    def test(self):
        #-----------------------------------------------------------------------
        from numpy import array, matrix
        from adao import adaoBuilder
        case = adaoBuilder.New()
        case.set( 'AlgorithmParameters', Algorithm='3DVAR' )
        case.set( 'Background',          Vector=[0, 1, 2] )
        case.set( 'BackgroundError',     ScalarSparseMatrix=1.0 )
        case.set( 'Observation',         Vector=array([0.5, 1.5, 2.5]) )
        case.set( 'ObservationError',    DiagonalSparseMatrix='1 1 1' )
        case.set( 'ObservationOperator', Matrix='1 0 0;0 2 0;0 0 3' )
        case.execute()
        #
        print(case.get("Analysis")[-1])
        #-----------------------------------------------------------------------


#===============================================================================
if __name__ == "__main__":
    print("\nAUTODIAGNOSTIC\n==============")
    unittest.main()
