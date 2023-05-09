#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \at_prop_obj.py
# Created Date: Wednesday, May 19th 2021, 1:59:00 pm
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

###################################################################################
def _LabelTypeList(self, context):

    if context is None:
        xLabelSet = bpy.context.scene.xAtLabelSet
    else:
        xLabelSet = context.scene.xAtLabelSet
    # endif

    lTypes = [(xType.sId, xType.sId, xType.sId) for xType in xLabelSet.clTypes]
    return lTypes


# endif

###################################################################################
class CPgAtCollectionLabel(bpy.types.PropertyGroup):

    bHasLabel: bpy.props.BoolProperty(name="Has Label", default=False)

    bIgnore: bpy.props.BoolProperty(name="Ignore", default=False)

    sType: bpy.props.StringProperty(
        name="Type", description="Type of object", default="None"
    )

    eChildrenInstanceType: bpy.props.EnumProperty(
        items=[
            ("SINGLE", "Single", "All children are regarded as the same instance"),
            ("INHERIT", "Inherit", "Inherits mode from parent collection"),
            (
                "COLLECTION",
                "Collection",
                "Each child collection is regarded as an instance",
            ),
            ("OBJECT", "Object", "Each child object is regarded as an instance"),
        ],
        name="Instance Type",
        description="Determines how instance ids are distributed",
    )

    def clear(self):
        self.bHasLabel = False
        self.sType = "None"
        self.sChildrenInstanceType = "None"

    # enddef


# endclass

###################################################################################
# Register


def register():

    bpy.utils.register_class(CPgAtCollectionLabel)


# enddef


def unregister():

    bpy.utils.unregister_class(CPgAtCollectionLabel)


# enddef
