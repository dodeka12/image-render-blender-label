#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \at_ops_labelset.py
# Created Date: Thursday, May 20th 2021, 10:48:59 am
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
from . import at_func_labelset
import anyblend


#######################################################################
class COpAcImportLabelTypes(bpy.types.Operator):
    bl_idname = "at.import_label_types"
    bl_label = "Import label types"
    bl_description = "Click to import label types."

    def execute(self, context):
        at_func_labelset.ImportLabelTypes(self, context)
        return {"FINISHED"}

    # enddef


# endclass


#######################################################################
class COpAcExportAppliedLabelTypes(bpy.types.Operator):
    bl_idname = "at.export_applied_label_types"
    bl_label = "Export applied label types"
    bl_description = "Click to export applied label types."

    def execute(self, context):
        at_func_labelset.ExportAppliedLabelTypes(self, context)
        return {"FINISHED"}

    # enddef


# endclass


#######################################################################
class COpAcUpdateArmatureBoneLabelWeights(bpy.types.Operator):
    bl_idname = "at.update_armature_bone_label_weights"
    bl_label = "Update armature bone label weights"
    bl_description = "Click to update bone label weights."

    sArmature: bpy.props.StringProperty(name="Armature")

    def execute(self, context):
        at_func_labelset.UpdateArmatureBoneLabelWeights(self, context, self.sArmature)
        return {"FINISHED"}

    # enddef


# endclass


#######################################################################
class COpAcSetSelLabelTypeToCln(bpy.types.Operator):
    bl_idname = "at.set_sel_label_type_to_cln"
    bl_label = "Set Type"
    bl_description = "Click to set the selected label type to the collection."

    sActCln: bpy.props.StringProperty()

    def execute(self, context):
        xLabelSet = context.scene.xAtLabelSet
        clnAct = anyblend.collection.GetCollection(self.sActCln)
        xAnyTruth = clnAct.AnyTruth
        xType = xLabelSet.SelectedType
        if xType is not None:
            xAnyTruth.xLabel.sType = xType.sId
        # endif
        return {"FINISHED"}

    # enddef


# endclass


#######################################################################################
# Register
def register():
    bpy.utils.register_class(COpAcImportLabelTypes)
    bpy.utils.register_class(COpAcExportAppliedLabelTypes)
    bpy.utils.register_class(COpAcSetSelLabelTypeToCln)
    bpy.utils.register_class(COpAcUpdateArmatureBoneLabelWeights)


# enddef


#######################################################################################
def unregister():

    bpy.utils.unregister_class(COpAcSetSelLabelTypeToCln)
    bpy.utils.unregister_class(COpAcExportAppliedLabelTypes)
    bpy.utils.unregister_class(COpAcImportLabelTypes)
    bpy.utils.unregister_class(COpAcUpdateArmatureBoneLabelWeights)


# enddef
