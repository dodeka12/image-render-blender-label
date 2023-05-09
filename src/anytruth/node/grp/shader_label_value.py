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


def Create(*, bForce=False, bUseFakeUser=False):
    """
    Create shader node group for shader label value.
    """

    # Create the name for the sensor specs shade node tree
    sGrpName = "AT.Func.ShaderLabelValue"

    # Try to get ray splitter specification node group
    ngMain = bpy.data.node_groups.get(sGrpName)

    ####!!! Debug
    # bpy.data.node_groups.remove(ngMain)
    # ngMain = None
    ####!!!

    if ngMain is None:
        ngMain = bpy.data.node_groups.new(sGrpName, "ShaderNodeTree")
        bUpdate = True
    else:
        bUpdate = bForce
    # endif

    if bUpdate:
        # Remove all nodes that may be present
        for nod in ngMain.nodes:
            ngMain.nodes.remove(nod)
        # endfor

        ngMain.use_fake_user = bUseFakeUser

        tNodeSpace = (50, 25)
        tNodeSpaceSmall = (25, 15)

        # Define Inputs
        sMaxInstCnt = "Max. Inst. Count"
        sTypeCnt = "Type Count"
        sInstIdx = "Instance Idx"
        sTypeIdx = "Type Idx"

        lInputs = [
            [sMaxInstCnt, "NodeSocketFloat", 1.0],
            [sTypeCnt, "NodeSocketFloat", 1.0],
            [sInstIdx, "NodeSocketFloat", 0.0],
            [sTypeIdx, "NodeSocketFloat", 0.0],
        ]

        # Define Output
        sValueOut = "Shader Label Value"

        lOutputs = [[sValueOut, "NodeSocketFloat"]]

        # Add group inputs if necessary and set default values
        nodIn = nsh.utils.ProvideNodeTreeInputs(ngMain, lInputs)

        skMaxInstCnt = nodIn.outputs[sMaxInstCnt]
        skTypeCnt = nodIn.outputs[sTypeCnt]
        skInstIdx = nodIn.outputs[sInstIdx]
        skTypeIdx = nodIn.outputs[sTypeIdx]

        # Add group outputs if necessary
        nodOut = nsh.utils.ProvideNodeTreeOutputs(ngMain, lOutputs)

        nodIn.location = (-400, 0)

        skTotalCnt = nsh.math.Multiply(ngMain, "Total Count", skMaxInstCnt, skTypeCnt)
        nalign.Relative(nodIn, (1, 0), skTotalCnt, (0, 1), tNodeSpace)

        skInstVal = nsh.math.Multiply(ngMain, "Instance Value", skTypeCnt, skInstIdx)
        nalign.Relative(skTotalCnt, (1, 1), skInstVal, (1, 0), tNodeSpaceSmall)

        skLabelIdx = nsh.math.Add(ngMain, "Label Index", skInstVal, skTypeIdx)
        nalign.Relative(skInstVal, (1, 1), skLabelIdx, (1, 0), tNodeSpaceSmall)

        skMaxVal = nsh.math.Add(ngMain, "Max Value", skTotalCnt, 1.0)
        nalign.Relative(skTotalCnt, (1, 0), skMaxVal, (0, 0), tNodeSpaceSmall)

        skLabelVal = nsh.math.Add(ngMain, "Label Value", skLabelIdx, 1.0)
        nalign.Relative(skLabelIdx, (1, 0), skLabelVal, (0, 0), tNodeSpaceSmall)

        skValue = nsh.math.Divide(ngMain, "Norm. Label Value", skLabelVal, skMaxVal)
        nalign.Relative(skMaxVal, (1, 1), skValue, (0, 0), tNodeSpaceSmall)

        nalign.Relative(skValue, (1, 0), nodOut, (0, 0), tNodeSpace)
        ngMain.links.new(nodOut.inputs[sValueOut], skValue)

        # ###############################################################
    # endif

    return ngMain


# enddef
