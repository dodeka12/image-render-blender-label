#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \ops_labeldb.py
# Created Date: Thursday, May 20th 2021, 9:46:46 am
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
import os
from typing import Optional
from pathlib import Path

import anybase
import anybase.path
import anyblend
from anybase.cls_anyexcept import CAnyExcept
from .cls_prop_labelset import CLabelSet
from .at_prop_clnlab import CPgAtCollectionLabel
from .cls_anycam_config import CAnyCamConfig
from .node.shader.types import ELabelShaderTypes


############################################################################################################
def ImportLabelTypes(_xContext, _sPathTypes: str = None):
    xLabelSetProp = _xContext.scene.xAtLabelSet
    if xLabelSetProp is None:
        raise Exception("Label set data does not exist in scene")
    # endif

    xLabelSet = CLabelSet(xLabelSetProp)

    if isinstance(_sPathTypes, str):
        xLabelSet.sFilePathImport = _sPathTypes
    # endif

    xLabelSet.ImportTypes()


# enddef


############################################################################################################
def SetCollectionLabel(
    _xContext, *, sCollectionName, sLabelTypeId=None, bHasLabel=True, bIgnore=False, sChildrenInstanceType=None
):
    xScn = _xContext.scene
    if not hasattr(xScn, "xAtLabelSet"):
        raise Exception("AnyTruth add-on not installed in current blender instance")
    # endif
    xLabelSet = CLabelSet(xScn.xAtLabelSet)

    clnAct = anyblend.collection.GetCollection(sCollectionName)
    if clnAct is None:
        raise Exception("Collection '{0}' not available in scene".format(sCollectionName))
    # endif
    xLabel = clnAct.AnyTruth.xLabel

    lInstTypes = ["SINGLE", "INHERIT", "COLLECTION", "OBJECT"]
    if sChildrenInstanceType is not None and sChildrenInstanceType not in lInstTypes:
        raise Exception(
            "Invalid children instance type '{0}'. "
            "Has to be one of {{{1}}}.".format(sChildrenInstanceType, ", ".join(lInstTypes))
        )
    # endif

    if sLabelTypeId is not None:
        if not xLabelSet.HasLabelType(sLabelTypeId):
            raise Exception("Label type '{0}' not available in scene".format(sLabelTypeId))
        # endif

        xLabel.sType = sLabelTypeId
    # endif

    xLabel.bHasLabel = bHasLabel

    xLabel.bIgnore = bIgnore
    if sChildrenInstanceType is not None:
        xLabel.eChildrenInstanceType = sChildrenInstanceType
    # endif


# enddef


############################################################################################################
def CopyCollectionLabel(*, _sClnNameTrg: str, _sClnNameSrc: str, _xContext: Optional[bpy.types.Context] = None):
    xCtx: bpy.types.Context
    if _xContext is None:
        xCtx = bpy.context
    else:
        xCtx = _xContext
    # endif

    xScn = xCtx.scene
    if not hasattr(xScn, "xAtLabelSet"):
        raise Exception("AnyTruth add-on not installed in current blender instance")
    # endif
    # xLabelSet = CLabelSet(xScn.xAtLabelSet)

    clnSrc: bpy.types.Collection = anyblend.collection.GetCollection(_sClnNameSrc)
    if clnSrc is None:
        raise Exception("Source collection '{0}' not available in scene".format(_sClnNameSrc))
    # endif
    xLabelSrc: CPgAtCollectionLabel = clnSrc.AnyTruth.xLabel

    clnTrg: bpy.types.Collection = anyblend.collection.GetCollection(_sClnNameTrg)
    if clnTrg is None:
        raise Exception("Target collection '{0}' not available in scene".format(_sClnNameTrg))
    # endif
    xLabelTrg: CPgAtCollectionLabel = clnTrg.AnyTruth.xLabel

    xLabelTrg.bHasLabel = xLabelSrc.bHasLabel
    xLabelTrg.sType = xLabelSrc.sType
    xLabelTrg.bIgnore = xLabelSrc.bIgnore
    xLabelTrg.eChildrenInstanceType = xLabelSrc.eChildrenInstanceType


# enddef


