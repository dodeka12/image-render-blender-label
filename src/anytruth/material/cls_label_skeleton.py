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

# from anybase.cls_anyexcept import CAnyExcept
from anyblend.cls_material import CMaterial
import anyblend

from .. import node
from ..node.shader.types import ELabelShaderTypes


#####################################################################
# @staticmethod
def CreateName(sLabelId, sSkelId):
    return "AnyTruth.Label.{0};{1}".format(sLabelId, sSkelId)


# enddef


#####################################################################
# Material class for skeleton labelling, using red channel of
# vertex color layer for shader label index
class CLabelSkeleton(CMaterial):
    def __init__(
        self,
        *,
        iLabelTypeCount,
        iMaxInstCount,
        iId,
        sLabelId,
        sSkelId,
        eLabelShaderType: ELabelShaderTypes = ELabelShaderTypes.DIFFUSE,
        bForce=True,
    ):
        super().__init__(sName=CreateName(sLabelId, sSkelId), bForce=bForce)

        self._iLabelTypeCount = iLabelTypeCount
        self._iMaxInstCount = iMaxInstCount
        self._iId = iId
        self._sLabelId = sLabelId
        self._sSkelId = sSkelId
        self._sVexColLayName = "AT.Label;{};{}".format(sSkelId, sLabelId)
        self._eLabelShaderType: ELabelShaderTypes = eLabelShaderType

        self._modLabelShaderColor = None

        if self._eLabelShaderType == ELabelShaderTypes.DIFFUSE:
            self._modLabelShaderColor = node.shader.label_diffuse
        elif self._eLabelShaderType == ELabelShaderTypes.EMISSION:
            self._modLabelShaderColor = node.shader.label_emission
        else:
            raise RuntimeError(f"Unsupported label shader type: {self._eLabelShaderType}")
        # endif

        if self._bNeedUpdate:
            self._Create()
        # endif

    # enddef

    #####################################################################
    @property
    def sVertexColorLayerName(self):
        return self._sVexColLayName

    # enddef

    #####################################################################
    def _Create(self):

        tNodeSpace = (50, 25)

        self.RemoveNode("Principled BSDF")

        ngMatLabVal = node.grp.material_label_value.Create(
            iLabelTypeCount=self._iLabelTypeCount, iMaxInstCount=self._iMaxInstCount
        )
        nodMatLabVal = anyblend.node.shader.utils.Group(self.xNodeTree, ngMatLabVal)

        ngLabelColor = self._modLabelShaderColor.Create(bUseFakeUser=True)
        nodLabelColor = anyblend.node.shader.utils.Group(self.xNodeTree, ngLabelColor)

        nodVexColLayer = anyblend.node.shader.utils.VertexColor(self.xNodeTree, self._sVexColLayName)
        nodOut = self.GetNode("Material Output")

        anyblend.node.align.Relative(nodOut, (0, 0), nodLabelColor, (1, 0), tNodeSpace)
        self.CreateLink(xOut=nodLabelColor.outputs[0], xIn=nodOut.inputs["Surface"])

        anyblend.node.align.Relative(nodLabelColor, (0, 0), nodMatLabVal, (1, 0), tNodeSpace)
        self.CreateLink(
            xOut=nodMatLabVal.outputs[0],
            xIn=nodLabelColor.inputs["Material Label Value"],
        )

        anyblend.node.align.Relative(nodMatLabVal, (0, 1), nodVexColLayer, (0, 0), tNodeSpace)

        nodSepCol = anyblend.node.shader.color.SeparateRGB(self.xNodeTree, "Split RGB", nodVexColLayer["Color"])
        anyblend.node.align.Relative(nodVexColLayer, (1, 1), nodSepCol, (1, 0), tNodeSpace)

        self.CreateLink(xOut=nodSepCol["R"], xIn=nodLabelColor.inputs["Shader Label Value"])

        self.xMaterial.pass_index = self._iId
        self._bNeedUpdate = False

    # enddef


# endclass
