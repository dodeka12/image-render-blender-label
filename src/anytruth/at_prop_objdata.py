#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \at_prop_objdata.py
# Created Date: Thursday, May 20th 2021, 3:15:50 pm
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
class CPgAtMaterial(bpy.types.PropertyGroup):

    # user id
    sId: bpy.props.StringProperty(default="")
    # associated user label material id
    sUserId: bpy.props.StringProperty(default="")

    bFakeUser: bpy.props.BoolProperty(default=False)


# endclass


###################################################################################
class CPgAtMesh(bpy.types.PropertyGroup):

    sId: bpy.props.StringProperty(default="")
    bLodEnabled: bpy.props.BoolProperty(default=False)
    clMaterial: bpy.props.CollectionProperty(type=CPgAtMaterial)


# endclass


###################################################################################
class CPgAtObjectData(bpy.types.PropertyGroup):

    sId: bpy.props.StringProperty(default="")
    sLabelId: bpy.props.StringProperty(default="")
    sMaterialType: bpy.props.StringProperty(default="")
    clMeshes: bpy.props.CollectionProperty(type=CPgAtMesh)
    iPassIdx: bpy.props.IntProperty(default=0)
    iLabelPassIdx: bpy.props.IntProperty(default=0)
    bIsShadowCatcher: bpy.props.BoolProperty(default=False)


# endclass


###################################################################################
class CPgAtIgnoreObjectData(bpy.types.PropertyGroup):

    sId: bpy.props.StringProperty(default="")
    bHideRender: bpy.props.BoolProperty(default=True)
    bHideViewport: bpy.props.BoolProperty(default=True)


# endclass


###################################################################################
# Register


def register():

    bpy.utils.register_class(CPgAtMaterial)
    bpy.utils.register_class(CPgAtMesh)
    bpy.utils.register_class(CPgAtObjectData)
    bpy.utils.register_class(CPgAtIgnoreObjectData)


# enddef


def unregister():

    bpy.utils.unregister_class(CPgAtIgnoreObjectData)
    bpy.utils.unregister_class(CPgAtObjectData)
    bpy.utils.unregister_class(CPgAtMesh)
    bpy.utils.unregister_class(CPgAtMaterial)


# enddef
