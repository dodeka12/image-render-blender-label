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
from anybase.cls_anyexcept import CAnyExcept
from anyblend.cls_material import CMaterial
import anyblend

from .. import node
from ..node.shader.types import ELabelShaderTypes


#####################################################################
# @staticmethod
def CreateName(sId):
    return "AnyTruth.Depth.{0}".format(sId)


# enddef


#####################################################################
# Plastic material class
class CObjectLoc3d(CMaterial):
    def __init__(
        self,
        *,
        sName="Default",
        tOffset: tuple[float, float, float] = (0.0, 0.0, 0.0),
        eLabelShaderType: ELabelShaderTypes = ELabelShaderTypes.DIFFUSE,
        bForce=False,
    ):
        super().__init__(sName=CreateName(sName), bForce=bForce)

        self._eLabelShaderType: ELabelShaderTypes = eLabelShaderType

        if self._bNeedUpdate:
            self._Create(sName=sName, tOffset=tOffset, bForce=bForce)
        # endif

    # enddef

    #####################################################################
    def _Create(self, sName="", tOffset: tuple[float, float, float] = (0.0, 0.0, 0.0), bForce=False):

        tNodeSpace = (50, 25)

        self.RemoveNode("Principled BSDF")

        if bForce:
            for xNode in self.xNodes:
                if xNode.name != "Material Output":
                    self.xNodes.remove(xNode)
                # endif
            # endfor
        # endif

        sklObjInfo = anyblend.node.shader.utils.ObjectInfo(self.xNodeTree)

        skAddOffset = anyblend.node.shader.vector.Add(self.xNodeTree, "Add Offset", sklObjInfo["Location"], tOffset)

        skObjColor: bpy.types.NodeSocket = None

        if self._eLabelShaderType == ELabelShaderTypes.DIFFUSE:
            skObjColor = anyblend.node.shader.bsdf.Diffuse(self.xNodeTree, "Object Id", skAddOffset)

        elif self._eLabelShaderType == ELabelShaderTypes.EMISSION:
            skObjColor = anyblend.node.shader.bsdf.Emission(self.xNodeTree, "Object Id", skAddOffset, 1.0)

        else:
            raise RuntimeError(f"Unsupported label shader type: {self._eLabelShaderType}")
        # endif

        nodOut = self.GetNode("Material Output")

        anyblend.node.align.Relative(nodOut, (0, 0), skObjColor, (1, 0), tNodeSpace)
        anyblend.node.align.Relative(skObjColor, (0, 0), skAddOffset, (1, 0), tNodeSpace)
        anyblend.node.align.Relative(skAddOffset, (0, 0), sklObjInfo, (1, 0), tNodeSpace)

        self.CreateLink(xOut=skObjColor, xIn=nodOut.inputs["Surface"])

        self._bNeedUpdate = False

    # enddef


# endclass