############################################################################################################
def ApplyAnnotation(_xContext, _bApply, _sAnnotationType, *, _bEvalBoxes2d: bool = False):
    xLabelSetProp = _xContext.scene.xAtLabelSet
    if xLabelSetProp is None:
        raise CAnyExcept("Label set does not exist in scene")
    # endif

    if not CLabelSet.IsValidLabelType(_sAnnotationType):
        raise Exception("Annotation type '{0}' not supported".format(_sAnnotationType))
    # endif

    xLabelSet = CLabelSet(xLabelSetProp)
    xLabelSet.eAnnotationType = _sAnnotationType
    xLabelSet.ApplyAnnotation(_bApply, _bEvalBoxes2d=_bEvalBoxes2d)


# enddef


############################################################################################################
def UpdatePos3dOffset(_xContext):
    xLabelSetProp = _xContext.scene.xAtLabelSet
    if xLabelSetProp is None:
        raise CAnyExcept("Label set does not exist in scene")
    # endif

    xLabelSet = CLabelSet(xLabelSetProp)
    xLabelSet.UpdatePos3dOffset()


# enddef


############################################################################################################
def ApplyLabelRenderSettings(
    _xContext,
    *,
    sPathTrgMain,
    sAnnotationType,
    xCompFileOut=None,
    sFilename=None,
    bApplyFilePathsOnly=True,
    bEvalBoxes2d: bool = False,
):
    from anyblend.compositor.cls_fileout import CFileOut

    if not CLabelSet.IsValidLabelType(sAnnotationType):
        raise Exception("Annotation type '{0}' not supported".format(sAnnotationType))
    # endif

    xAnyCamConfig: CAnyCamConfig = None
    if bApplyFilePathsOnly is False:
        camAct: bpy.types.Object = bpy.context.scene.camera
        if camAct is None:
            raise RuntimeError("No camera activated in 'ApplyLabelRenderSettings()'")
        # endif
        xAnyCamConfig = CAnyCamConfig()
        xAnyCamConfig.FromCamera(bpy.context.scene.camera, _bDoRaise=False)
    # endif

    xScn = _xContext.scene
    xNT = xScn.node_tree
    lPathExport = []

    if sAnnotationType == "LABEL":
        # Render label as diffuse color render pass
        bpy.context.view_layer.use_pass_diffuse_color = True

        # Look for a label output node. If it does not exist, then create one
        # and connect it with the render layers "Image" output.
        nodOut = next((x for x in xNT.nodes if x.label == "Out:AT.Label.Raw:RGB"), None)
        if nodOut is None:
            nodOut = xNT.nodes.new(type="CompositorNodeBrightContrast")
            nodOut.label = "Out:AT.Label.Raw:RGB"
        # endif

        nodRL = next((x for x in xNT.nodes if x.name == "Render Layers"), None)
        if nodRL is None:
            raise Exception("Compositor does not contain 'Render Layers' node")
        # endif

        if bApplyFilePathsOnly is False:
            if xAnyCamConfig.eLabelShaderType == ELabelShaderTypes.DIFFUSE:
                xNT.links.new(nodRL.outputs["DiffCol"], nodOut.inputs["Image"])
            elif xAnyCamConfig.eLabelShaderType == ELabelShaderTypes.EMISSION:
                xNT.links.new(nodRL.outputs["Image"], nodOut.inputs["Image"])
            else:
                raise RuntimeError(f"Unsupported label shader type '{xAnyCamConfig.eLabelShaderType}'")
            # endif
        # endif

        if sFilename is None:
            sFilename = "Exp_#######"
        # endif
        sFolder = "AT_Label_Raw"
        lPathExport.append(os.path.normpath(os.path.join(sPathTrgMain, sFolder)))
        # sFpExport = os.path.join(sPathExport, "AnyTruth_Label_Raw.json")

        lFileOut = [
            {
                "sOutput": "AT.Label.Raw",
                "sFolder": sFolder,
                "sFilename": sFilename,
                "mFormat": {
                    "sFileFormat": "OPEN_EXR",
                    "sCodec": "ZIP",
                    "sColorDepth": "32",
                },
            }
        ]

    elif sAnnotationType == "POS3D":
        # Render label as diffuse color render pass
        bpy.context.view_layer.use_pass_diffuse_color = True

        # Look for a label output node. If it does not exist, then create one
        # and connect it with the render layers "Image" output.
        nodOut = next((x for x in xNT.nodes if x.label == "Out:AT.Pos3d.Raw:RGB"), None)
        if nodOut is None:
            nodOut = xNT.nodes.new(type="CompositorNodeBrightContrast")
            nodOut.label = "Out:AT.Pos3d.Raw:RGB"
        # endif

        nodRL = next((x for x in xNT.nodes if x.name == "Render Layers"), None)
        if nodRL is None:
            raise Exception("Compositor does not contain 'Render Layers' node")
        # endif

        if bApplyFilePathsOnly is False:
            if xAnyCamConfig.eLabelShaderType == ELabelShaderTypes.DIFFUSE:
                xNT.links.new(nodRL.outputs["DiffCol"], nodOut.inputs["Image"])
            elif xAnyCamConfig.eLabelShaderType == ELabelShaderTypes.EMISSION:
                xNT.links.new(nodRL.outputs["Image"], nodOut.inputs["Image"])
            else:
                raise RuntimeError(f"Unsupported label shader type '{xAnyCamConfig.eLabelShaderType}'")
            # endif
        # endif

        # # HACK ###
        # # Output flow together with Pos3d using Blender's flow output.
        # # This won't work for poly or lft cameras
        # bpy.context.view_layer.use_pass_vector = True

        # nodOut = next((x for x in xNT.nodes if x.label == "Out:AT.Flow.Raw:RGBA"), None)
        # if nodOut is None:
        #     nodOut = xNT.nodes.new(type="CompositorNodeBrightContrast")
        #     nodOut.label = "Out:AT.Flow.Raw:RGBA"
        # # endif

        # nodRL = next((x for x in xNT.nodes if x.name == "Render Layers"), None)
        # if nodRL is None:
        #     raise Exception("Compositor does not contain 'Render Layers' node")
        # # endif

        # xNT.links.new(nodRL.outputs["Vector"], nodOut.inputs["Image"])

        if sFilename is None:
            sFilename = "Exp_#######"
        # endif
        sFolderLoc3d = "AT_Pos3d_Raw"
        # sFolderFlow = "AT_Flow_Raw"
        lPathExport.append(os.path.normpath(os.path.join(sPathTrgMain, sFolderLoc3d)))
        # lPathExport.append(os.path.normpath(os.path.join(sPathTrgMain, sFolderFlow)))
        # sFpExportPos3d = os.path.join(sPathExportPos3d, "AnyTruth_Pos3d_Raw.json")

        lFileOut = [
            {
                "sOutput": "AT.Pos3d.Raw",
                "sFolder": sFolderLoc3d,
                "sFilename": sFilename,
                "mFormat": {
                    "sFileFormat": "OPEN_EXR",
                    "sCodec": "ZIP",
                    "sColorDepth": "32",
                },
            },
            # {
            #     "sOutput": "AT.Flow.Raw",
            #     "sFolder": sFolderFlow,
            #     "sFilename": sFilename,
            #     "mFormat": {
            #         "sFileFormat": "OPEN_EXR",
            #         "sCodec": "ZIP",
            #         "sColorDepth": "32",
            #     },
            # },
        ]

    elif sAnnotationType == "LOCALPOS3D":
        # Render label as diffuse color render pass
        bpy.context.view_layer.use_pass_diffuse_color = True

        # Look for a label output node. If it does not exist, then create one
        # and connect it with the render layers "Image" output.
        nodOut = next((x for x in xNT.nodes if x.label == "Out:AT.LocalPos3d.Raw:RGB"), None)
        if nodOut is None:
            nodOut = xNT.nodes.new(type="CompositorNodeBrightContrast")
            nodOut.label = "Out:AT.LocalPos3d.Raw:RGB"
        # endif

        nodRL = next((x for x in xNT.nodes if x.name == "Render Layers"), None)
        if nodRL is None:
            raise Exception("Compositor does not contain 'Render Layers' node")
        # endif

        if bApplyFilePathsOnly is False:
            if xAnyCamConfig.eLabelShaderType == ELabelShaderTypes.DIFFUSE:
                xNT.links.new(nodRL.outputs["DiffCol"], nodOut.inputs["Image"])
            elif xAnyCamConfig.eLabelShaderType == ELabelShaderTypes.EMISSION:
                xNT.links.new(nodRL.outputs["Image"], nodOut.inputs["Image"])
            else:
                raise RuntimeError(f"Unsupported label shader type '{xAnyCamConfig.eLabelShaderType}'")
            # endif
        # endif

        if sFilename is None:
            sFilename = "Exp_#######"
        # endif
        sFolderLoc3d = "AT_LocalPos3d_Raw"
        lPathExport.append(os.path.normpath(os.path.join(sPathTrgMain, sFolderLoc3d)))
        # sFpExportPos3d = os.path.join(sPathExportPos3d, "AnyTruth_Pos3d_Raw.json")

        lFileOut = [
            {
                "sOutput": "AT.LocalPos3d.Raw",
                "sFolder": sFolderLoc3d,
                "sFilename": sFilename,
                "mFormat": {
                    "sFileFormat": "OPEN_EXR",
                    "sCodec": "ZIP",
                    "sColorDepth": "32",
                },
            }
        ]

    elif sAnnotationType == "OBJIDX":
        # Render label as diffuse color render pass
        bpy.context.view_layer.use_pass_diffuse_color = True

        # Look for a label output node. If it does not exist, then create one
        # and connect it with the render layers "Image" output.
        nodOut = next((x for x in xNT.nodes if x.label == "Out:AT.ObjIdx.Raw:RGB"), None)
        if nodOut is None:
            nodOut = xNT.nodes.new(type="CompositorNodeBrightContrast")
            nodOut.label = "Out:AT.ObjIdx.Raw:RGB"
        # endif

        nodRL = next((x for x in xNT.nodes if x.name == "Render Layers"), None)
        if nodRL is None:
            raise Exception("Compositor does not contain 'Render Layers' node")
        # endif

        if bApplyFilePathsOnly is False:
            if xAnyCamConfig.eLabelShaderType == ELabelShaderTypes.DIFFUSE:
                xNT.links.new(nodRL.outputs["DiffCol"], nodOut.inputs["Image"])
            elif xAnyCamConfig.eLabelShaderType == ELabelShaderTypes.EMISSION:
                xNT.links.new(nodRL.outputs["Image"], nodOut.inputs["Image"])
            else:
                raise RuntimeError(f"Unsupported label shader type '{xAnyCamConfig.eLabelShaderType}'")
            # endif
        # endif

        if sFilename is None:
            sFilename = "Exp_#######"
        # endif
        sFolderLoc3d = "AT_ObjectIdx_Raw"
        lPathExport.append(os.path.normpath(os.path.join(sPathTrgMain, sFolderLoc3d)))
        # sFpExportPos3d = os.path.join(sPathExportPos3d, "AnyTruth_Pos3d_Raw.json")

        lFileOut = [
            {
                "sOutput": "AT.ObjIdx.Raw",
                "sFolder": sFolderLoc3d,
                "sFilename": sFilename,
                "mFormat": {
                    "sFileFormat": "OPEN_EXR",
                    "sCodec": "ZIP",
                    "sColorDepth": "32",
                },
            }
        ]

    elif sAnnotationType == "OBJLOC3D":
        # Render label as diffuse color render pass
        bpy.context.view_layer.use_pass_diffuse_color = True

        # Look for a label output node. If it does not exist, then create one
        # and connect it with the render layers "Image" output.
        nodOut = next((x for x in xNT.nodes if x.label == "Out:AT.ObjLoc3d.Raw:RGB"), None)
        if nodOut is None:
            nodOut = xNT.nodes.new(type="CompositorNodeBrightContrast")
            nodOut.label = "Out:AT.ObjLoc3d.Raw:RGB"
        # endif

        nodRL = next((x for x in xNT.nodes if x.name == "Render Layers"), None)
        if nodRL is None:
            raise Exception("Compositor does not contain 'Render Layers' node")
        # endif

        if bApplyFilePathsOnly is False:
            if xAnyCamConfig.eLabelShaderType == ELabelShaderTypes.DIFFUSE:
                xNT.links.new(nodRL.outputs["DiffCol"], nodOut.inputs["Image"])
            elif xAnyCamConfig.eLabelShaderType == ELabelShaderTypes.EMISSION:
                xNT.links.new(nodRL.outputs["Image"], nodOut.inputs["Image"])
            else:
                raise RuntimeError(f"Unsupported label shader type '{xAnyCamConfig.eLabelShaderType}'")
            # endif
        # endif

        if sFilename is None:
            sFilename = "Exp_#######"
        # endif
        sFolderLoc3d = "AT_ObjectLoc3d_Raw"
        lPathExport.append(os.path.normpath(os.path.join(sPathTrgMain, sFolderLoc3d)))
        # sFpExportPos3d = os.path.join(sPathExportPos3d, "AnyTruth_Pos3d_Raw.json")

        lFileOut = [
            {
                "sOutput": "AT.ObjLoc3d.Raw",
                "sFolder": sFolderLoc3d,
                "sFilename": sFilename,
                "mFormat": {
                    "sFileFormat": "OPEN_EXR",
                    "sCodec": "ZIP",
                    "sColorDepth": "32",
                },
            }
        ]

    else:
        raise Exception("Invalid annotation type")
    # endif

    if xCompFileOut is None:
        xCompFileOut = CFileOut(xScn)
    else:
        xCompFileOut.UpdateOutputs()
    # endif

    # Apply file out config to compositor
    xCompFileOut.SetFileOut(sPathTrgMain, lFileOut)

    if bApplyFilePathsOnly is False:
        # Apply the label materials
        ApplyAnnotation(_xContext, True, sAnnotationType, _bEvalBoxes2d=bEvalBoxes2d)

        for sPathExport in lPathExport:
            if not os.path.exists(sPathExport):
                anybase.path.CreateDir(sPathExport)
            # endif
        # endfor

        anyblend.viewlayer.Update()
    # endif

    return xCompFileOut


