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


##############################################################################
# Collection label UI
class AT_PT_ObjectSettings(bpy.types.Panel):
    """Object Settings"""

    bl_label = "Object Settings"
    bl_idname = "AT_PT_ObjectSettings"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "AnyTruth"

    def draw(self, context):
        layout = self.layout

        objX = bpy.context.view_layer.objects.active
        if objX is None:
            yRow = layout.row()
            yRow.label(text="[No active object]")
            return
        # endif

        xObjSet = objX.AnyTruth.xSettings

        yRow = layout.row()
        yRow.label(text=objX.name)

        yRow = layout.row()
        yRow.prop(xObjSet, "bIgnore")

    # enddef


# endclass


###################################################################################
# Register
def register():

    bpy.utils.register_class(AT_PT_ObjectSettings)


# enddef


###################################################################################
# Unregister
def unregister():

    bpy.utils.unregister_class(AT_PT_ObjectSettings)


# enddef
