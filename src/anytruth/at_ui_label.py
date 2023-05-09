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
import anyblend

# from .at_prop_clnlab import CPgAtCollectionLabel


##############################################################################
# Collection label UI
class AT_PT_CollectionLabel(bpy.types.Panel):
    """Collection Label"""

    bl_label = "Collection Label"
    bl_idname = "AT_PT_CollectionLabel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "AnyTruth"

    def draw(self, context):
        layout = self.layout
        xLabelSet = context.scene.xAtLabelSet

        clAct = anyblend.collection.GetActiveCollection(context)

        # objAct = anyblend.object.GetActiveObject(context)
        # if objAct is None or objAct.name != xLabelSet.sActiveObject:
        #     clAct = anyblend.collection.GetActiveCollection(context)
        # else:
        #     clAct = anyblend.collection.FindCollectionOfObject(context, objAct)
        # # endif

        # xLabelSet.sActiveObject = objAct.name
        # xLabelSet.sActiveCollection = clAct.name

        if clAct is not None:
            xAnyTruth = clAct.AnyTruth
            xLabel = xAnyTruth.xLabel
        # endif

        yRow = layout.row()
        yRow.label(text=clAct.name)

        if xLabelSet.bApplyAnnotation:
            yRow = layout.row()
            if xLabel.bIgnore:
                yRow.label(text="[Collection ignored]")
            else:
                if xLabel.bHasLabel:
                    yRow.label(text="Type: {0}".format(xLabel.sType))
                else:
                    yRow.label(text="[No label set]")
                # endif
            # endif
        else:
            yRow = layout.row()
            yRow.prop(xLabel, "bHasLabel")

            if xLabel.bHasLabel:
                yBox = layout.box()

                xSelType = xLabelSet.SelectedType
                if xSelType is not None:
                    yRow = yBox.row()
                    ySplit = yRow.split(factor=0.9)
                    yCol1 = ySplit.column()
                    yCol2 = ySplit.column()
                    ySplit1 = yCol1.split(factor=0.25)
                    yCol1_1 = ySplit1.column()
                    yCol1_2 = ySplit1.column()
                    yCol1_1.label(text="Sel:")
                    yCol1_2.label(text=xSelType.sId)

                    xOp = yCol2.operator(
                        "at.set_sel_label_type_to_cln", text="", icon="TRIA_DOWN"
                    )
                    xOp.sActCln = clAct.name
                # endif

                yRow = yBox.row()
                yRow.alert = xLabel.sType not in xLabelSet.clTypes
                yRow.prop(xLabel, "sType")

                yRow = layout.row()
                yRow.prop(xLabel, "eChildrenInstanceType")
            else:

                yRow = layout.row()
                yRow.prop(xLabel, "bIgnore")

            # endif
        # endif

    # enddef


# endclass


###################################################################################
# Register
def register():

    bpy.utils.register_class(AT_PT_CollectionLabel)


# enddef


###################################################################################
# Unregister
def unregister():

    bpy.utils.unregister_class(AT_PT_CollectionLabel)


# enddef
