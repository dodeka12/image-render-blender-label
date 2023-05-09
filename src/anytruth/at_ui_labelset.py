#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \at_ui_label.py
# Created Date: Wednesday, May 19th 2021, 2:20:49 pm
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
import importlib

# import anyblend

if "at_ui_list_labeltype" in locals():
    importlib.reload(at_ui_list_labeltype)
else:
    from . import at_ui_list_labeltype
# endif
# from .at_ui_list_labeltype import AT_UL_LabelTypeList


##############################################################################
# The create camera panel, where cameras can be added to the scene
class AT_PT_LabelSet(bpy.types.Panel):
    """Label Set"""

    bl_label = "Label Set"
    bl_idname = "AT_PT_LabelSet"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "AnyTruth"

    def draw(self, context):
        xLabelSet = context.scene.xAtLabelSet
        layout = self.layout

        if len(xLabelSet.sMessage) > 0:
            yRow = layout.row()
            yRow.label(text=xLabelSet.sMessage, icon="ERROR")
            yRow.alert = True
        # endif

        yRow = layout.row()
        ySplit = yRow.split(factor=0.9)
        yCol1 = ySplit.column().row()
        yCol2 = ySplit.column().row()
        yCol1.alert = not xLabelSet.bImportFileExists
        yCol1.prop(xLabelSet, "sFilePathImport", text="Import file")
        if xLabelSet.bImportFileExists:
            yCol2.operator("at.import_label_types", text="", icon="IMPORT", emboss=True)
        else:
            yCol2.label(text="", icon="IMPORT")
        # endif

        yRow = layout.row()
        yRow.template_list(
            "AT_UL_LabelTypeList",
            "",
            xLabelSet,
            "clTypes",
            xLabelSet,
            "iTypeSelIdx",
            type="DEFAULT",
        )

        yRow = layout.row()
        ySplit = yRow.split(factor=0.5)
        yCol1 = ySplit.column().row()
        yCol2 = ySplit.column().row()
        yCol1.label(text="Annotation Type")
        yCol2.prop(xLabelSet, "eAnnotationType", text="")
        yRow = layout.row()
        yRow.prop(xLabelSet, "bApplyAnnotation")

        if xLabelSet.bApplyAnnotation and xLabelSet.eAnnotationType == "LABEL":
            yRow = layout.row()
            ySplit = yRow.split(factor=0.9)
            yCol1 = ySplit.column().row()
            yCol2 = ySplit.column().row()
            yCol1.alert = (
                xLabelSet.bExportFileExists and not xLabelSet.bOverwriteExportApplied
            )
            yCol1.prop(xLabelSet, "sFilePathExport", text="Export file")
            if not xLabelSet.bExportFileExists or xLabelSet.bOverwriteExportApplied:
                yCol2.operator(
                    "at.export_applied_label_types", text="", icon="EXPORT", emboss=True
                )
            else:
                yCol2.label(text="", icon="EXPORT")
            # endif

            yRow = layout.row()
            yRow.prop(xLabelSet, "bOverwriteExportApplied")
        # endif

    # enddef


# endclass


###################################################################################
# Register
def register():
    at_ui_list_labeltype.register()
    bpy.utils.register_class(AT_PT_LabelSet)


# enddef


###################################################################################
# Unregister
def unregister():

    bpy.utils.unregister_class(AT_PT_LabelSet)
    at_ui_list_labeltype.unregister()


# enddef
