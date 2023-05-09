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

#####################################################################
# @staticmethod
def CreateName(sId):
    return "AnyTruth.Movement.{0}".format(sId)


# enddef

#####################################################################
# Plastic material class
class CMovement(CMaterial):
    def __init__(self, *, sLayerName, sName="Default", bForce=False):
        super().__init__(sName=CreateName(sName), sLayerName=sLayerName, bForce=bForce)

        if self._bNeedUpdate:
            self._Create(sName=sName, bForce=bForce)
        # endif

    # enddef

    #####################################################################
    def _Create(self, *, sLayerName, sName="", bForce=False):

        tNodeSpace = (50, 25)

        self.RemoveNode("Principled BSDF")

        if bForce:
            for xNode in self.xNodes:
                if xNode.name != "Material Output":
                    self.xNodes.remove(xNode)
                # endif
            # endfor
        # endif

        skVexCol = anyblend.node.shader.utils.VertexColor(self.xNodeTree, sLayerName)

        # Need to set emission strength to 1.25 so that color values are output 1-to-1. (Blender 2.93)
        # There seems to be a color scaling by 0.8 internally, even for the raw image output.
        skEmission = anyblend.node.shader.bsdf.Emission(
            self.xNodeTree, "Pos3d", skVexCol["Color"], 1.25
        )
        nodOut = self.GetNode("Material Output")

        anyblend.node.align.Relative(nodOut, (0, 0), skEmission, (1, 0), tNodeSpace)
        anyblend.node.align.Relative(skEmission, (0, 0), skVexCol, (1, 0), tNodeSpace)

        self.CreateLink(xOut=skEmission, xIn=nodOut.inputs["Surface"])

        self._bNeedUpdate = False

    # enddef


# endclass
