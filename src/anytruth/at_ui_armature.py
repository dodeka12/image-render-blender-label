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

import anyblend

if "at_ui_list_bone" in locals():
    importlib.reload(at_ui_list_bone)
else:
    from . import at_ui_list_bone
# endif


##############################################################################
# Collection label UI
class AT_PT_Armature(bpy.types.Panel):
    """Armature"""

    bl_label = "Armature"
    bl_idname = "AT_PT_Armature"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "AnyTruth"

    def draw(self, context):
        layout = self.layout
        xLabelSet = context.scene.xAtLabelSet

        if xLabelSet.bApplyAnnotation is False:
            yRow = layout.row()
            yRow.prop(xLabelSet, "bEnableArmatureSelfOcclusion")

            yRow = layout.row()
            yRow.label(text="[Apply annotations for more options]")
            return
        # endif

        objAct = anyblend.object.GetActiveObject(context)
        if objAct is None or objAct.type != "ARMATURE":
            yRow = layout.row()
            yRow.label(text="[Select an armature]")
            return
        # endif

        yRow = layout.row()
        yRow.label(text=objAct.name)

        # Find labeltype, instance and pose data of selected armature
        xActType = None
        xActInst = None
        xActPose = None
        for xType in xLabelSet.clAppliedTypes:
            for xInst in xType.clInstances:
                xActPose = xInst.clPoses.get(objAct.name)
                if xActPose is not None:
                    xActInst = xInst
                    break
                # endif
            # endfor
            if xActInst is not None:
                xActType = xType
                break
            # endif
        # endfor

        yRow = layout.row()
        if xActType is None:
            yRow.alert = True
            yRow.label(text="Armature not found in label data")
            return
        # endif

        sLabelType = xActType.sId
        yRow.label(text="Label Type: {}".format(sLabelType))

        yRow = layout.row()
        if len(xActPose.clSkelId) == 0:
            yRow.alert = True
            yRow.label("[No label skeleton defined]")
            return
        # endif

        sSkelId = xActPose.clSkelId[0].sId
        yRow.label(text="Skeleton: {}".format(sSkelId))

        yRow = layout.row()
        xSkeleton = xActType.clSkeletons.get(sSkelId)
        if xSkeleton is None:
            yRow.alert = True
            yRow.label(text="[Skeleton type '{}' not defined]".format(sSkelId))
            return
        # endif

        yRow.template_list(
            "AT_UL_BoneList",
            "",
            xSkeleton,
            "clBoneId",
            xSkeleton,
            "iBoneSelIdx",
            type="DEFAULT",
        )

        yRow = layout.row()
        yRow.prop(xSkeleton, "fActBoneEnvDist")

        yRow = layout.row()
        yRow.prop(xSkeleton, "fActBoneRadiusHead")

        yRow = layout.row()
        yRow.prop(xSkeleton, "bApplyToAll")

        # yRow = layout.row()
        # opBLW = yRow.operator("at.update_armature_bone_label_weights", text="", icon="FILE_REFRESH")
        # opBLW.sArmature = xActPose.sId

    # enddef


# endclass


###################################################################################
# Register
def register():

    at_ui_list_bone.register()
    bpy.utils.register_class(AT_PT_Armature)


# enddef


###################################################################################
# Unregister
def unregister():

    bpy.utils.unregister_class(AT_PT_Armature)
    at_ui_list_bone.unregister()


# enddef
