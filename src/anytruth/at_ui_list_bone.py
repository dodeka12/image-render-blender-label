#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \ac_ui_camset.py
# Created Date: Friday, April 30th 2021, 8:05:59 am
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


##############################################################################
# The camera set element list
class AT_UL_BoneList(bpy.types.UIList):

    ##############################################################################
    def draw_item(
        self,
        context,
        layout,
        data,
        item,
        icon,
        active_data,
        active_propname,
        index,
        flt_flag,
    ):
        yRow = layout
        yRow.label(text=item.sId)

    # enddef

    ##############################################################################
    def filter_items(self, context, data, propname):

        lItems = getattr(data, propname)
        xHelper = bpy.types.UI_UL_list

        # Default return values.
        flt_flags = []
        flt_neworder = []

        # Filtering by name
        if self.filter_name:
            flt_flags = xHelper.filter_items_by_name(
                self.filter_name,
                self.bitflag_filter_item,
                lItems,
                "sId",
                reverse=self.use_filter_sort_reverse,
            )
        # endif

        if not flt_flags:
            flt_flags = [self.bitflag_filter_item] * len(lItems)
        # endif

        # Reorder by name or average weight.
        if self.use_filter_sort_alpha:
            flt_neworder = xHelper.sort_items_by_name(lItems, "sId")
        # endif

        return flt_flags, flt_neworder

    # endif


# endclass


##############################################################################
# Register
def register():
    bpy.utils.register_class(AT_UL_BoneList)


# enddef


##############################################################################
# Unregister
def unregister():
    bpy.utils.unregister_class(AT_UL_BoneList)


# enddef
