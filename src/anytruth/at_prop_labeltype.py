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
class CPgAtShaderTypes(bpy.types.PropertyGroup):

    sId: bpy.props.StringProperty(name="Shader Type Id")


# endclass

###################################################################################
class CPgAtBox2d(bpy.types.PropertyGroup):

    bIsValid: bpy.props.BoolProperty(default=False, name="IsValid")

    vMinXY: bpy.props.FloatVectorProperty(name="Min XY")
    vMaxXY: bpy.props.FloatVectorProperty(name="Max XY")

    def clear(self):
        self.vMinXY = (0, 0, 0)
        self.vMaxXY = (0, 0, 0)

    # enddef


# endclass


###################################################################################
class CPgAtBox3d(bpy.types.PropertyGroup):

    bIsValid: bpy.props.BoolProperty(default=False, name="IsValid")

    vCenter: bpy.props.FloatVectorProperty(name="Center")
    vSize: bpy.props.FloatVectorProperty(name="Size")
    vAxisX: bpy.props.FloatVectorProperty(name="Axis X")
    vAxisY: bpy.props.FloatVectorProperty(name="Axis Y")
    vAxisZ: bpy.props.FloatVectorProperty(name="Axis Z")

    def clear(self):
        self.vCenter = (0, 0, 0)
        self.vSize = (0, 0, 0)

    # enddef


# endclass


###################################################################################
class CPgAtBoneId(bpy.types.PropertyGroup):
    sId: bpy.props.StringProperty(name="Bone Id")


# endclass


###################################################################################
class CPgAtSkelId(bpy.types.PropertyGroup):
    sId: bpy.props.StringProperty(name="Skeleton Id")


# endclass


###################################################################################
# Helper Functions for CPgAtSkeleton
def _CPgAtSkeleton_GetBone(self, _sBoneId):
    sBoneId = "AT.Label;{};{}".format(self.sId, _sBoneId)

    objAct = bpy.context.active_object
    if objAct is None or objAct.type != "ARMATURE":
        return None
    # endif

    return objAct.data.bones.get(sBoneId)


# enddef


def _CPgAtSkeleton_GetActBone(self):
    if self.iBoneSelIdx >= 0 and self.iBoneSelIdx < len(self.clBoneId):
        sBoneId = self.clBoneId[self.iBoneSelIdx].sId
        return _CPgAtSkeleton_GetBone(self, sBoneId)
    # endif
    return None


# enddef


def _UpdateArmatureBoneLabelWeights():

    objAct = bpy.context.active_object
    if objAct is None or objAct.type != "ARMATURE":
        return
    # endif

    bpy.ops.at.update_armature_bone_label_weights(sArmature=objAct.name)


# enddef


def _CPgAtSkeleton_GetActBoneRadiusHead(self):
    xBone = _CPgAtSkeleton_GetActBone(self)
    if xBone is None:
        return 0.0
    # endif

    return xBone.head_radius


# enddef


def _CPgAtSkeleton_SetActBoneRadiusHead(self, _fValue):
    if self.bApplyToAll is True:
        for sBoneId in self.clBoneId.keys():
            xBone = _CPgAtSkeleton_GetBone(self, sBoneId)
            xBone.head_radius = _fValue
        # endfor
    else:
        xBone = _CPgAtSkeleton_GetActBone(self)
        if xBone is not None:
            xBone.head_radius = _fValue
        # endif
    # endif
    _UpdateArmatureBoneLabelWeights()


# enddef


def _CPgAtSkeleton_GetActBoneEnvDist(self):
    xBone = _CPgAtSkeleton_GetActBone(self)
    if xBone is None:
        return 0.0
    # endif

    return xBone.envelope_distance


# enddef


