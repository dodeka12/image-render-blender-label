#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \node\shader\Label.py
# Created Date: Thursday, May 20th 2021, 2:23:17 pm
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

##########################################################
# Node group to calculate polynomial
import bpy
from anybase.cls_anyexcept import CAnyExcept
import anyblend

nsh = anyblend.node.shader
nalign = anyblend.node.align

##########################################################
# Create pixel fraction grid group


def Create(*, iLabelTypeCount, iMaxInstCount):
    """
    Create shader node group for label color material.
    Optional Parameters:
        Force: Renew node tree even if group already exists.
    """

    if iLabelTypeCount < 1:
        raise CAnyExcept("The number of label types must be larger than zero")
    # endif

    if iMaxInstCount < 1:
        raise CAnyExcept("The maximal number of instances must be larger than zero")
    # endif

    # Create the name for the sensor specs shade node tree
    sGrpName = "AnyTruth.Label.Std"

    # Try to get ray splitter specification node group
    ngMain = bpy.data.node_groups.get(sGrpName)

    ####!!! Debug
    # bpy.data.node_groups.remove(ngMain)
    # ngMain = None
    ####!!!

    if ngMain is None:
        ngMain = bpy.data.node_groups.new(sGrpName, "ShaderNodeTree")
    # endif

    # Remove all nodes that may be present
    for nod in ngMain.nodes:
        ngMain.nodes.remove(nod)
    # endfor

    tNodeSpace = (50, 25)
    tNodeSpaceSmall = (25, 15)

    # Define Inputs
    lInputs = []

    # Define Output
    sShaderOut = "Emission"
    sColorOut = "Color"

    lOutputs = [[sShaderOut, "NodeSocketShader"], [sColorOut, "NodeSocketColor"]]

    # Add group inputs if necessary and set default values
    nodIn = nsh.utils.ProvideNodeTreeInputs(ngMain, lInputs)

    # Add group outputs if necessary
    nodOut = nsh.utils.ProvideNodeTreeOutputs(ngMain, lOutputs)

    nodIn.location = (-400, 0)

    skInstCnt = nsh.utils.Value(ngMain, "Max Instance Count", iMaxInstCount)
    nalign.Relative(nodIn, (1, 0), skInstCnt, (0, 0), tNodeSpace)

    skTypeCnt = nsh.utils.Value(ngMain, "Label Type Count", iLabelTypeCount)
    nalign.Relative(skInstCnt, (1, 1), skTypeCnt, (1, 0), tNodeSpace)

    skMaxVal = nsh.math.Multiply(ngMain, "Max Value", skInstCnt, skTypeCnt)
    nalign.Relative(skInstCnt, (1, 0), skMaxVal, (0, 0), tNodeSpace)

    skObjInfo = nsh.utils.ObjectInfo(ngMain)
    nalign.Relative(skTypeCnt, (1, 1), skObjInfo, (1, 0), tNodeSpaceSmall)

    skObjIdx = nsh.math.Multiply(
        ngMain, "Object Index", skTypeCnt, skObjInfo["Object Index"]
    )
    nalign.Relative(skMaxVal, (1, 1), skObjIdx, (1, 0), tNodeSpace)

    skCombined = nsh.math.Add(
        ngMain, "Combined Index", skObjIdx, skObjInfo["Material Index"]
    )
    nalign.Relative(skObjIdx, (1, 1), skCombined, (1, 0), tNodeSpaceSmall)

    skValue = nsh.math.Divide(ngMain, "Value", skCombined, skMaxVal)
    nalign.Relative(skCombined, (1, 1), skValue, (1, 0), tNodeSpaceSmall)

    skColor = nsh.color.CombineRGB(ngMain, "Combined Color", skValue, 0.0, 1.0)
    nalign.Relative(skValue, (1, 1), skColor, (1, 0), tNodeSpaceSmall)

    shEmission = nsh.bsdf.Emission(ngMain, "Label Color", skColor[0], 1.0)
    nalign.Relative(skCombined, (1, 0), shEmission, (0, 0), tNodeSpace)

    nalign.Relative(shEmission, (1, 0), nodOut, (0, 0), tNodeSpace)
    ngMain.links.new(nodOut.inputs[sShaderOut], shEmission)
    ngMain.links.new(nodOut.inputs[sColorOut], skColor[0])

    # ###############################################################

    return ngMain


# enddef
