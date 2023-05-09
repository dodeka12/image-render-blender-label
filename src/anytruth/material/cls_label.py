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
    return "AnyTruth.Label.{0}".format(sId)


# enddef

#####################################################################
# Plastic material class
class CLabel(CMaterial):
    def __init__(
        self,
        *,
        iLabelTypeCount: int,
        iMaxInstCount: int,
        iId: int,
        sName: str = "Default",
        eLabelShaderType: ELabelShaderTypes = ELabelShaderTypes.DIFFUSE,
        bForce: bool = False,
    ):
        super().__init__(sName=CreateName(sName), bForce=bForce)

        self._iLabelTypeCount: int = iLabelTypeCount
        self._iMaxInstCount: int = iMaxInstCount
        self._iId: int = iId
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
            self._Create(sName=sName, bForce=bForce)
        # endif

    # enddef

    #####################################################################
    def _Create(self, sName="", bForce=False):

        tNodeSpace = (50, 25)

        self.RemoveNode("Principled BSDF")

        ngMatLabVal = node.grp.material_label_value.Create(
            iLabelTypeCount=self._iLabelTypeCount, iMaxInstCount=self._iMaxInstCount
        )
        nodMatLabVal = anyblend.node.shader.utils.Group(self.xNodeTree, ngMatLabVal)

        ngLabelColor = self._modLabelShaderColor.Create(bUseFakeUser=True)
        nodLabelColor = anyblend.node.shader.utils.Group(self.xNodeTree, ngLabelColor)

        nodOut = self.GetNode("Material Output")

        anyblend.node.align.Relative(nodOut, (0, 0), nodLabelColor, (1, 0), tNodeSpace)
        self.CreateLink(xOut=nodLabelColor.outputs["BSDF"], xIn=nodOut.inputs["Surface"])

        anyblend.node.align.Relative(nodLabelColor, (0, 0), nodMatLabVal, (1, 0), tNodeSpace)
        self.CreateLink(
            xOut=nodMatLabVal.outputs[0],
            xIn=nodLabelColor.inputs["Material Label Value"],
        )

        self.xMaterial.pass_index = self._iId
        self._bNeedUpdate = False

    # enddef


# endclass