def _CPgAtSkeleton_SetActBoneEnvDist(self, _fValue):
    if self.bApplyToAll is True:
        for sBoneId in self.clBoneId.keys():
            xBone = _CPgAtSkeleton_GetBone(self, sBoneId)
            xBone.envelope_distance = _fValue
        # endfor
    else:
        xBone = _CPgAtSkeleton_GetActBone(self)
        if xBone is not None:
            xBone.envelope_distance = _fValue
        # endif
    # endif
    _UpdateArmatureBoneLabelWeights()


# enddef


###################################################################################
class CPgAtSkeleton(bpy.types.PropertyGroup):
    sId: bpy.props.StringProperty(name="Skeleton Id")
    clBoneId: bpy.props.CollectionProperty(type=CPgAtBoneId)
    iBoneSelIdx: bpy.props.IntProperty(name="Selected Bone Index", default=0)

    bApplyToAll: bpy.props.BoolProperty(name="Apply to all bones")

    fActBoneRadiusHead: bpy.props.FloatProperty(
        name="Radius Head",
        min=0.0,
        max=10.0,
        soft_min=0.0,
        soft_max=1.0,
        step=1,
        get=_CPgAtSkeleton_GetActBoneRadiusHead,
        set=_CPgAtSkeleton_SetActBoneRadiusHead,
    )

    fActBoneEnvDist: bpy.props.FloatProperty(
        name="Envelope Distance",
        min=0.0,
        max=10.0,
        soft_min=0.0,
        soft_max=1.0,
        step=1,
        get=_CPgAtSkeleton_GetActBoneEnvDist,
        set=_CPgAtSkeleton_SetActBoneEnvDist,
    )


# endclass


###################################################################################
class CPgAtBone(bpy.types.PropertyGroup):

    sId: bpy.props.StringProperty(name="Bone Id")
    sParent: bpy.props.StringProperty(name="Parent Bone Id")
    clChildren: bpy.props.CollectionProperty(type=CPgAtBoneId)

    vHead: bpy.props.FloatVectorProperty(name="Head")
    vTail: bpy.props.FloatVectorProperty(name="Tail")
    vAxisX: bpy.props.FloatVectorProperty(name="Axis X")
    vAxisY: bpy.props.FloatVectorProperty(name="Axis Y")
    vAxisZ: bpy.props.FloatVectorProperty(name="Axis Z")


# endclass


###################################################################################
class CPgAtPose(bpy.types.PropertyGroup):

    sId: bpy.props.StringProperty(name="Pose Id")

    clBones: bpy.props.CollectionProperty(type=CPgAtBone)
    clSkelId: bpy.props.CollectionProperty(type=CPgAtSkelId)


# endclass


###################################################################################
class CPgAtObject(bpy.types.PropertyGroup):

    pObject: bpy.props.PointerProperty(type=bpy.types.Object, name="object")


# endclass


###################################################################################
class CPgAtVertex(bpy.types.PropertyGroup):

    vVertex: bpy.props.FloatVectorProperty(name="Vertex")


# endclass


###################################################################################
class CPgAtVertexList(bpy.types.PropertyGroup):

    eType: bpy.props.EnumProperty(
        items=[
            ("NONE", "None", "Undefined vertex list type"),
            ("LINESTRIP", "Line Strip", "A list of points connected by lines"),
        ],
        default="NONE",
        name="Vertex List Type",
    )

    clVertices: bpy.props.CollectionProperty(type=CPgAtVertex)


# endclass


###################################################################################
class CPgAtVgData(bpy.types.PropertyGroup):

    sId: bpy.props.StringProperty(name="Vertex Group Id")
    sType: bpy.props.StringProperty(name="Vertex Group Type")
    vColor: bpy.props.FloatVectorProperty(name="Color")
    clVertexLists: bpy.props.CollectionProperty(type=CPgAtVertexList)


# endclass


###################################################################################
class CPgAtVgInstance(bpy.types.PropertyGroup):

    iIdx: bpy.props.IntProperty(name="Vertex Group Instance")

    clVertexGroups: bpy.props.CollectionProperty(type=CPgAtVgData)


# endclass


