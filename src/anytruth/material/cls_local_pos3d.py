#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \material\cls_plastic.py
# Created Date: Tuesday, May 4th 2021, 8:35:47 am
# Author: Christian Perwass (CR/AEC5)
# <LICENSE id="GPL-3.0">
#
#   Image-Render Blender Label add-on module
#   Copyright (C) 2022 Robert Bosch GmbH and its subsidiaries
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#
# </LICENSE>
###

import bpy
import math

from typing import Union
from anybase.cls_anyexcept import CAnyExcept
from anyblend.cls_material import CMaterial
import anyblend

from .. import node
from ..node.shader.types import ELabelShaderTypes
from .nodegroup.cls_local_pos_3d import CLocalPos3d as CNgLocalPos3d


#####################################################################
# @staticmethod
def CreateName(sId):
    return "AnyTruth.LocPos3d.{0}".format(sId)


# enddef


#####################################################################
# Plastic material class
class CLocalPos3d(CMaterial):
    def __init__(
        self,
        *,
        sName="Default",
        bSphericalCS: bool = False,
        xOffset: Union[str, tuple[float, float, float]] = (0, 0, 0),
        eLabelShaderType: ELabelShaderTypes = ELabelShaderTypes.DIFFUSE,
        bForce=False,
    ):
        super().__init__(sName=CreateName(sName), bForce=bForce)

        self._eLabelShaderType: ELabelShaderTypes = eLabelShaderType
        self._bSphericalCS: bool = bSphericalCS

        self._sOffsetProperty: str = None
        self._tOffset: tuple[float, float, float] = None

        if isinstance(xOffset, str):
            self._sOffsetProperty = xOffset
        elif isinstance(xOffset, tuple) and len(xOffset) == 3:
            self._tOffset: tuple[float, float, float] = xOffset
        else:
            raise RuntimeError("Offset parameter must be object property name or tuple of three floats")
        # endif

        if self._bNeedUpdate:
            self._Create(sName=sName, bForce=bForce)
        # endif

    # enddef

    #####################################################################
    def _Create(self, sName="", bForce=False):

        tNodeSpace = (50, 25)

        self.RemoveNode("Principled BSDF")

        if bForce:
            for xNode in self.xNodes:
                if xNode.name != "Material Output":
                    self.xNodes.remove(xNode)
                # endif
            # endfor
        # endif

        sSntName: str = "Spherical" if self._bSphericalCS is True else "Cartesian"

        xLocPos3d = CNgLocalPos3d(
            sName=sSntName, bSphericalCS=self._bSphericalCS, eLabelShaderType=self._eLabelShaderType, bForce=True
        )

        nodOut = self.GetNode("Material Output")
        ngLocPos3d = anyblend.node.shader.utils.Group(self.xNodeTree, xLocPos3d.xNodeTree)

        anyblend.node.align.Relative(nodOut, (0, 0), ngLocPos3d, (1, 0), tNodeSpace)
        self.CreateLink(xOut=ngLocPos3d.outputs["BSDF"], xIn=nodOut.inputs["Surface"])

        if self._sOffsetProperty is not None:
            sklAttribute = anyblend.node.shader.utils.Attribute(
                self.xNodeTree, anyblend.node.shader.utils.EAttributeType.OBJECT, self._sOffsetProperty
            )
            anyblend.node.align.Relative(ngLocPos3d, (0, 0), sklAttribute, (1, 0), tNodeSpace)
            self.CreateLink(xOut=sklAttribute["Vector"], xIn=ngLocPos3d.inputs["Offset"])
        else:
            ngLocPos3d.inputs["Offset"].default_value = self._tOffset
        # endif

        self._bNeedUpdate = False

    # enddef


# endclass
