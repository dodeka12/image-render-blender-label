#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \cls_local_pos_3d.py
# Created Date: Monday, March 27th 2023, 8:36:59 am
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
from anyblend.cls_shader_node_tree import CShaderNodeTree
import anyblend

from ...node.shader.types import ELabelShaderTypes


#####################################################################
# @staticmethod
def CreateName(sId):
    return "AnyTruth.SNT.LocPos3d.{0}".format(sId)


# enddef


#####################################################################
# Plastic material class
class CLocalPos3d(CShaderNodeTree):
    def __init__(
        self,
        *,
        sName: str = "Default",
        bSphericalCS: bool = False,
        eLabelShaderType: ELabelShaderTypes = ELabelShaderTypes.DIFFUSE,
        bForce: bool = False,
    ):
        super().__init__(sName=CreateName(sName), bForce=bForce)

        self._eLabelShaderType: ELabelShaderTypes = eLabelShaderType
        self._bSphericalCS: bool = bSphericalCS

        if self._bNeedUpdate:
            self._Create(sName=sName, bForce=bForce)
        # endif

    # enddef

    #####################################################################
    def _Create(self, sName="", bForce=False):

        tNodeSpace = (50, 25)

        if bForce:
            self.Clear()
        # endif

        lInputs = [["Offset", "NodeSocketVector", (0, 0, 0)]]

        lOutputs = [["BSDF", "NodeSocketShader"]]

        nodIn = anyblend.node.shader.utils.ProvideNodeTreeInputs(self.xNodeTree, lInputs)
        nodOut = anyblend.node.shader.utils.ProvideNodeTreeOutputs(self.xNodeTree, lOutputs)

        nodIn.location = (0, 0)

        skGeo = anyblend.node.shader.utils.Geometry(self.xNodeTree)

        skTransform = anyblend.node.shader.vector.TransformPointWorldToObject(
            self.xNodeTree, "To Local", skGeo["Position"]
        )

        skOffset = anyblend.node.shader.vector.Add(self.xNodeTree, "Add Offset", skTransform, nodIn.outputs["Offset"])
        skScale = anyblend.node.shader.vector.Scale(self.xNodeTree, "Scale", skOffset, 100.0)
        skLocPos = skScale

        if self._bSphericalCS is True:
            skRadius = anyblend.node.shader.vector.Length(self.xNodeTree, "Radius", skScale)

            sklCoord = anyblend.node.shader.vector.SeparateXYZ(self.xNodeTree, "Coords", skTransform)
            skZdivLen = anyblend.node.shader.math.Divide(self.xNodeTree, "Z / len", sklCoord["Z"], skRadius)
            skTheta = anyblend.node.shader.math.ArcCos(self.xNodeTree, "Theta", skZdivLen)

            skVecXY = anyblend.node.shader.vector.CombineXYZ(
                self.xNodeTree, "Vec XY", sklCoord["X"], sklCoord["Y"], 0.0
            )
            skLenXY = anyblend.node.shader.vector.Length(self.xNodeTree, "Len XY", skVecXY)
            skXdivLenXY = anyblend.node.shader.math.Divide(self.xNodeTree, "X / len(xy)", sklCoord["X"], skLenXY)
            skPrePhi = anyblend.node.shader.math.ArcCos(self.xNodeTree, "Pre-Phi", skXdivLenXY)
            skSignY = anyblend.node.shader.math.Sign(self.xNodeTree, "Sign(y)", sklCoord["Y"])
            skSignedPhi = anyblend.node.shader.math.Multiply(self.xNodeTree, "Signed Phi", skPrePhi, skSignY)
            skPhi = anyblend.node.shader.math.Add(self.xNodeTree, "Phi", skSignedPhi, math.pi)

            sklColor = anyblend.node.shader.color.CombineRGB(self.xNodeTree, "Color", skRadius, skTheta, skPhi)
            skLocPos = sklColor[0]

            anyblend.node.align.Relative(sklColor, (0, 0), skRadius, (1, 1), tNodeSpace)
            anyblend.node.align.Relative(sklColor, (0, 0), skTheta, (1, 0), tNodeSpace)
            anyblend.node.align.Relative(skTheta, (0, 1), skPhi, (0, 0), tNodeSpace)

            anyblend.node.align.Relative(skTheta, (0, 0), skZdivLen, (1, 0), tNodeSpace)
            anyblend.node.align.Relative(skZdivLen, (0, 0), sklCoord, (1, 0), tNodeSpace)

            anyblend.node.align.Relative(skPhi, (0, 0), skSignedPhi, (1, 0), tNodeSpace)
            anyblend.node.align.Relative(skSignedPhi, (0, 0), skPrePhi, (1, 0), tNodeSpace)
            anyblend.node.align.Relative(skPrePhi, (1, 1), skSignY, (1, 0), tNodeSpace)
            anyblend.node.align.Relative(skPrePhi, (0, 0), skXdivLenXY, (1, 0), tNodeSpace)
            anyblend.node.align.Relative(skXdivLenXY, (0, 0), skLenXY, (1, 0), tNodeSpace)
            anyblend.node.align.Relative(skLenXY, (0, 0), skVecXY, (1, 0), tNodeSpace)

            anyblend.node.align.Relative(sklCoord, (0, 0), skOffset, (1, 1), tNodeSpace)
        # endif

        skPosColor: bpy.types.NodeSocket = None

        if self._eLabelShaderType == ELabelShaderTypes.DIFFUSE:
            skPosColor = anyblend.node.shader.bsdf.Diffuse(self.xNodeTree, "LocalPos3d", skLocPos)

        elif self._eLabelShaderType == ELabelShaderTypes.EMISSION:
            skPosColor = anyblend.node.shader.bsdf.Emission(self.xNodeTree, "LocalPos3d", skLocPos, 1.0)

        else:
            raise RuntimeError(f"Unsupported label shader type: {self._eLabelShaderType}")
        # endif

        anyblend.node.align.Relative(nodOut, (0, 0), skPosColor, (1, 0), tNodeSpace)
        anyblend.node.align.Relative(skPosColor, (0, 0), skLocPos, (1, 0), tNodeSpace)

        anyblend.node.align.Relative(skLocPos, (0, 0), skOffset, (1, 0), tNodeSpace)
        anyblend.node.align.Relative(skOffset, (0, 0), skTransform, (1, 1), tNodeSpace)

        anyblend.node.align.Relative(skTransform, (0, 0), skGeo, (1, 0), tNodeSpace)
        anyblend.node.align.Relative(skGeo, (0, 1), nodIn, (0, 0), tNodeSpace)

        self.CreateLink(xOut=skPosColor, xIn=nodOut.inputs["BSDF"])

        self._bNeedUpdate = False

    # enddef


# endclass