###################################################################################
class CPgAtVgLabelType(bpy.types.PropertyGroup):

    sId: bpy.props.StringProperty(name="Vertex Group Label Type")

    clInstances: bpy.props.CollectionProperty(type=CPgAtVgInstance)


# endclass


###################################################################################
class CPgAtInstance(bpy.types.PropertyGroup):

    iIdx: bpy.props.IntProperty(name="Instance Idx")
    sOrientId: bpy.props.StringProperty(name="Orientation Id")

    clObjects: bpy.props.CollectionProperty(type=CPgAtObject)
    xBox2d: bpy.props.PointerProperty(type=CPgAtBox2d)
    xBox3d: bpy.props.PointerProperty(type=CPgAtBox3d)
    clPoses: bpy.props.CollectionProperty(type=CPgAtPose)
    clVexGrpTypes: bpy.props.CollectionProperty(type=CPgAtVgLabelType)

    def clear(self):
        self.iIdx = 0
        self.clObjects.clear()
        self.xBox2d.clear()
        self.xBox3d.clear()
        self.clPoses.clear()
        self.clVexGrpTypes.clear()

    # enddef


# endclass


###################################################################################
class CPgAtLabelType(bpy.types.PropertyGroup):

    sId: bpy.props.StringProperty(name="Type ID", description="Label type id")

    colLabel: bpy.props.FloatVectorProperty(default=(0.8, 0.8, 0.8), subtype="COLOR", min=0.0, max=1.0)

    iShaderMaxInstCnt: bpy.props.IntProperty(name="Shader Max Inst Cnt", default=0)

    clShaderTypes: bpy.props.CollectionProperty(type=CPgAtShaderTypes)
    clInstances: bpy.props.CollectionProperty(type=CPgAtInstance)
    clSkeletons: bpy.props.CollectionProperty(type=CPgAtSkeleton)

    def clear(self):
        self.sId = ""
        self.iShaderMaxInstCnt = 0
        self.clShaderTypes.clear()
        self.clInstances.clear()

    # enddef


# endclass


###################################################################################
# Register
def register():

    bpy.utils.register_class(CPgAtBoneId)
    bpy.utils.register_class(CPgAtBone)
    bpy.utils.register_class(CPgAtSkelId)
    bpy.utils.register_class(CPgAtSkeleton)
    bpy.utils.register_class(CPgAtPose)
    bpy.utils.register_class(CPgAtBox2d)
    bpy.utils.register_class(CPgAtBox3d)
    bpy.utils.register_class(CPgAtObject)

    bpy.utils.register_class(CPgAtVertex)
    bpy.utils.register_class(CPgAtVertexList)
    bpy.utils.register_class(CPgAtVgData)
    bpy.utils.register_class(CPgAtVgInstance)
    bpy.utils.register_class(CPgAtVgLabelType)

    bpy.utils.register_class(CPgAtInstance)

    bpy.utils.register_class(CPgAtShaderTypes)
    bpy.utils.register_class(CPgAtLabelType)


# enddef


def unregister():

    bpy.utils.unregister_class(CPgAtLabelType)
    bpy.utils.unregister_class(CPgAtShaderTypes)
    bpy.utils.unregister_class(CPgAtInstance)

    bpy.utils.unregister_class(CPgAtVertex)
    bpy.utils.unregister_class(CPgAtVertexList)
    bpy.utils.unregister_class(CPgAtVgData)
    bpy.utils.unregister_class(CPgAtVgInstance)
    bpy.utils.unregister_class(CPgAtVgLabelType)

    bpy.utils.unregister_class(CPgAtObject)
    bpy.utils.unregister_class(CPgAtBox3d)
    bpy.utils.unregister_class(CPgAtBox2d)
    bpy.utils.unregister_class(CPgAtBoneId)
    bpy.utils.unregister_class(CPgAtBone)
    bpy.utils.unregister_class(CPgAtPose)
    bpy.utils.unregister_class(CPgAtSkeleton)
    bpy.utils.unregister_class(CPgAtSkelId)


# enddef