# enddef


############################################################################################################
def ExportAppliedLabelTypes(
    _xContext,
    _sFpExport,
    *,
    bOverwrite=False,
    bUpdateLabelData3d: bool = True,
    bEvalBoxes2d: bool = False,
    _pathExData: Path = None,
):
    # ## DEBUG
    # print("ExportAppliedLabelTypes", flush=True)
    # ##########

    xLabelSetProp = _xContext.scene.xAtLabelSet
    if xLabelSetProp is None:
        raise CAnyExcept("Label set does not exist in scene")
    # endif

    xLabelSet = CLabelSet(xLabelSetProp)
    if bUpdateLabelData3d is True:
        xLabelSet.UpdateLabelData3d(bDrawData=False, bEvalBoxes2d=bEvalBoxes2d)
    # endif
    xLabelSet.sFilePathExport = _sFpExport
    xLabelSet.bOverwriteExportApplied = bOverwrite
    xLabelSet.ExportAppliedTypes(_pathExData=_pathExData)


# enddef


############################################################################################################
def GetOffsetPos3d(_xContext: Optional[bpy.types.Context] = None) -> list:
    xCtx: bpy.types.Context = None

    if _xContext is None:
        xCtx = bpy.context
    else:
        xCtx = _xContext
    # endif

    xLabelSetProp = xCtx.scene.xAtLabelSet
    if xLabelSetProp is None:
        raise CAnyExcept("Label set does not exist in scene")
    # endif

    xLabelSet = CLabelSet(xLabelSetProp)
    return list(xLabelSet.vOffsetPos3d)


# enddef


############################################################################################################
def ExportPos3dInfo(_xContext, _sFpExport, bOverwrite=False):
    xLabelSetProp = _xContext.scene.xAtLabelSet
    if xLabelSetProp is None:
        raise CAnyExcept("Label set does not exist in scene")
    # endif

    xLabelSet = CLabelSet(xLabelSetProp)
    xLabelSet.sFilePathExport = _sFpExport
    xLabelSet.bOverwriteExportApplied = bOverwrite
    xLabelSet.ExportPos3dInfo()


# enddef


############################################################################################################
def EnableAutoUpdateAnnotation(_xContext, _bEnable=True):
    xLabelSetProp = _xContext.scene.xAtLabelSet
    if xLabelSetProp is None:
        raise CAnyExcept("Label set does not exist in scene")
    # endif

    xLabelSet = CLabelSet(xLabelSetProp)
    xLabelSet.bAutoUpdateAnnotation = _bEnable


# enddef
