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

from .at_prop_clnlab import CPgAtCollectionLabel
from .at_prop_objset import CPgAtObjectSettings
from . import at_prop_clnlab
from . import at_prop_objset


###################################################################################
class CPgAtMain(bpy.types.PropertyGroup):

    xLabel: bpy.props.PointerProperty(type=CPgAtCollectionLabel)

    def clear(self):
        self.xLabel.clear()

    # enddef


# endclass


###################################################################################
class CPgAtMainObject(bpy.types.PropertyGroup):

    xSettings: bpy.props.PointerProperty(type=CPgAtObjectSettings)

    def clear(self):
        self.xSettings.clear()

    # enddef


# endclass


###################################################################################
# Register
def register():

    at_prop_clnlab.register()
    at_prop_objset.register()
    bpy.utils.register_class(CPgAtMain)
    bpy.utils.register_class(CPgAtMainObject)

    bpy.types.Collection.AnyTruth = bpy.props.PointerProperty(type=CPgAtMain)
    bpy.types.Object.AnyTruth = bpy.props.PointerProperty(type=CPgAtMainObject)


# enddef


def unregister():

    del bpy.types.Collection.AnyTruth

    bpy.utils.unregister_class(CPgAtMain)
    bpy.utils.unregister_class(CPgAtMainObject)
    at_prop_clnlab.unregister()
    at_prop_objset.unregister()


# enddef
