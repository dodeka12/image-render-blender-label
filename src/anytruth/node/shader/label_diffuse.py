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
    Combine material and shader label values to output diffuse shader with label color.
    Optional Parameters:
        Force: Renew node tree even if group already exists.
    """

    # Create the name for the sensor specs shade node tree
    sGrpName = "AT.Shader.Label.Diffuse.v1"

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
        # endif

        ngMain.use_fake_user = bUseFakeUser

        tNodeSpace = (50, 25)
        tNodeSpaceSmall = (25, 15)

        # Define Inputs
        sMatVal = "Material Label Value"
        sShVal = "Shader Label Value"
        lInputs = [[sMatVal, "NodeSocketFloat", 0.0], [sShVal, "NodeSocketFloat", 0.0]]

        # Define Output
        sShaderOut = "BSDF"

        lOutputs = [[sShaderOut, "NodeSocketShader"]]

        # Add group inputs if necessary and set default values
        # ngMain.inputs.clear()
        nodIn = nsh.utils.ProvideNodeTreeInputs(ngMain, lInputs)
        skMatVal = nodIn.outputs[sMatVal]
        skShVal = nodIn.outputs[sShVal]

        # Add group outputs if necessary
        # ngMain.outputs.clear()
        nodOut = nsh.utils.ProvideNodeTreeOutputs(ngMain, lOutputs)

        nodIn.location = (-400, 0)

        skColor = nsh.color.CombineRGB(ngMain, "Combined Color", skMatVal, skShVal, 1.0)
        nalign.Relative(nodIn, (1, 0), skColor, (0, 0), tNodeSpace)

        shDiffuse = nsh.bsdf.Diffuse(ngMain, "Label Color", skColor[0])
        nalign.Relative(skColor, (1, 0), shDiffuse, (0, 0), tNodeSpace)

        nalign.Relative(shDiffuse, (1, 0), nodOut, (0, 0), tNodeSpace)
        ngMain.links.new(nodOut.inputs[sShaderOut], shDiffuse)
    # endif

    # ###############################################################

    return ngMain


# enddef
