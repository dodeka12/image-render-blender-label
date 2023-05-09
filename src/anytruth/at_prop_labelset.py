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

# import mathutils
from bpy.app.handlers import persistent

import os
import importlib
import traceback
from pathlib import Path

from . import at_global

if "at_prop_labeltype" in locals():
    importlib.reload(at_prop_labeltype)
else:
    from . import at_prop_labeltype
# endif

if "at_prop_objdata" in locals():
    importlib.reload(at_prop_objdata)
else:
    from . import at_prop_objdata
# endif

from .at_prop_labeltype import CPgAtLabelType
from .at_prop_objdata import CPgAtObjectData
from .at_prop_objdata import CPgAtIgnoreObjectData
from .cls_prop_labelset import CLabelSet


###################################################################################
def _GetLabelSet(self):
    return CLabelSet(self)
    # xLabelSet = at_global.xLabelSet
    # if xLabelSet is None:
    #     xLabelSet = at_global.xLabelSet = CLabelSet(self)
    # # endif
    # return xLabelSet


# enddef


###################################################################################
def _ImportFileExists(self):
    xPath = Path(_GetLabelSet(self).GetImportFilePath())
    if len(xPath.suffix) == 0:
        sFp = xPath.as_posix() + ".json"
    else:
        sFp = xPath.as_posix()
    # endif
    return os.path.exists(sFp)


# enddef


###################################################################################
def _ExportFileExists(self):
    xPath = Path(_GetLabelSet(self).GetExportFilePath())
    if len(xPath.suffix) == 0:
        sFp = xPath.as_posix() + ".json"
    else:
        sFp = xPath.as_posix()
    # endif
    return os.path.exists(sFp)


# enddef


###################################################################################
def _GetUseAnnotation(self):
    return _GetLabelSet(self).loc_bApplyAnnotation


# enddef


def _SetUseAnnotation(self, _bValue):
    try:
        #######################
        ### DEBUG
        # print(">>>>>>>>>>>>>>>> SetUseAnnotation!", flush=True)
        #######################
        _GetLabelSet(self).ApplyAnnotation(_bValue)
        self.sMessage = ""
    except Exception as xEx:
        self.sMessage = str(xEx)
    # endif


# enddef


###################################################################################
class CPgAtLabelSet(bpy.types.PropertyGroup):

    bIsInitialized: bpy.props.BoolProperty(name="Is Initialized", default=False)

    sMessage: bpy.props.StringProperty(name="Message", default="")

    loc_bApplyAnnotation: bpy.props.BoolProperty()

    bApplyAnnotation: bpy.props.BoolProperty(
        name="Apply Annotation",
        default=False,
        get=_GetUseAnnotation,
        set=_SetUseAnnotation,
    )

    bAutoUpdateAnnotation: bpy.props.BoolProperty(name="Auto Update Annotation", default=True)

    bEnableArmatureSelfOcclusion: bpy.props.BoolProperty(name="Armature Self-Occlusion", default=True)

    eAnnotationType: bpy.props.EnumProperty(
        items=[
            ("LABEL", "Label", "Apply label materials"),
            ("POS3D", "Pos3d", "Apply 3d position material"),
            ("LOCALPOS3D", "LocalPos3d", "Apply local 3d position material"),
            ("OBJIDX", "ObjectIdx", "Apply object index material")
            # ("OBJLOC3D", "ObjectLoc3d", "Apply object location material")
            # , ("MOVE", "Movement", "Apply movement material")
        ],
        default="LABEL",
        name="Annotation Type",
        description="Select the annotation type",
    )

    vOffsetPos3d: bpy.props.FloatVectorProperty(name="OffsetPos3d", default=(0.0, 0.0, 0.0), size=3)

    bImportFileExists: bpy.props.BoolProperty(name="Import File Exists", default=False, get=_ImportFileExists)

    sFilePathImport: bpy.props.StringProperty(
        name="Import File",
        description="Path to label types JSON configuration file",
        subtype="FILE_PATH",
        default="",
    )

    bExportFileExists: bpy.props.BoolProperty(name="Export File Exists", default=False, get=_ExportFileExists)

    bOverwriteExportApplied: bpy.props.BoolProperty(name="Overwrite")

    sFilePathExport: bpy.props.StringProperty(
        name="Export File",
        description="Path to applied types JSON configuration file export",
        subtype="FILE_PATH",
        default="",
    )

    # Store all available types
    clTypes: bpy.props.CollectionProperty(type=CPgAtLabelType)
    iTypeSelIdx: bpy.props.IntProperty(name="Selected Type Index", default=0)

    # Store object data that has to be restored when labelling is unapplied
    clObjectData: bpy.props.CollectionProperty(type=CPgAtObjectData)
    # Store objects that are ignored for labelling
    clIgnoreObjectData: bpy.props.CollectionProperty(type=CPgAtIgnoreObjectData)

    # Store original world shader id
    sWorldId: bpy.props.StringProperty(name="WorldId", default="")

    # Store all data that is applied
    clAppliedTypes: bpy.props.CollectionProperty(type=CPgAtLabelType)
    iAppliedTypeSelIdx: bpy.props.IntProperty(name="Selected Applied Type Index", default=0)
    iColorNormValue: bpy.props.IntProperty(name="Max. instantiation count", default=0)

    # Active Elements
    # sActiveObject: bpy.props.StringProperty(name="Active Object", default="")
    # sActiveCollection: bpy.props.StringProperty(name="Active Collection", default="")

    ##########################################################################
    @property
    def bSelectedTypeValid(self):
        return self.iTypeSelIdx >= 0 and self.iTypeSelIdx < len(self.clTypes)

    # enddef

    ##########################################################################
    @property
    def SelectedType(self):
        if not self.bSelectedTypeValid:
            return None
        # endif

        return self.clTypes[self.iTypeSelIdx]

    # enddef

    ##########################################################################
    def clear(self):
        self.loc_bApplyAnnotation = False
        self.sFilePathImport = ""

    # enddef


