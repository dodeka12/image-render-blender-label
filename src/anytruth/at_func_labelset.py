#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \at_func_labelset.py
# Created Date: Thursday, May 20th 2021, 10:50:23 am
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
import traceback
from .cls_prop_labelset import CLabelSet
from . import at_global
from .object import armature


#######################################################################################
def ImportLabelTypes(self, context, _sPathTypes: str = None):

    try:
        xLabelSetProp = context.scene.xAtLabelSet
        if xLabelSetProp is None:
            raise Exception("Label set data does not exist in scene")
        # endif

        xLabelSet = CLabelSet(xLabelSetProp)

        if isinstance(_sPathTypes, str):
            xLabelSet.sFilePathImport = _sPathTypes
        # endif

        xLabelSet.ImportTypes()

    except Exception as xEx:
        self.report({"ERROR"}, str(xEx))
        traceback.print_exception(type(xEx), xEx, xEx.__traceback__)
    # endif


# enddef


#######################################################################################
def ExportAppliedLabelTypes(self, context):

    try:
        xLabelSetProp = context.scene.xAtLabelSet
        if xLabelSetProp is None:
            raise Exception("Label set data does not exist in scene")
        # endif

        CLabelSet(xLabelSetProp).ExportAppliedTypes()

    except Exception as xEx:
        self.report({"ERROR"}, str(xEx))
    # endif


# enddef


#######################################################################################
def UpdateArmatureBoneLabelWeights(self, context, _sArmature):

    try:
        xLabelSet = CLabelSet(context.scene.xAtLabelSet)

        if xLabelSet.bApplyAnnotation is False:
            raise Exception("Labels not applied")
        # endif

        dicBLW = xLabelSet.dicArmatureBoneLabelWeights.get(_sArmature)
        if dicBLW is None:
            raise Exception("Armature '{}' not in label set".format(_sArmature))
        # endif

        objArma = bpy.data.objects.get(_sArmature)
        if objArma is None:
            raise Exception("Armature object '{}' not found".format(_sArmature))
        # endif

        lMeshObjects = dicBLW["lMeshObjects"]
        for sMeshObject in lMeshObjects:
            objMesh = bpy.data.objects.get(sMeshObject)
            if objMesh is None:
                raise Exception("Mesh object '{}' not found".format(sMeshObject))
            # endif

            armature.CreateBoneWeightVexColLay(
                objArma=objArma,
                objMesh=objMesh,
                lBoneNames=dicBLW["lBoneNames"],
                sBoneWeightMode=dicBLW["sBoneWeightMode"],
                lLabelColors=dicBLW["lLabelColors"],
                sVexColNameLabel=dicBLW["sVexColNameLabel"],
                lPreviewColors=dicBLW["lPreviewColors"],
                sVexColNamePreview=dicBLW["sVexColNamePreview"],
            )
        # endfor
    except Exception as xEx:
        self.report({"ERROR"}, str(xEx))
    # endif


# enddef