# endclass

###################################################################################
# Handler
@persistent
def AnyTruth_LabelSetInit(_xScene):
    CLabelSet(bpy.context.scene.xAtLabelSet).Init()


# enddef


@persistent
def AnyTruth_FrameChangePost(_xScene):
    xLabelSet = CLabelSet(bpy.context.scene.xAtLabelSet)
    if xLabelSet.bApplyAnnotation and xLabelSet.bAutoUpdateAnnotation:
        xLabelSet.UpdateLabelData3d()
    # endif


# enddef


@persistent
def AnyTruth_SavePre(_xScene):
    CLabelSet(bpy.context.scene.xAtLabelSet).ApplyAnnotation(False)


# enddef

###################################################################################
# Register


def register():

    at_prop_labeltype.register()
    at_prop_objdata.register()

    bpy.utils.register_class(CPgAtLabelSet)
    bpy.types.Scene.xAtLabelSet = bpy.props.PointerProperty(type=CPgAtLabelSet)

    # add handler if not in app.handlers
    if AnyTruth_LabelSetInit not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(AnyTruth_LabelSetInit)
    # endif

    # add handler if not in app.handlers
    if AnyTruth_FrameChangePost not in bpy.app.handlers.frame_change_post:
        bpy.app.handlers.frame_change_post.append(AnyTruth_FrameChangePost)
    # endif

    # add handler if not in app.handlers
    if AnyTruth_SavePre not in bpy.app.handlers.save_pre:
        bpy.app.handlers.save_pre.append(AnyTruth_SavePre)
    # endif

    # # add handler if not in app.handlers
    # if AnyTruth_LabelSetInit not in bpy.app.handlers.load_factory_startup_post:
    # 	bpy.app.handlers.load_factory_startup_post.append(AnyTruth_LabelSetInit)
    # # endif


# enddef


def unregister():

    # # remove handler if not in app.handlers
    # if AnyTruth_LabelSetInit in bpy.app.handlers.load_factory_startup_post:
    # 	bpy.app.handlers.load_factory_startup_post.remove(AnyTruth_LabelSetInit)
    # # endif

    # remove handler if not in app.handlers
    if AnyTruth_LabelSetInit in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(AnyTruth_LabelSetInit)
    # endif

    # remove handler if not in app.handlers
    if AnyTruth_FrameChangePost in bpy.app.handlers.frame_change_post:
        bpy.app.handlers.frame_change_post.remove(AnyTruth_FrameChangePost)
    # endif

    # remove handler if not in app.handlers
    if AnyTruth_SavePre not in bpy.app.handlers.save_pre:
        bpy.app.handlers.save_pre.remove(AnyTruth_SavePre)
    # endif

    bpy.utils.unregister_class(CPgAtLabelSet)
    at_prop_labeltype.unregister()
    at_prop_objdata.unregister()


# enddef
