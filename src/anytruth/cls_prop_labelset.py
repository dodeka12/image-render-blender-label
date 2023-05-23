#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \cls_labeldata.py
# Created Date: Tuesday, May 25th 2021, 2:33:54 pm
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
import mathutils

import sys
from typing import Union, Callable

# import inspect

if sys.version_info < (3, 10):
    import importlib_resources as res
else:
    from importlib import resources as res
# endif

import re

import os
import pyjson5 as json
from pathlib import Path
import numpy as np

import anybase
import anybase.path
import anybase.config
import anyblend

from anyblend.cls_boundbox import CBoundingBox
from anyblend.util.node import GetByLabelOrId as GetNodeByLabelOrId

import anycam
from anycam.obj.camera_lut import StoreLutCameraData

from anybase.cls_any_error import CAnyError_Message
from anybase.cls_anycml import CAnyCML

from .material.cls_label import CLabel
from .material.cls_label_skeleton import CLabelSkeleton
from .material.cls_pos3d import CPos3d
from .material.cls_pos3d import CreateName as CreateNameMaterialPos3d
from .material.cls_local_pos3d import CLocalPos3d
from .material.cls_object_idx import CObjectIdx
from .material.cls_object_loc3d import CObjectLoc3d

from .object import armature
from . import node
from .node.shader.types import ELabelShaderTypes
from .cls_anycam_config import CAnyCamConfig

import anytruth

c_dicArmatureBoneLabelWeights = {}


class CLabelInstance:
    def __init__(self, *, _sTopObj: str, _sOrientObj: str, _lValidObjects: list[str]):
        self._sTopObj: str = _sTopObj
        self._sOrientObj: str = _sOrientObj
        self._lValidObjects: list[str] = _lValidObjects.copy()

    # enddef

    @property
    def sTopObj(self):
        return self._sTopObj

    # enddef

    @property
    def sOrientObj(self):
        return self._sOrientObj

    # enddef

    @property
    def lValidObjects(self):
        return self._lValidObjects

    # enddef

    @property
    def objTop(self):
        objX = bpy.data.objects.get(self._sTopObj)
        if objX is None:
            raise RuntimeError(f"Object '{self._sTopObj}' not available")
        # endif
        return objX

    # enddef

    @property
    def sType(self):
        return self.objTop.type

    # enddef


# endclass


###################################################################################
# This class defines the functions for the property group CPgAtLabelSet.
# The functions are not directly members of CPgAtLabelSet, make them usable
# even if the AnyTruth add-on is not installed. This can be the case,
# when the functions are called from Catharsys. In this case, only the data of
# CPgAtLabelSet stored in the Blender file is used. If we use member functions
# of the property group class, it tries to access the functions of the installed addon.
# However, I want to be able to use Catharsys on systems where not all addons are installed.
class CLabelSet:
    def __init__(self, _xLabelSetProp):
        self.xLabelSetProp = _xLabelSetProp

        # Default label shader type
        self.xAnyCamConfig: CAnyCamConfig = CAnyCamConfig()

    # enddef

    dicUserLabelMaterial: dict = {}
    # dicArmatureBoneLabelWeights: dict = {}

    reAtMat: re.Pattern = re.compile(r"^.+;AT\.Label\.(.+)$")
    reAtNode: re.Pattern = re.compile(r"^AT\.Label\.(.+)$")
    reAtOrient: re.Pattern = re.compile(r"^.+;AT\.Label\.Instance\.Orientation$")
    reAtBone: re.Pattern = re.compile(r"^AT\.Label;(?P<skel>.+);(?P<bone>.+)")
    reAtVexGrp: re.Pattern = re.compile(
        r"^AT\.Label;(?P<type>[^;]+);(?P<inst>\d+);(?P<id>[^;]+);(?P<vextype>\w+);" r"(?P<r>\d+);(?P<g>\d+);(?P<b>\d+)$"
    )

    _lAllowedInstTypes: list[str] = ["MESH", "ARMATURE"]
    _lAllowedLabelTypes: list[str] = ["LABEL", "POS3D", "LOCALPOS3D", "OBJIDX", "OBJLOC3D"]

    dicInstInc: dict = {
        "NONE": {
            "NONE": (0, 0),
            "SINGLE": (1, 0),
            "COLLECTION": (1, 0),
            "OBJECT": (1, 1),
        },
        "SINGLE": {
            "NONE": (0, 0),
            "SINGLE": (0, 0),
            "COLLECTION": (1, 0),
            "OBJECT": (1, 1),
        },
        "COLLECTION": {
            "NONE": (1, 0),
            "SINGLE": (1, 0),
            "COLLECTION": (1, 0),
            "OBJECT": (1, 1),
        },
        "OBJECT": {
            "NONE": (1, 1),
            "SINGLE": (1, 0),
            "COLLECTION": (1, 0),
            "OBJECT": (1, 1),
        },
    }

    @classmethod
    def GetAllowedLabelTypes(cls):
        return cls._lAllowedLabelTypes.copy()

    # enddef

    @classmethod
    def IsValidLabelType(cls, _sType: str):
        return _sType in cls._lAllowedLabelTypes

    # enddef

    @property
    def clTypes(self):
        return self.xLabelSetProp.clTypes

    # enddef

    @property
    def clAppliedTypes(self):
        return self.xLabelSetProp.clAppliedTypes

    # enddef

    @property
    def clObjectData(self):
        return self.xLabelSetProp.clObjectData

    # enddef

    @property
    def clIgnoreObjectData(self):
        return self.xLabelSetProp.clIgnoreObjectData

    # enddef

    @property
    def iColorNormValue(self):
        return self.xLabelSetProp.iColorNormValue

    # enddef

    @iColorNormValue.setter
    def iColorNormValue(self, iValue):
        self.xLabelSetProp.iColorNormValue = iValue

    # enddef

    @property
    def bAutoUpdateAnnotation(self):
        return self.xLabelSetProp.bAutoUpdateAnnotation

    # enddef

    @bAutoUpdateAnnotation.setter
    def bAutoUpdateAnnotation(self, _bValue: bool):
        self.xLabelSetProp.bAutoUpdateAnnotation = _bValue

    # enddef

    @property
    def bEnableArmatureSelfOcclusion(self):
        return self.xLabelSetProp.bEnableArmatureSelfOcclusion

    # enddef

    @bEnableArmatureSelfOcclusion.setter
    def bEnableArmatureSelfOcclusion(self, _bValue: bool):
        self.xLabelSetProp.bEnableArmatureSelfOcclusion = _bValue

    # enddef

    @property
    def bApplyAnnotation(self):
        return self.xLabelSetProp.loc_bApplyAnnotation

    # enddef

    @property
    def loc_bApplyAnnotation(self):
        return self.xLabelSetProp.loc_bApplyAnnotation

    # enddef

    @loc_bApplyAnnotation.setter
    def loc_bApplyAnnotation(self, bValue):
        self.xLabelSetProp.loc_bApplyAnnotation = bValue

    # enddef

    @property
    def eAnnotationType(self):
        return self.xLabelSetProp.eAnnotationType

    # enddef

    @eAnnotationType.setter
    def eAnnotationType(self, sValue):
        self.xLabelSetProp.eAnnotationType = sValue

    # enddef

    @property
    def iAppliedTypeSelIdx(self):
        return self.xLabelSetProp.iAppliedTypeSelIdx

    # enddef

    @iAppliedTypeSelIdx.setter
    def iAppliedTypeSelIdx(self, iValue):
        self.xLabelSetProp.iAppliedTypeSelIdx = iValue

    # enddef

    @property
    def sFilePathImport(self):
        return self.xLabelSetProp.sFilePathImport

    # enddef

    @sFilePathImport.setter
    def sFilePathImport(self, sValue):
        self.xLabelSetProp.sFilePathImport = sValue

    # enddef

    @property
    def sFilePathExport(self):
        return self.xLabelSetProp.sFilePathExport

    # enddef

    @sFilePathExport.setter
    def sFilePathExport(self, sValue):
        self.xLabelSetProp.sFilePathExport = sValue

    # enddef

    @property
    def bImportFileExists(self):
        return self.xLabelSetProp.bImportFileExists

    # enddef

    @property
    def bExportFileExists(self):
        return self.xLabelSetProp.bExportFileExists

    # enddef

    @property
    def bOverwriteExportApplied(self):
        return self.xLabelSetProp.bOverwriteExportApplied

    # enddef

    @bOverwriteExportApplied.setter
    def bOverwriteExportApplied(self, bValue):
        self.xLabelSetProp.bOverwriteExportApplied = bValue

    # enddef

    @property
    def dicArmatureBoneLabelWeights(self):
        global c_dicArmatureBoneLabelWeights
        return c_dicArmatureBoneLabelWeights

    # enddef

    @property
    def vOffsetPos3d(self):
        return self.xLabelSetProp.vOffsetPos3d

    # enddef

    @vOffsetPos3d.setter
    def vOffsetPos3d(self, tOffset: tuple[float, float, float]):
        self.xLabelSetProp.vOffsetPos3d = tOffset

    # enddef

    ##########################################################################
    def Print(self, _sText):
        print("anytruth: {}".format(_sText), flush=True)

    # endif

    ##########################################################################
    def HasLabelType(self, _sType):
        return any(x.sId == _sType for x in self.clTypes)

    # enddef

    ##########################################################################
    def ApplyAnnotation(self, _bApply, *, _bEvalBoxes2d: bool = False):
        if _bApply == self.loc_bApplyAnnotation:
            return
        # endif

        if _bApply is True:
            if self.eAnnotationType == "LABEL":
                self.ApplyLabel()
            elif self.eAnnotationType == "POS3D":
                self.ApplyPos3d()
            elif self.eAnnotationType == "LOCALPOS3D":
                self.ApplyLocalPos3d()
            elif self.eAnnotationType == "OBJIDX":
                self.ApplyObjectIdx()
            elif self.eAnnotationType == "OBJLOC3D":
                self.ApplyObjectLoc3d()
            else:
                raise Exception("Annotation type '{0}' not supported".format(self.eAnnotationType))
            # endif

        else:
            self.Restore()
        # endif

        self.loc_bApplyAnnotation = _bApply
        if _bApply is True and self.eAnnotationType == "LABEL":
            self.UpdateLabelData3d(bEvalBoxes2d=_bEvalBoxes2d)
        # endif

    # enddef

    ##########################################################################
    def UpdateLabelData3d(self, *, bDrawData=True, bEvalBoxes2d=False):
        if not self.loc_bApplyAnnotation:
            return
        # endif

        # ## DEBUG
        # print(f"UpdateLabelData3d(): Called from '{(inspect.stack()[1].function)}'")
        # ###########

        self.Print("UpdateLabelData3d() start")

        self.Print("UpdateLabelData3d->EvalPoses() start")
        self.EvalPoses()

        if bEvalBoxes2d is True:
            self.Print("UpdateLabelData3d->EvalBoxes2d() start")
            self.EvalBoxes2d()
        # endif

        self.Print("UpdateLabelData3d->EvalBoxes3d() start")
        self.EvalBoxes3d()

        self.Print("UpdateLabelData3d->EvalVertexLists3d() start")
        self.EvalVertexLists3d()

        if bDrawData:
            self.Print("UpdateLabelData3d->CreateBoxes3d() start")
            self.CreateBoxes3d()

            self.Print("UpdateLabelData3d->CreatePoses() start")
            self.CreatePoses()

            self.Print("UpdateLabelData3d->CreateVertexGroups() start")
            self.CreateVertexGroups()
        # endif

        self.Print("UpdateLabelData3d() finished")

    # enddef

    ###################################################################################
    def _PrepareCameraForLabeling(self):
        ##########################################################################################
        # Check for settings by AnyCam Camera
        if self.xAnyCamConfig.FromCamera(bpy.context.scene.camera, _bDoRaise=False) is True:
            if self.xAnyCamConfig.eLabelShaderType == ELabelShaderTypes.EMISSION:
                self.Print("_IgnoreAllLights() start")
                self._IgnoreAllLights()
            # endif

            self.xAnyCamConfig.EnableLabeling(True)
        # endif

    # enddef

    ###################################################################################
    def _RestoreCameraFromLabeling(self):
        if self.xAnyCamConfig.FromCamera(bpy.context.scene.camera, _bDoRaise=False) is True:
            self.xAnyCamConfig.EnableLabeling(False)
        # endif

    # enddef

    ###################################################################################
    def ApplyPos3d(self):
        self._PrepareCameraForLabeling()

        lObjects = [
            x
            for x in bpy.context.scene.objects
            if ((x.type == "MESH" or x.type == "ARMATURE") and x.hide_render is False)
        ]

        boxAll = CBoundingBox(_lObjects=lObjects, _bLocal=False, _bCompoundObject=False, _bUseMesh=False)

        tOffset = tuple(-x for x in boxAll.vCornerMin)
        self.vOffsetPos3d = tOffset

        # Create Material
        xMatPos3d = CPos3d(
            sName="Default",
            tOffset=tOffset,
            eLabelShaderType=self.xAnyCamConfig.eLabelShaderType,
            bForce=True,
        )

        matPos3d = xMatPos3d.xMaterial

        # Apply Material
        self.ApplyMaterial(matObject=matPos3d, sBgName="AT.Pos3d", tBgColor=(0, 0, 0, 0), fBgStrength=1.0)
        # self.ApplyMaterial(matObject=matPos3d, sBgName="AT.Pos3d", tBgColor=(1e6, 1e6, 1e6, 1), fBgStrength=1.0)

    # enddef

    ###################################################################################
    def UpdatePos3dOffset(self):
        lObjects = [
            x
            for x in bpy.context.scene.objects
            if ((x.type == "MESH" or x.type == "ARMATURE") and x.hide_render is False)
        ]

        boxAll = CBoundingBox(_lObjects=lObjects, _bLocal=False, _bCompoundObject=False, _bUseMesh=False)

        tOffset = tuple(-x for x in boxAll.vCornerMin)
        self.vOffsetPos3d = tOffset

        sMatName = CreateNameMaterialPos3d("Default")
        matPos3d = bpy.data.materials.get(sMatName)
        if matPos3d is None:
            raise RuntimeError(f"Pos3d material '{sMatName}' not found")
        # endif

        nodOffset = GetNodeByLabelOrId(matPos3d.node_tree, "Add Offset")
        nodOffset.inputs[1].default_value = tOffset

    # enddef

    ###################################################################################
    def ApplyLocalPos3d(self):
        bSphericalCS: bool = False

        self._PrepareCameraForLabeling()

        # Create Material
        xMatLocalPos = CLocalPos3d(
            sName="Default",
            bSphericalCS=bSphericalCS,
            xOffset="Offset",
            eLabelShaderType=self.xAnyCamConfig.eLabelShaderType,
            bForce=True,
        )
        matLocalPos = xMatLocalPos.xMaterial

        def _SetOffset(objX: bpy.types.Object):
            objX["Offset"] = [-min([pos[i] for pos in objX.bound_box]) for i in range(3)]

        # enddef

        # Apply Material
        self.ApplyMaterial(
            matObject=matLocalPos,
            sBgName="AT.LocalPos3d",
            tBgColor=(1e9, 1e9, 1e9, 1),
            fBgStrength=1.0,
            funcPerObject=_SetOffset if bSphericalCS is False else None,
        )

    # enddef

    ###################################################################################
    def ApplyObjectIdx(self):
        self._PrepareCameraForLabeling()

        # Create Material
        xMatLocalPos = CObjectIdx(sName="Default", eLabelShaderType=self.xAnyCamConfig.eLabelShaderType, bForce=True)
        matLocalPos = xMatLocalPos.xMaterial

        # Apply Material
        self.ApplyMaterial(matObject=matLocalPos, sBgName="AT.ObjectIdx", tBgColor=(1e9, 1e9, 1e9, 1), fBgStrength=1.0)

    # enddef

    ###################################################################################
    def ApplyObjectLoc3d(self):
        self._PrepareCameraForLabeling()

        # Create Material
        xMatLocalPos = CObjectLoc3d(
            sName="Default", tOffset=(1e4, 1e4, 1e4), eLabelShaderType=self.xAnyCamConfig.eLabelShaderType, bForce=True
        )
        matLocalPos = xMatLocalPos.xMaterial

        # Apply Material
        self.ApplyMaterial(
            matObject=matLocalPos, sBgName="AT.ObjectLoc3d", tBgColor=(1e9, 1e9, 1e9, 1), fBgStrength=1.0
        )

    # enddef

    ###################################################################################
    def ApplyMaterial(
        self,
        *,
        sBgName: str,
        tBgColor: Union[list, tuple[float, float, float, float]],
        fBgStrength: float = 1.0,
        matObject: bpy.types.Material = None,
        funcCreateMaterial: Callable[["CLabelSet"], bpy.types.Material] = None,
        funcPerObject: Callable[[bpy.types.Object], None] = None,
    ):
        clRoot = anyblend.collection.GetRootCollection(bpy.context)
        self.clObjectData.clear()

        # Add None type to applied types with single instance
        # lNames = [x.name for x in self.clTypes]
        xTypeNone = self.clTypes.get("None")
        if xTypeNone is None:
            raise Exception("No labeltype 'None' defined")
        # endif
        self.clAppliedTypes.clear()
        xAppType = self.clAppliedTypes.add()
        xAppType.sId = xAppType.name = xTypeNone.sId
        xAppType.colLabel = xTypeNone.colLabel

        ##########################################################################################
        # Add label data from scene
        self._AddLabelData(clRoot, "NONE", "None", None, None)

        if matObject is None and funcCreateMaterial is not None:
            matObject = funcCreateMaterial(self)
        elif matObject is None and funcCreateMaterial is None:
            raise RuntimeError("None of the arguments 'matObject' or 'funcCreateMaterial' is given")
        # endif

        # Set materials and pass index of objects
        iObjIdx: int = 1
        for xObjData in self.clObjectData:
            objX = bpy.data.objects.get(xObjData.sId)
            objX.pass_index = iObjIdx
            # Need to ensure that object is not regarded as shadow catcher.
            # Otherwise material colors are multiplied by 2 by Blender internally!?
            objX.is_shadow_catcher = False

            if funcPerObject is not None:
                funcPerObject(objX)
            # endif

            for xMesh in xObjData.clMeshes:
                sMeshId = xMesh.sId
                mshX = bpy.data.meshes[sMeshId]
                iMatCnt = len(mshX.materials)
                # Switch off LOD as workaround for problems with Grasswald.
                # I cannot find bug where LOD objects are not switched to
                # render LOD.
                # The LOD feature has been removed in Blender 2.93
                if bpy.app.version <= (2, 84, 0):
                    mshX.lod_enabled = False

                if iMatCnt == 0:
                    mshX.materials.append(matObject)
                else:
                    for iMatIdx in range(iMatCnt):
                        matX = mshX.materials[iMatIdx]
                        if matX is not None:
                            matX.use_fake_user = True
                            mshX.materials[iMatIdx] = matObject
                        else:
                            mshX.materials[iMatIdx] = matObject
                        # endif

                    # endfor materials
                # endfor
            # endfor meshes

            iObjIdx += 1
        # endfor objects

        #######################################################################
        # Replace world shader with label shader

        # Get currently selected world
        worldAct = bpy.context.scene.world
        if worldAct is None:
            raise Exception("Scene has no world shader set")
        # endif

        # Store current world id
        self.xLabelSetProp.sWorldId = worldAct.name

        # Look for "AT.Label" world
        worldATD = bpy.data.worlds.get(sBgName)
        if worldATD is None:
            # Create the label world shader
            worldATD = bpy.data.worlds.new(name=sBgName)
            worldATD.use_nodes = True

            nodBg = worldATD.node_tree.nodes.get("Background")
            if nodBg is None:
                raise Exception("Newly created world shader does not contain 'Background' node")
            # endif

            nodBg.use_custom_color = True
            nodBg.inputs["Color"].default_value = tBgColor
            nodBg.inputs["Strength"].default_value = fBgStrength
        # endif

        # Set AT.Label shader as world shader
        bpy.context.scene.world = worldATD

    # enddef

    ###################################################################################
    def _CollectUserMaterials(self):
        # Collect all available user defined label materials
        # for the currently available types
        for matX in bpy.data.materials:
            sMatId = matX.name
            xMatch = self.reAtMat.match(sMatId)
            if xMatch is not None:
                sTypeId = xMatch.group(1)
                if sTypeId in self.clTypes:
                    lShaderTypes = []
                    iShaderMaxInstCnt = 1
                    for nodX in matX.node_tree.nodes:
                        if nodX.type != "VALUE":
                            continue
                        # endif

                        if nodX.label == "AT.MaxInstCount":
                            iShaderMaxInstCnt = int(round(nodX.outputs[0].default_value))
                            continue
                        # endif

                        xMatchNode = self.reAtNode.match(nodX.label)
                        if xMatchNode is None:
                            continue
                        # endif

                        sShaderType = xMatchNode.group(1)
                        if sShaderType not in self.clTypes:
                            continue
                        # endif

                        lShaderTypes.append(sShaderType)
                    # endfor

                    self.dicUserLabelMaterial[sMatId] = {
                        "sTypeId": sTypeId,
                        "lShaderTypes": lShaderTypes,
                        "iShaderMaxInstCnt": iShaderMaxInstCnt,
                    }
                # endif
            # endif
        # endfor

    # enddef

    ###################################################################################
    def _PrepareUserMaterials(self):
        lTypeIds = [x.sId for x in self.clAppliedTypes]

        for sUserMatId in self.dicUserLabelMaterial:
            dicUserMat = self.dicUserLabelMaterial.get(sUserMatId)
            sLabelType = dicUserMat.get("sTypeId")
            xActAppType = self.clAppliedTypes.get(sLabelType)
            if xActAppType is None:
                continue
            # endif

            lOverallShaderTypes = [x.sId for x in xActAppType.clShaderTypes]
            iTotalShaderTypeCount = len(lOverallShaderTypes)
            iLabelTypeId = lTypeIds.index(sLabelType)
            matX = bpy.data.materials.get(sUserMatId)
            matX.pass_index = iLabelTypeId
            for nodX in matX.node_tree.nodes:
                if nodX.type != "VALUE":
                    continue
                # endif

                if nodX.label == "AT.TypeCount":
                    nodX.outputs[0].default_value = iTotalShaderTypeCount
                    continue
                # endif

                # Set maximal instance count of all user defined materials for
                # this object label type
                if nodX.label == "AT.MaxInstCount":
                    nodX.outputs[0].default_value = xActAppType.iShaderMaxInstCnt
                # endif

                xMatchNode = self.reAtNode.match(nodX.label)
                if xMatchNode is None:
                    continue
                # endif

                sShaderType = xMatchNode.group(1)
                if sShaderType not in xActAppType.clShaderTypes:
                    continue
                # endif

                iShaderTypeIdx = lOverallShaderTypes.index(sShaderType)
                nodX.outputs[0].default_value = iShaderTypeIdx
            # endfor
        # endfor

    # enddef

    ###################################################################################
    def _GetBlenderToCustomWorldMatrix(self):
        objOrig = bpy.data.objects.get("AT.Label.Orig.World")
        if objOrig is None:
            return mathutils.Matrix.Identity(4)
        else:
            return objOrig.matrix_world.inverted()
        # endif

    # enddef

    ###################################################################################
    def _IgnoreAllLights(self):
        lLights = [x for x in bpy.data.objects if x.type == "LIGHT"]

        for objL in lLights:
            xIgnObjData = self.clIgnoreObjectData.add()
            xIgnObjData.sId = xIgnObjData.name = objL.name
            xIgnObjData.bHideRender = objL.hide_render
            xIgnObjData.bHideViewport = objL.hide_get()
            anyblend.object.Hide(objL, bHide=True, bHideRender=True)
        # endfor

    # enddef

    ###################################################################################
    def ApplyLabel(self):
        global c_dicArmatureBoneLabelWeights

        self.Print("ApplyLabel() start")
        clRoot = anyblend.collection.GetRootCollection(bpy.context)

        self.clObjectData.clear()
        self.dicUserLabelMaterial = {}
        c_dicArmatureBoneLabelWeights = {}

        # Add None type to applied types with single instance
        # lNames = [x.name for x in self.clTypes]
        xTypeNone = self.clTypes.get("None")
        if xTypeNone is None:
            print("{}".format([x.sId for x in self.clTypes.keys()]))
            raise Exception("No labeltype 'None' defined")
        # endif
        self.clAppliedTypes.clear()
        xAppType = self.clAppliedTypes.add()
        xAppType.sId = xAppType.name = xTypeNone.sId
        xAppType.colLabel = xTypeNone.colLabel

        self._PrepareCameraForLabeling()

        ##########################################################################################
        self.Print("CollectUserMaterials() start")
        self._CollectUserMaterials()

        ##########################################################################################
        # Add label data from scene
        self.Print("_AddLabelData() start")
        self._AddLabelData(clRoot, "NONE", "None", None, None)

        self.Print("Label Types count: {}".format(len(self.clTypes)))
        self.Print("Applied Types count: {}".format(len(self.clAppliedTypes)))
        self.Print("Object Data count: {}".format(len(self.clObjectData)))
        self.Print("Ignore Object Data count: {}".format(len(self.clIgnoreObjectData)))

        ##########################################################################################
        # Prepare user material types by setting the type indices
        # and the overall shader type count for the corresponding label type
        self.Print("_PrepareUserMaterials() start")
        self._PrepareUserMaterials()

        ##########################################################################################
        # Provide all label materials needed
        self.Print("_ProvideLabelMaterials() start")
        dicMaterials = self._ProvideLabelMaterials()
        self.iColorNormValue = dicMaterials["iMaxInstCnt"]

        # New label meshes created for skeletons need a view layer update
        self.Print("View Layer Update start")
        bpy.context.view_layer.update()

        # Ensure that all meshes have a unique label
        self.Print("Ensure unique mesh label types...")
        dicMeshes = {}
        for xObjData in self.clObjectData:
            sMaterialType = xObjData.sMaterialType
            if sMaterialType == "DEFAULT":
                sLabelType = xObjData.sLabelId
                for xMesh in xObjData.clMeshes:
                    sMeshName = xMesh.sId
                    if sMeshName not in dicMeshes:
                        dicMeshes[sMeshName] = sLabelType
                    else:
                        if dicMeshes[sMeshName] != sLabelType:
                            raise RuntimeError(
                                "Mesh '{}' is used for different label types: {} and {}".format(
                                    sMeshName, dicMeshes[sMeshName], sLabelType
                                )
                            )
                        # endif
                    # endif
                # endfor meshes
            # endif
        # endfor

        # Set materials and pass index of objects
        self.Print("Set materials and pass indices for all objects...")
        for xObjData in self.clObjectData:
            sMaterialType = xObjData.sMaterialType
            dicMatType = dicMaterials["dicTypes"].get(sMaterialType)
            if dicMatType is None:
                raise Exception("Materials for material type '{}' do not exist".format(sMaterialType))
            # endif

            if sMaterialType == "DEFAULT":
                self._SetDefaultMeshLabelMaterial(dicMatType, xObjData)

            elif sMaterialType == "ARMATURE_MESH":
                # if the material is of type ARMATURE_MESH, need to create
                # and update a vertex color layer for the mesh.
                self._SetArmatureMeshLabelMaterial(dicMatType, xObjData)

            else:
                raise Exception("Unsupported label material type '{}'".format(sMaterialType))
            # endif

            objX = bpy.data.objects.get(xObjData.sId)
            objX.pass_index = xObjData.iLabelPassIdx
        # endfor

        #######################################################################
        # Replace world shader with label shader
        self.Print("Replace world shader...")

        # Get currently selected world
        worldAct = bpy.context.scene.world
        if worldAct is None:
            raise Exception("Scene has no world shader set")
        # endif

        # Store current world id
        self.xLabelSetProp.sWorldId = worldAct.name

        # Look for "AT.Label" world
        worldATL = bpy.data.worlds.get("AT.Label")
        if worldATL is None:
            # Create the label world shader
            worldATL = bpy.data.worlds.new(name="AT.Label")
            worldATL.use_nodes = True

            nodBg = worldATL.node_tree.nodes.get("Background")
            if nodBg is None:
                raise Exception("Newly created world shader does not contain 'Background' node")
            # endif

            nodBg.use_custom_color = True
            nodBg.inputs["Color"].default_value = (0, 0, 0, 1)
        # endif

        # Set AT.Label shader as world shader
        bpy.context.scene.world = worldATL

        self.Print("ApplyLabel() finished")

    # enddef

    ############################################################################################################
    def _SetDefaultMeshLabelMaterial(self, _dicMatType, _xObjData):
        sLabelType = _xObjData.sLabelId
        xMat = _dicMatType.get(sLabelType)
        if xMat is None:
            raise Exception("No material object defined for label type '{}'".format(sLabelType))
        # endif
        matType = xMat.xMaterial

        for xMesh in _xObjData.clMeshes:
            sMeshId = xMesh.sId

            ### DEBUG
            # if sMeshId == ".PlantainRibwort_Big_CLUMP_LOW_001":
            #     print(sMeshId)
            # # endif
            ###

            mshX = bpy.data.meshes[sMeshId]
            iMatCnt = len(mshX.materials)

            # Switch off LOD as workaround for problems with Grasswald.
            # I cannot find bug where LOD objects are not switched to
            # render LOD.
            # The LOD feature has been removed in Blender 2.93
            if bpy.app.version <= (2, 84, 0):
                mshX.lod_enabled = False

            if iMatCnt == 0:
                mshX.materials.append(matType)
            else:
                for iMatIdx in range(iMatCnt):
                    matX = mshX.materials[iMatIdx]

                    if matX is not None:
                        matX.use_fake_user = True
                        if matX.name not in xMesh.clMaterial:
                            sUserMatId = ""
                        else:
                            sUserMatId = xMesh.clMaterial.get(matX.name).sUserId
                        # endif

                        if len(sUserMatId) == 0:
                            mshX.materials[iMatIdx] = matType
                        else:
                            mshX.materials[iMatIdx] = bpy.data.materials[sUserMatId]
                        # endif
                    else:
                        mshX.materials[iMatIdx] = matType
                    # endif

                # endfor materials
            # endif
        # endfor meshes

    # enddef

    ############################################################################################################
    def _SetArmatureMeshLabelMaterial(self, _dicMatType, _xObjData):
        global c_dicArmatureBoneLabelWeights

        sLabelType = _xObjData.sLabelId
        dicMatSkel = _dicMatType.get(sLabelType)
        if dicMatSkel is None:
            raise Exception("No skeleton materials defined for label type '{}'".format(sLabelType))
        # endif

        # TODO: For now select the first skeleton
        lSkelIds = [x for x in dicMatSkel.keys()]
        sSkelId = lSkelIds[0]
        xMat = dicMatSkel[sSkelId]
        matType = xMat.xMaterial

        xAppType = self.clAppliedTypes.get(sLabelType)
        if xAppType is None:
            raise Exception("Invalid type '{}'".format(sLabelType))
        # endif

        lShaderTypes = [x for x in xAppType.clShaderTypes.keys()]
        iShaderTypeCnt = len(lShaderTypes)

        lBoneNames = [x for x in xAppType.clSkeletons.get(sSkelId).clBoneId.keys()]
        if lBoneNames is None:
            raise Exception("Skeleton '{}' not found in applied types".format(sSkelId))
        # endif

        lBoneLabelIdx = [lShaderTypes.index("Skeleton;{};{}".format(sSkelId, x)) for x in lBoneNames]
        lBoneIds = ["AT.Label;{};{}".format(sSkelId, x) for x in lBoneNames]

        iBoneCnt = len(lBoneLabelIdx)
        lBoneColors = []
        for iIdx in lBoneLabelIdx:
            # The vertex colors are assumed to be sRGB values by Blender.
            # So, in order to get the correct value rendered, we need
            # to convert the label id value to sRGB
            fValue = anyblend.color.ConvertRgbLinearToS((iIdx + 1) / (iShaderTypeCnt + 1))
            lBoneColors.append((fValue, fValue, fValue, 1.0))
        # endfor

        lPreviewColors = []
        fColStep = 360.0 / iBoneCnt
        for iIdx in range(iBoneCnt):
            tHsv = (iIdx * fColStep, 1.0, 1.0)
            tRgb = anyblend.color.ConvertRgbLinearToS(anyblend.color.ConvertHsvToRgb(tHsv))
            lPreviewColors.append((*tRgb, 1.0))
        # endfor

        objX = bpy.data.objects.get(_xObjData.sId)
        sVexColNameLabel = "AT.Label;{};{}".format(sSkelId, sLabelType)
        sVexColNamePreview = "AT.Label.Preview;{};{}".format(sSkelId, sLabelType)

        # Look for the associated Armature object as one of the parents
        # in the parent hierarchy of the object.
        objArma = objX
        while True:
            objArma = objArma.parent
            if objArma is None:
                raise RuntimeError(f"Object '{objX.name}' has no armature as parent")
            # endif
            if objArma.type == "ARMATURE":
                break
            # endif
        # endwhile

        armature.CreateBoneWeightVexColLay(
            objArma=objArma,
            objMesh=objX,
            lBoneNames=lBoneIds,
            sBoneWeightMode="HEAD",
            lLabelColors=lBoneColors,
            sVexColNameLabel=sVexColNameLabel,
            lPreviewColors=lPreviewColors,
            sVexColNamePreview=sVexColNamePreview,
        )

        dicArmaBLW = c_dicArmatureBoneLabelWeights.get(objArma.name)
        if dicArmaBLW is None:
            dicArmaBLW = c_dicArmatureBoneLabelWeights[objArma.name] = {
                "lBoneNames": lBoneIds,
                "sBoneWeightMode": "HEAD",
                "lLabelColors": lBoneColors,
                "sVexColNameLabel": sVexColNameLabel,
                "lPreviewColors": lPreviewColors,
                "sVexColNamePreview": sVexColNamePreview,
                "lMeshObjects": [],
            }
        # endif

        dicArmaBLW["lMeshObjects"].append(objX.name)

        mshX = objX.data
        xVexColLay = mshX.vertex_colors[sVexColNameLabel]
        xVexColLay.active_render = True
        xVexColLay = mshX.vertex_colors[sVexColNamePreview]
        xVexColLay.active = True

        iMatCnt = len(mshX.materials)

        if iMatCnt == 0:
            mshX.materials.append(matType)
        else:
            for iMatIdx in range(iMatCnt):
                matX = mshX.materials[iMatIdx]
                if matX is not None:
                    matX.use_fake_user = True
                # endif
                mshX.materials[iMatIdx] = matType
            # endfor materials
        # endif

    # enddef

    ############################################################################################################
    def _AddArmatureData(self, *, objArma, xActInst, xActAppType):
        xPose = xActInst.clPoses.get(objArma.name)
        if xPose is None:
            xPose = xActInst.clPoses.add()
            xPose.sId = xPose.name = objArma.name
        # endif
        xPose.clBones.clear()

        for boneX in objArma.pose.bones:
            xBone = xPose.clBones.add()
            xBone.sId = xBone.name = boneX.name
            xMatch = self.reAtBone.search(boneX.name)
            # Check whether bone is a AT bone
            if xMatch is not None:
                # If this is an AT bone, add the AT skeleton
                # and the bone to the applied type and
                # add a reference to the skeleton to the pose of the instance
                sSkelId = xMatch.group("skel")
                sBoneId = xMatch.group("bone")
                xSkel = xActAppType.clSkeletons.get(sSkelId)
                if xSkel is None:
                    xSkel = xActAppType.clSkeletons.add()
                    xSkel.sId = xSkel.name = sSkelId
                # endif

                xBoneId = xSkel.clBoneId.get(sBoneId)
                if xBoneId is None:
                    xBoneId = xSkel.clBoneId.add()
                    xBoneId.sId = xBoneId.name = sBoneId
                # endif

                xSkelId = xPose.clSkelId.get(sSkelId)
                if xSkelId is None:
                    xSkelId = xPose.clSkelId.add()
                    xSkelId.sId = xSkelId.name = sSkelId
                # endif
            # endif

            xBone.sParent = boneX.parent.name if boneX.parent is not None else ""
            for xChild in boneX.children:
                xBoneId = xBone.clChildren.add()
                xBoneId.sId = xBoneId.name = xChild.name
            # endfor
        # endfor

        # If the pose has at least one skeleton,
        # add the skeleton label bones as shader types
        # to the applied type
        if len(xPose.clSkelId) > 0:
            # For now, use first skeleton found.
            # TODO: Need some way to select skeleton type for labelling.
            sSkelId = xPose.clSkelId[0].sId
            xSkel = xActAppType.clSkeletons.get(sSkelId)
            # iBoneCnt = len(xSkel.clBoneId)

            xActAppType.iShaderMaxInstCnt = max(xActAppType.iShaderMaxInstCnt, 1)

            for sBoneId in xSkel.clBoneId.keys():
                sShaderType = "Skeleton;{};{}".format(sSkelId, sBoneId)
                if sShaderType not in xActAppType.clShaderTypes:
                    xShType = xActAppType.clShaderTypes.add()
                    xShType.sId = xShType.name = sShaderType
                # endif
            # endfor
        # endif

        return xPose

    # enddef

    ############################################################################################################
    def _GetInstances(self, _lObjects: list[str], _sActiveCollection: str) -> list[CLabelInstance]:
        """For each top level object collect the object itself and all its' children
            that are of an allowed type and are members of collection _clAct, into separate object lists.

        Parameters
        ----------
        _lObjects : list[str]
            Top level objects.
        _sActiveCollection : string
            Only objects and child objects that are members of this collection are considered.

        Returns
        -------
        list[CLabelInstance]
            List of instance objects.
        """
        # For each top level object collect the object itself and all its' children
        # that are of an allowed type, into separate object lists.
        clnAct = bpy.data.collections.get(_sActiveCollection)

        lLabInstList: list[CLabelInstance] = []
        for sTopObj in _lObjects:
            if clnAct is not None and sTopObj not in clnAct.objects:
                continue
            # endif

            objTop = bpy.data.objects[sTopObj]

            if objTop.AnyTruth.xSettings.bIgnore is True:
                xIgnObjData = self.clIgnoreObjectData.add()
                xIgnObjData.sId = xIgnObjData.name = objTop.name
                xIgnObjData.bHideRender = objTop.hide_render
                xIgnObjData.bHideViewport = objTop.hide_get()
                anyblend.object.Hide(objTop, bHide=True, bHideRender=True)
                continue
            # endif

            if objTop.type == "EMPTY":
                lChildren = [x.name for x in objTop.children]
                if len(lChildren) > 0:
                    lChildInst = self._GetInstances(lChildren, _sActiveCollection)
                    lLabInstList.extend(lChildInst)
                # endif

            elif objTop.type in self._lAllowedInstTypes and objTop.hide_render is False:
                lInstGrp = [sTopObj]
                lChildren = [x.name for x in objTop.children]
                if len(lChildren) > 0:
                    lChildInst = self._GetInstances(lChildren, _sActiveCollection)
                    for xChild in lChildInst:
                        lInstGrp.extend(xChild.lValidObjects)
                    # endfor
                # endif

                # Look for instance orientation object
                objOrient = next(
                    (x for x in objTop.children if x.type == "EMPTY" and self.reAtOrient.match(x.name) is not None),
                    None,
                )

                # Check whether object has a child orientation empty
                if objOrient is None:
                    sInstOrientId = objTop.name
                else:
                    sInstOrientId = objOrient.name
                # endif

                # print(f"Cln: {_sActiveCollection}, Top: {objTop.name} -> {sInstOrientId}")

                lLabInstList.append(
                    CLabelInstance(_sTopObj=sTopObj, _sOrientObj=sInstOrientId, _lValidObjects=lInstGrp)
                )
            # endif
        # endfor

        return lLabInstList

    # enddef

    ############################################################################################################
    def _AddLabelData(
        self,
        _clAct,
        _sParentInstType,
        _sLabelType,
        _sParentInstOrientId,
        _iParentInstIdx,
    ):
        ### DEBUG
        # sClName = _clAct.name
        # if sClName == "Grass":
        #     print(sClName)
        # # endif
        ###

        # Do not process collections excluded from the current view layer context
        if anyblend.collection.IsExcluded(bpy.context, _clAct.name):
            return None
        # endif

        xLabel = None
        bIgnore = False
        xAnyTruth = _clAct.AnyTruth
        if xAnyTruth is None:
            bIgnore = True
        else:
            xLabel = xAnyTruth.xLabel
            if xLabel is None:
                bIgnore = True
            else:
                bIgnore = xLabel.bIgnore
            # endif
        # endif

        if bIgnore:
            return None
        # endif

        # Test whether collection has a label type that is currently not available
        # In this case, mark the collection has not having a label
        if xLabel.bHasLabel is True:
            if self.clTypes.get(xLabel.sType) is None:
                xLabel.bHasLabel = False
            # endif
        # endif

        xActLabelType = self.clTypes.get(_sLabelType)

        sLabelType = xLabel.sType if xLabel.bHasLabel else _sLabelType
        bEqualLabelType = _sLabelType == sLabelType

        sThisInstType = xLabel.eChildrenInstanceType if xLabel.bHasLabel else "NONE"
        sParentInstType = _sParentInstType if bEqualLabelType else "NONE"

        if sThisInstType == "INHERIT":
            sThisInstType = sParentInstType
        # endif

        bFirstObject = True
        dicThisInstInc = self.dicInstInc.get(sParentInstType)
        if dicThisInstInc is None:
            raise Exception("Unsupport children instance type '{0}'".format(sParentInstType))
        # endif
        iFirstObjInc, iNextObjInc = dicThisInstInc.get(sThisInstType)

        xActLabelType = self.clTypes.get(sLabelType)
        xActAppType = self.clAppliedTypes.get(sLabelType)
        if xActAppType is None:
            xActInst = None
        else:
            if bEqualLabelType and _iParentInstIdx is not None and iFirstObjInc == 0:
                xActInst = xActAppType.clInstances[_iParentInstIdx]
            else:
                xActInst = None
            # endif
        # endif

        # Get top-level objects in collection
        lTopObjs = anyblend.collection.GetCollectionObjects(_clAct)
        # Keep only those objects that are also rendered
        lTopObjs = [x for x in lTopObjs if bpy.data.objects[x].hide_render is False]

        # Get list of instances by ignoring empties and only collecting
        # MESH and ARMATURE objects and their children as instances.
        lLabInst: list[CLabelInstance] = self._GetInstances(lTopObjs, _clAct.name)

        ##########################################
        ### DEBUG ####
        # if _clAct.name == "Highway.4Lane":
        #     iLen = len(lLabInst)
        #     print(f"Instance count: {iLen}")
        #     for xInst in lLabInst:
        #         print(xInst.lValidObjects)
        #     # endfor
        # # endif
        ##########################################

        if bEqualLabelType and _sParentInstOrientId is not None and iFirstObjInc == 0:
            sInstOrientId = _sParentInstOrientId
        else:
            # Look for instance orientation object
            objOrient = next(
                (
                    bpy.data.objects[x]
                    for x in lTopObjs
                    if bpy.data.objects[x].type == "EMPTY" and self.reAtOrient.match(x) is not None
                ),
                None,
            )

            if objOrient is None:
                # if no explicit instance orientation object is present at the top level,
                # then look for an orientation empty as child of a top object.
                for sTopObj in lTopObjs:
                    objTop = bpy.data.objects[sTopObj]
                    if objTop is not None:
                        objOrient = next(
                            (
                                x
                                for x in objTop.children
                                if x.type == "EMPTY" and self.reAtOrient.match(x.name) is not None
                            ),
                            None,
                        )
                        if objOrient is not None:
                            break
                        # endif
                    # endif
                # endfor

                if objOrient is None:
                    # if not explicit orientation object could be found as child of a top object,
                    # then take the first Empty in the collection.
                    objOrient = next(
                        (bpy.data.objects[x] for x in lTopObjs if bpy.data.objects[x].type == "EMPTY"),
                        None,
                    )

                    # if there is also no empty in the collection, use the first object's orientation object
                    if objOrient is None and len(lLabInst) > 0:
                        objOrient = bpy.data.objects.get(lLabInst[0].sOrientObj)
                    # endif
                # endif
            # endif

            # if objOrient is not None:
            #     print(f"clnAct: {_clAct.name}, objOrient: {objOrient.name}")
            # else:
            #     print(f"clnAct: {_clAct.name}, objOrient: None")
            # # endif

            if objOrient is None:
                sInstOrientId = None
            else:
                sInstOrientId = objOrient.name
            # endif
        # endif

        # print(f">> clnAct: {_clAct.name}, sInstOrientId: {sInstOrientId}")

        # Loop over instances
        for xLabInst in lLabInst:
            bNewInstance = False
            if bFirstObject:
                bFirstObject = False
                if xActInst is None and iFirstObjInc == 0:
                    bNewInstance = True
                else:
                    bNewInstance = iFirstObjInc > 0
                # endif
            else:
                bNewInstance = iNextObjInc > 0
            # endif

            # If every object is an instance, then use the object's orientation
            # as instance orientation, or a child orientation empty.
            if iNextObjInc > 0:
                sInstOrientId = xLabInst.sOrientObj
            # endif

            # Add new instance to applied type data
            if bNewInstance:
                if xActAppType is None:
                    # print(">>>>>")
                    # print("Add instance type: {0}".format(xActLabelType.sId))
                    # print("Object: {0}".format(objY.name))
                    # print("Object parent: {0}".format(objY.parent.name if objY.parent is not None else ""))
                    # print("Collection: {0}".format(_clAct.name))
                    # print(">>>>>")
                    xActAppType = self.clAppliedTypes.add()
                    xActAppType.sId = xActAppType.name = xActLabelType.sId
                    xActAppType.colLabel = xActLabelType.colLabel
                # endif

                xActInst = xActAppType.clInstances.add()
                iLabelTypeInstIdx = len(xActAppType.clInstances)
                xActInst.name = str(iLabelTypeInstIdx)
                xActInst.iIdx = iLabelTypeInstIdx
                xActInst.sOrientId = sInstOrientId if sInstOrientId is not None else ""
            # endif

            # Store pose of armature objects
            if xLabInst.sType == "ARMATURE":
                xArmaPose = self._AddArmatureData(objArma=xLabInst.objTop, xActInst=xActInst, xActAppType=xActAppType)
            else:
                xArmaPose = None
            # endif

            lObjects: list[bpy.types.Object] = [
                bpy.data.objects[x] for x in xLabInst.lValidObjects if bpy.data.objects[x].type == "MESH"
            ]

            objIter: bpy.types.Object
            for objIter in lObjects:
                # Store current object data that will be changed
                xObjData = self.clObjectData.add()
                xObjData.sLabelId = sLabelType
                xObjData.iLabelPassIdx = xActInst.iIdx

                objX: bpy.types.Object = None
                if xArmaPose is not None and len(xArmaPose.clSkelId) > 0:
                    if self.bEnableArmatureSelfOcclusion is True:
                        xObjData.sMaterialType = "ARMATURE_MESH"
                    else:
                        xObjData.sMaterialType = "DEFAULT"
                    # endif

                    # Evaluate mesh object and add it as child to armature.
                    # This will be the object we are labelling
                    objX = armature.CreateLabelMeshObject(objIter)

                else:
                    xObjData.sMaterialType = "DEFAULT"
                    objX = objIter
                # endif

                xObjData.sId = xObjData.name = objX.name
                xObjData.iPassIdx = objX.pass_index
                xObjData.bIsShadowCatcher = objX.is_shadow_catcher

                # Store object in applied types structure
                xActObj = xActInst.clObjects.add()
                xActObj.name = objX.name
                xActObj.pObject = objX

                # get original LOD mesh, which contains the list of lod meshes
                lObjMeshes = []
                # The LOD feature has been removed in Blender 2.93
                if bpy.app.version <= (2, 84, 0):
                    mshOrig = objX.lod_original
                else:
                    mshOrig = None
                # endif

                if mshOrig is None:
                    # Check whether object has graswald data
                    if hasattr(objX, "graswald"):
                        xGwLod = objX.graswald.lod
                        if (
                            xGwLod.high_data is not None
                            and xGwLod.low_data is not None
                            and xGwLod.proxy_data is not None
                        ):
                            # Use meshes stored in Graswald LOD
                            lObjMeshes = [
                                objX.graswald.lod.high_data,
                                objX.graswald.lod.low_data,
                                objX.graswald.lod.proxy_data,
                            ]
                        else:
                            lObjMeshes = [objX.data]
                        # endif
                    else:
                        # There are no LODs
                        lObjMeshes = [objX.data]
                    # endif
                else:
                    # There are LOD meshes
                    if mshOrig.lod_enabled:
                        lObjMeshes = [x.ui_lod for x in mshOrig.lod_list]
                    else:
                        lObjMeshes = [objX.data]
                    # endif
                # endif

                # Loop over LOD meshes of object
                for mshX in lObjMeshes:
                    xObjMesh = xObjData.clMeshes.add()
                    xObjMesh.sId = mshX.name
                    if bpy.app.version <= (2, 84, 0):
                        xObjMesh.bLodEnabled = mshX.lod_enabled
                    else:
                        xObjMesh.bLodEnabled = False
                    # endif

                    # lUserMaterial = []

                    # Store current set of materials of mesh
                    for matX in mshX.materials:
                        xMeshMat = xObjMesh.clMaterial.add()
                        if matX is None:
                            xMeshMat.sId = ""
                            xMeshMat.sUserId = ""
                            xMeshMat.bFakeUser = False
                        else:
                            xMeshMat.sId = xMeshMat.name = matX.name
                            xMeshMat.bFakeUser = matX.use_fake_user

                            # Check whether material has associated AnyTruth Material
                            sAtMatId = "{0};AT.Label.{1}".format(matX.name, sLabelType)
                            if sAtMatId not in self.dicUserLabelMaterial:
                                # Check whether AnyTruth material is currently active
                                if matX.name in self.dicUserLabelMaterial:
                                    # if yes, then use it also as "replacement"
                                    sAtMatId = matX.name
                                # endif
                            # endif

                            # Again check whether label material exists
                            if sAtMatId in self.dicUserLabelMaterial:
                                xMeshMat.sUserId = sAtMatId
                                dicUserMat = self.dicUserLabelMaterial.get(sAtMatId)

                                xActAppType.iShaderMaxInstCnt = max(
                                    xActAppType.iShaderMaxInstCnt,
                                    dicUserMat.get("iShaderMaxInstCnt"),
                                )

                                for sShaderType in dicUserMat.get("lShaderTypes"):
                                    if sShaderType not in xActAppType.clShaderTypes:
                                        xShType = xActAppType.clShaderTypes.add()
                                        xShType.sId = xShType.name = sShaderType
                                    # endif
                                # endfor
                            else:
                                xMeshMat.sUserId = ""
                            # endif
                        # endif
                    # endfor materials
                # endfor meshes

            # endfor object + objects children
        # endfor objects in collection

        iThisInstIdx = None
        if iNextObjInc == 0 and xActInst is not None:
            iThisInstIdx = len(xActAppType.clInstances) - 1
        # endif

        # Loop over all child collections
        for clChild in _clAct.children:
            iChildInstIdx = self._AddLabelData(clChild, sThisInstType, sLabelType, sInstOrientId, iThisInstIdx)
            if iThisInstIdx is None and iChildInstIdx is not None and iNextObjInc == 0:
                iThisInstIdx = iChildInstIdx
            # endif
        # endfor

        if bEqualLabelType and _iParentInstIdx is None and iFirstObjInc == 0 and xActInst is not None:
            iThisInstIdx = len(xActAppType.clInstances) - 1
        else:
            iThisInstIdx = None
        # endif

        return iThisInstIdx

    # enddef

    ###################################################################################
    def Restore(self):
        self.Print("Restore() start")

        for xObjData in self.clObjectData:
            objX = bpy.data.objects.get(xObjData.sId)
            if objX is None:
                continue
            # endif

            if armature.TestRemoveLabelMeshObject(objX) is True:
                continue
            # endif

            for iMeshIdx, xMesh in enumerate(xObjData.clMeshes):
                sMeshId = xMesh.sId
                mshX = bpy.data.meshes.get(sMeshId)
                if bpy.app.version <= (2, 84, 0):
                    mshX.lod_enabled = xMesh.bLodEnabled
                # endif

                if len(xMesh.clMaterial) == 0:
                    mshX.materials.clear()
                else:
                    for iMatIdx, xMat in enumerate(xMesh.clMaterial):
                        sMatId = xMat.sId
                        if len(sMatId) == 0:
                            mshX.materials[iMatIdx] = None
                        else:
                            matX = bpy.data.materials.get(sMatId)
                            mshX.materials[iMatIdx] = matX
                            matX.use_fake_user = xMat.bFakeUser
                        # endif
                    # endfor materials
                # endif has materials
            # endfor meshes
            objX.pass_index = xObjData.iPassIdx
            objX.is_shadow_catcher = xObjData.bIsShadowCatcher
        # endfor objects

        for xObjData in self.clIgnoreObjectData:
            objX = bpy.data.objects.get(xObjData.sId)
            if objX is None:
                continue
            # endif

            objX.hide_render = xObjData.bHideRender
            objX.hide_set(xObjData.bHideViewport)
        # endif

        self.clObjectData.clear()
        self.clIgnoreObjectData.clear()
        self.clAppliedTypes.clear()
        self.iAppliedTypeSelIdx = 0
        self.iColorNormValue = 0

        # Restore World shader
        worldOrig = bpy.data.worlds.get(self.xLabelSetProp.sWorldId)
        if worldOrig is None:
            raise Exception("Cannot restore original world shader with name '{0}'".format(self.xLabelSetProp.sWorldId))
        # endif
        bpy.context.scene.world = worldOrig

        # Restore camera settings
        self._RestoreCameraFromLabeling()

        self.Print("Restore() finished")

    # enddef

    ###################################################################################
    def EvalPoses(self):
        for xAppType in self.clAppliedTypes:
            for xInst in xAppType.clInstances:
                for xPose in xInst.clPoses:
                    objX = bpy.data.objects[xPose.sId]
                    if objX is None or objX.type != "ARMATURE":
                        continue
                    # endif

                    mWorld = objX.matrix_world
                    for boneX in objX.pose.bones:
                        xBone = xPose.clBones.get(boneX.name)
                        if xBone is None:
                            continue
                        # endif

                        # Get Bone matrix in world coordinates
                        mBone = mWorld @ boneX.matrix
                        # Get rotation matrix without scale
                        mAxes = mBone.to_euler().to_matrix().transposed()

                        # Get head and tail positions
                        vHead = (mWorld @ boneX.head.to_4d()).to_3d()
                        vTail = (mWorld @ boneX.tail.to_4d()).to_3d()

                        xBone.vAxisX = tuple(mAxes[0])
                        xBone.vAxisY = tuple(mAxes[1])
                        xBone.vAxisZ = tuple(mAxes[2])
                        xBone.vHead = tuple(vHead)
                        xBone.vTail = tuple(vTail)
                    # endfor bones
                # endfor pose objects
            # endfor instance
        # endfor type

    # enddef

    ###################################################################################
    def EvalBoxes3d(self):
        xDepsGraph = bpy.context.evaluated_depsgraph_get()

        for xAppType in self.clAppliedTypes:
            ############################################
            # ## DEBUG ###
            # print(f"Processing applied type '{xAppType.sId}'")
            ############################################

            for xInst in xAppType.clInstances:
                ############################################
                # ## DEBUG ###
                # if len(xInst.clObjects) > 0:
                #     print(xInst.clObjects[0].pObject.name)
                # # endif
                ############################################

                xInst.xBox3d.bIsValid = False
                sOrientId = xInst.sOrientId

                # Use presence of sOrientId as flag whether to calculate a 3d box
                if len(sOrientId) == 0:
                    continue
                # endif

                aAllVex = None
                for xObj in xInst.clObjects:
                    objOrigX = xObj.pObject
                    if objOrigX.hide_render is True:
                        continue
                    # endif
                    ### DEBUG ###
                    # print(f"3D Box Object: {objOrigX.name} ({objOrigX.type})")
                    #############

                    objX = objOrigX.evaluated_get(xDepsGraph)
                    if len(objX.data.vertices) == 0:
                        # print("> No vertices!")
                        continue
                    # endif

                    # if objOrigX.parent is not None and objOrigX.parent.type == "ARMATURE":
                    # 	objP = objX.parent.evaluated_get(xDepsGraph)
                    # 	mWorld = objP.matrix_world @ objX.matrix_world
                    # else:
                    # 	mWorld = objX.matrix_world
                    # # endif
                    mWorld = objX.matrix_world

                    mWorldT = np.array(mWorld.to_3x3()).transpose()
                    mTrans = np.array(mWorld.translation)
                    meshX = objX.to_mesh()

                    iVexCnt = len(meshX.vertices)
                    aVex = np.empty(iVexCnt * 3, dtype=np.float64)
                    meshX.vertices.foreach_get("co", aVex)
                    aVex.shape = (iVexCnt, 3)
                    aVex = (aVex @ mWorldT) + mTrans

                    if aAllVex is not None:
                        aAllVex = np.append(aAllVex, aVex, axis=0)
                    else:
                        aAllVex = aVex.copy()
                    # endif

                    objX.to_mesh_clear()
                # endfor objects

                # Test whether any vertices were collected.
                # This can be zero for mesh objects that only instantiate with geometry nodes.
                if aAllVex is None or aAllVex.shape[0] == 0:
                    # print("> No vertices collected")
                    continue
                # endif

                # Test whether an orientation object is defined for this instance
                if len(sOrientId) > 0:
                    # We will use the world matrix axes of the orientation object
                    # as the main axes along which to calculate the 3d box.
                    objOrient = bpy.data.objects.get(sOrientId)

                    # Get rotation matrix of orientation object without scale
                    mWorldT = np.array(objOrient.matrix_world.to_euler().to_matrix()).transpose()
                    mWorldInvT = np.array(objOrient.matrix_world.to_euler().to_matrix().inverted()).transpose()

                else:
                    # Use an SVD to determine the main directions of the vertex set

                    # Object Mean
                    aMean = np.mean(aAllVex, axis=0)
                    aRelVex = aAllVex - aMean
                    aSqVex = aRelVex.transpose() @ aRelVex

                    mWorldInvT, mS, mWorldT = np.linalg.svd(aSqVex)
                # endif

                # print(f"aAllVex.shape: {aAllVex.shape}")
                aRotVex = aAllVex @ mWorldInvT

                aMin = aRotVex.min(axis=0)
                aMax = aRotVex.max(axis=0)
                aSize = aMax - aMin
                aCtr = (aMin + aSize / 2.0) @ mWorldT

                xBox3d = xInst.xBox3d
                xBox3d.bIsValid = True
                xBox3d.vCenter = tuple(aCtr.tolist())
                xBox3d.vSize = tuple(aSize.tolist())
                xBox3d.vAxisX = tuple(mWorldT[0].tolist())
                xBox3d.vAxisY = tuple(mWorldT[1].tolist())
                xBox3d.vAxisZ = tuple(mWorldT[2].tolist())

            # endfor instance
        # endfor type

    # enddef

    ###################################################################################
    def EvalBoxes2d(self):
        # xDepsGraph = bpy.context.evaluated_depsgraph_get()

        viewCam = anycam.ops.GetAnyCamView(bpy.context, bpy.context.scene.camera.name, _bAddExtrinsics=True)
        bCanProject: bool = hasattr(viewCam, "ProjectToImage")

        for xAppType in self.clAppliedTypes:
            ############################################
            # ## DEBUG ###
            # print(f"Processing applied type '{xAppType.sId}'")
            ############################################

            for xInst in xAppType.clInstances:
                ############################################
                # ## DEBUG ###
                # if len(xInst.clObjects) > 0:
                #     print(xInst.clObjects[0].pObject.name)
                # # endif
                ############################################

                xInst.xBox2d.bIsValid = False
                if bCanProject is False:
                    continue
                # endif

                aAllVex = None
                for xObj in xInst.clObjects:
                    objOrigX = xObj.pObject
                    if objOrigX.hide_render is True:
                        continue
                    # endif

                    aVex = anyblend.object.GetMeshVex(objOrigX, sFrame="WORLD", bEvaluated=True)

                    if aAllVex is not None:
                        aAllVex = np.append(aAllVex, aVex, axis=0)
                    else:
                        aAllVex = aVex.copy()
                    # endif
                # endfor objects

                # Test whether any vertices were collected.
                # This can be zero for mesh objects that only instantiate with geometry nodes.
                if aAllVex is None or aAllVex.shape[0] == 0:
                    # print("> No vertices collected")
                    continue
                # endif

                lImgPnts, lInFront, lInImage = viewCam.ProjectToImage(aAllVex, _bDetailedFlags=True)
                if all(lInFront) is True:
                    aImgPnts = np.array(lImgPnts)
                    aMin = np.min(aImgPnts, axis=0)
                    aMax = np.max(aImgPnts, axis=0)

                    xBox2d = xInst.xBox2d
                    xBox2d.bIsValid = True
                    xBox2d.vMinXY = (aMin[0], aMin[1], 0)
                    xBox2d.vMaxXY = (aMax[0], aMax[1], 0)
                # endif

            # endfor instance
        # endfor type

    # enddef

    ###################################################################################
    def EvalVertexLists3d(self):
        # xDepsGraph = bpy.context.evaluated_depsgraph_get()

        for xAppType in self.clAppliedTypes:
            for xInst in xAppType.clInstances:
                # Clear any vertex group types that may be present
                xInst.clVexGrpTypes.clear()

                # Loop over all objects in the instance
                for xObj in xInst.clObjects:
                    objOrigX = xObj.pObject
                    # Check whether object contains per vertex label data
                    if objOrigX.type != "MESH" or "AT.Label" not in objOrigX.data.vertex_colors:
                        continue
                    # endif
                    # print("Processing object: {0}".format(objOrigX.name))

                    # Loop over all vertex groups to get association of label type to vertex color
                    for vgX in objOrigX.vertex_groups:
                        # print("Processing vertex group: {0}".format(vgX.name))

                        # Check if the vex groups' name fits the assumed structure
                        # e.g. 'AT.Label;Road.Std.Mark.Lane.Solid;0;ls;1;1;1;center'
                        # 'AT.Label;[Label type];[Shader instance];[id];[vex type];[r];[g];[b]'
                        # (r, g, b)/255 are the RGB values associated with these vertices in the vertex color layer.
                        # 'vex type' determines the structure of the vertices:
                        # - 'ls': line strip. The vertices should be interpreted as a line-strip.
                        # 	        This has to be a quad strip with zero width. If the vertex group has no faces,
                        #    		the vertex colors are not kept through when the object is transformed by modifiers.
                        # 'id': An id name for the list of vertices that will be used in the output label data.
                        #           That is, there may be any number of vertex groups with the same label type and
                        #           shader instance, but different (r, g, b) values and names.
                        #           For example, a road lane line could have a center, left and right line-strip.
                        mchVgName = self.reAtVexGrp.match(vgX.name)
                        if mchVgName is None:
                            continue
                        # endif

                        sVgLabelType = mchVgName.group("type")
                        sVgShInst = mchVgName.group("inst")
                        sVgId = mchVgName.group("id")
                        sVgVexType = mchVgName.group("vextype")
                        sVgColR = mchVgName.group("r")
                        sVgColG = mchVgName.group("g")
                        sVgColB = mchVgName.group("b")
                        tRGB = (
                            float(sVgColR) / 255.0,
                            float(sVgColG) / 255.0,
                            float(sVgColB) / 255.0,
                        )

                        if sVgVexType not in ["ls"]:
                            raise Exception(
                                "Vertex group type '{0}' not supported "
                                "in vertex group '{1}' of object '{2}'".format(sVgVexType, vgX.name, objOrigX.name)
                            )
                        # endif

                        xVexGrpType = xInst.clVexGrpTypes.get(sVgLabelType)
                        if xVexGrpType is None:
                            xVexGrpType = xInst.clVexGrpTypes.add()
                            xVexGrpType.name = xVexGrpType.sId = sVgLabelType
                        # endif

                        xVgTypeInst = xVexGrpType.clInstances.get(sVgShInst)
                        if xVgTypeInst is None:
                            xVgTypeInst = xVexGrpType.clInstances.add()
                            xVgTypeInst.name = sVgShInst
                            xVgTypeInst.iIdx = int(sVgShInst)
                        # endif

                        xVexGrp = xVgTypeInst.clVertexGroups.get(sVgId)
                        if xVexGrp is not None:
                            raise Exception(
                                "Vertex group id '{0}' for label type '{1}' and "
                                "shader instance '{2}' used multiple times, see object: {3}".format(
                                    sVgId, sVgLabelType, sVgShInst, objOrigX.name
                                )
                            )
                        # endif
                        # print("Processing vertex group '{0}' of object '{1}'".format(sVgId, objOrigX.name))

                        xVexGrp = xVgTypeInst.clVertexGroups.add()
                        xVexGrp.name = xVexGrp.sId = sVgId
                        xVexGrp.sType = sVgVexType
                        xVexGrp.vColor = tRGB

                        if sVgVexType == "ls":
                            lLineStrips = self._GetVexListLineStrip(objOrigX, tRGB)
                            for lLineStrip in lLineStrips:
                                xVexList = xVexGrp.clVertexLists.add()
                                xVexList.eType = "LINESTRIP"
                                for lVex in lLineStrip:
                                    xVex = xVexList.clVertices.add()
                                    xVex.vVertex = tuple(lVex)
                                # endfor
                            # endfor
                        else:
                            raise Exception(
                                "Vertex group type '{0}' not supported "
                                "in vertex group '{1}' of object '{2}'".format(sVgVexType, vgX.name, objOrigX.name)
                            )
                        # endif
                    # endfor vertex groups
                # endfor objects
            # endfor instance
        # endfor type

    # enddef

    ##########################################################################
    def _GetVexListLineStrip(self, _objOrigX, _tRGB):
        xDG = bpy.context.evaluated_depsgraph_get()

        objX = _objOrigX.evaluated_get(xDG)
        mshX = objX.to_mesh()

        mWorld = objX.matrix_world
        mWorldT = np.array(mWorld.to_3x3()).transpose()
        mTrans = np.array(mWorld.translation)

        xVexCol = mshX.vertex_colors.get("AT.Label")
        if xVexCol is None:
            raise Exception("Vertex color layer with name 'AT.Label' not available")
        # endif

        # Find indices of vertices that have the given color associated in the vertex color layer.
        # lColVexColor = [
        # 	tuple(xVexCol.data[i].color) for i, x in enumerate(mshX.loops)
        # 	if xVexCol.data[i].color[0] > 0.0
        # ]

        fClose = 1e-2
        fPrec = 1 / 512.0
        lColVexIdx = [
            x.vertex_index
            for i, x in enumerate(mshX.loops)
            if (
                abs(xVexCol.data[i].color[0] - _tRGB[0]) < fPrec
                and abs(xVexCol.data[i].color[1] - _tRGB[1]) < fPrec
                and abs(xVexCol.data[i].color[2] - _tRGB[2]) < fPrec
            )
        ]

        # Get indices of edges whose both vertices are contained in lColVexList
        lEdgeIdx = [x.index for x in mshX.edges if all((v in lColVexIdx for v in x.vertices))]
        # Get the vertex indices for the edges
        lEdgeVexIdx = [[mshX.edges[i].vertices[0], mshX.edges[i].vertices[1]] for i in lEdgeIdx]

        # Get unique set of vertex indices contained in all edges
        lVexIdx = list(set([i for lSublist in lEdgeVexIdx for i in lSublist]))

        # Get the array of vertex coordinates
        aVex = np.array([list(mshX.vertices[i].co) for i in lVexIdx])

        # Convert the edge indices to indices for lVexIdx
        lMyEdgeVexIdx = [[lVexIdx.index(lEdge[0]), lVexIdx.index(lEdge[1])] for lEdge in lEdgeVexIdx]

        # Find vertex indices that relate to the same point in space
        lSameVexIdx = [lEdge for lEdge in lMyEdgeVexIdx if np.linalg.norm(aVex[lEdge[0]] - aVex[lEdge[1]]) < fClose]

        # Create a vertex index reference list, where equivalent vertices point to the same index
        lSameRefIdx = np.arange(aVex.shape[0]).tolist()
        for lSameIdx in lSameVexIdx:
            lSameRefIdx[max(lSameIdx)] = min(lSameIdx)
        # endfor

        # Get the list of vertices that are unique in 3d space
        lUniqueVexIdx = list(set(lSameRefIdx))
        iUniqueVexCnt = len(lUniqueVexIdx)

        # Get the 3d coordinates of these unique vertices
        aUniqueVex = (aVex[lUniqueVexIdx] @ mWorldT) + mTrans

        # Convert the edge indices so that indices that refer to the same vertex are also equal,
        # and remove edges that have zero length
        lMyEdgeVexIdx = [
            [lSameRefIdx[lEdge[0]], lSameRefIdx[lEdge[1]]]
            for lEdge in lMyEdgeVexIdx
            if lSameRefIdx[lEdge[0]] != lSameRefIdx[lEdge[1]]
        ]

        # Convert vertex indices to point into lUniqueVexIdx
        lMyEdgeVexIdx = [[lUniqueVexIdx.index(lEdge[0]), lUniqueVexIdx.index(lEdge[1])] for lEdge in lMyEdgeVexIdx]

        # Create hashes of edges and reduce them to a unique set
        setMyEdgeVexIdxHash = set([min(lEdge) * iUniqueVexCnt + max(lEdge) for lEdge in lMyEdgeVexIdx])

        # Get list of unique edges
        lMyUniqueEdge = [[int(h / iUniqueVexCnt), h % iUniqueVexCnt] for h in set(setMyEdgeVexIdxHash)]

        # find edge connections
        lStripLists = []
        setAllStripVex = set([])
        bHasLoop = False

        for lStartEdge in lMyUniqueEdge:
            if lStartEdge[0] in setAllStripVex:
                continue
            # endif
            lEdge = lStartEdge.copy()
            # print("Start Edge: {0}".format(lStartEdge))
            lStrip = []
            lStripVex = []
            while True:
                if lEdge[0] in lStripVex:
                    # print("Loop: {0}".format(lEdge))
                    bHasLoop = True
                    break
                # endif
                setAllStripVex.add(lEdge[0])
                lStripVex.append(lEdge[0])
                lStrip.append(lEdge)
                lNextEdge = next(
                    (x for x in lMyUniqueEdge if x[0] == lEdge[1] and x[1] not in setAllStripVex),
                    None,
                )
                if lNextEdge is None:
                    lNextEdge = next(
                        (x for x in lMyUniqueEdge if x[1] == lEdge[1] and x[0] not in setAllStripVex),
                        None,
                    )
                    if lNextEdge is None:
                        if lEdge[1] not in setAllStripVex:
                            lStripVex.append(lEdge[1])
                            setAllStripVex.add(lEdge[1])
                        # endif
                        break
                    # endif
                    lEdge = [lNextEdge[1], lNextEdge[0]]
                else:
                    lEdge = lNextEdge
                # endif
            # endfor
            # print("lStrip ({0}):\n{1}\n".format(len(lStrip), lStrip))

            lEdge = lStartEdge.copy()
            while True:
                lNextEdge = next(
                    (x for x in lMyUniqueEdge if x[1] == lEdge[0] and x[0] not in setAllStripVex),
                    None,
                )
                if lNextEdge is None:
                    lNextEdge = next(
                        (x for x in lMyUniqueEdge if x[0] == lEdge[0] and x[1] not in setAllStripVex),
                        None,
                    )
                    if lNextEdge is None or lNextEdge[1] in setAllStripVex:
                        if lEdge[0] not in lStripVex:
                            lStripVex.insert(0, lEdge[0])
                            setAllStripVex.add(lEdge[0])
                        # endif
                        break
                    # endif
                    lEdge = [lNextEdge[1], lNextEdge[0]]
                else:
                    lEdge = lNextEdge
                # endif
                if lEdge[0] in lStripVex:
                    # print("Loop: {0}".format(lEdge))
                    bHasLoop = True
                    break
                # endif
                setAllStripVex.add(lEdge[0])
                lStripVex.insert(0, lEdge[0])
                lStrip.insert(0, lEdge)
            # endfor
            # print("lStrip ({0}):\n{1}\n".format(len(lStrip), lStrip))

            if bHasLoop:
                break
            # endif
            lStripLists.append(lStripVex)
        # endfor
        # print("lStripLists ({0}):\n{1}\n".format(len(lStripLists), lStripLists))

        if bHasLoop:
            raise Exception("Edge loop found in line strip")
        # endif

        # Check whether line strips are connected in 3d space
        setUsedStripIdx = set([])
        lFullStripLists = []
        iStartStripIdx = 0
        while iStartStripIdx < len(lStripLists):
            if iStartStripIdx not in setUsedStripIdx:
                setUsedStripIdx.add(iStartStripIdx)
                lStrip = lStripLists[iStartStripIdx]
                lFullStrip = lStrip.copy()
                aVexBase = aUniqueVex[lStrip[-1]]
                while True:
                    bNextStripFound = False
                    for iTestStripIdx in range(len(lStripLists)):
                        if iTestStripIdx in setUsedStripIdx:
                            continue
                        # endif
                        lTestStrip = lStripLists[iTestStripIdx]
                        if np.linalg.norm(aVexBase - aUniqueVex[lTestStrip[0]]) < fClose:
                            setUsedStripIdx.add(iTestStripIdx)
                            lFullStrip.extend(lTestStrip[1:])
                            aVexBase = aUniqueVex[lTestStrip[-1]]
                            bNextStripFound = True
                            break
                        elif np.linalg.norm(aVexBase - aUniqueVex[lTestStrip[-1]]) < fClose:
                            setUsedStripIdx.add(iTestStripIdx)
                            lFullStrip.extend(lTestStrip[-2:0:-1])
                            aVexBase = aUniqueVex[lTestStrip[0]]
                            bNextStripFound = True
                            break
                        # endif
                    # endfor
                    if not bNextStripFound:
                        break
                    # endif
                # endwhile

                aVexBase = aUniqueVex[lStrip[0]]
                while True:
                    bPrevStripFound = False
                    for iTestStripIdx in range(len(lStripLists)):
                        if iTestStripIdx in setUsedStripIdx:
                            continue
                        # endif
                        lTestStrip = lStripLists[iTestStripIdx]
                        if np.linalg.norm(aVexBase - aUniqueVex[lTestStrip[-1]]) < fClose:
                            setUsedStripIdx.add(iTestStripIdx)
                            lTemp = lTestStrip[0:-2]
                            lTemp.extend(lFullStrip)
                            lFullStrip = lTemp
                            aVexBase = aUniqueVex[lTestStrip[0]]
                            bPrevStripFound = True
                            break
                        elif np.linalg.norm(aVexBase - aUniqueVex[lTestStrip[0]]) < fClose:
                            setUsedStripIdx.add(iTestStripIdx)
                            lTemp = lTestStrip[-1:1:-1]
                            lTemp.extend(lFullStrip)
                            lFullStrip = lTemp
                            aVexBase = aUniqueVex[lTestStrip[-1]]
                            bPrevStripFound = True
                            break
                        # endif
                    # endfor
                    if not bPrevStripFound:
                        break
                    # endif
                # endwhile

                lFullStripLists.append(aUniqueVex[lFullStrip].tolist())
            # endif
            iStartStripIdx += 1
        # endwhile
        # print("lFullStripLists ({0}):\n{1}\n".format(len(lFullStripLists), lFullStripLists))

        return lFullStripLists

    # enddef

    ##########################################################################
    def Init(self):
        if self.sFilePathImport == "":
            xData = res.files(anytruth).joinpath("data").joinpath("labeltypes_std.json")
            with res.as_file(xData) as pathData:
                self.sFilePathImport = pathData.as_posix()
                if self.bImportFileExists:
                    self.ImportTypes()
                # endif
            # endwith
        # endif

        # Create Node Groups needed
        self.ProvideLabelNodeGroups()

    # enddef

    ##########################################################################
    def GetImportFilePath(self):
        return os.path.normpath(bpy.path.abspath(self.sFilePathImport))

    # enddef

    ##########################################################################
    def GetExportFilePath(self):
        return os.path.normpath(bpy.path.abspath(self.sFilePathExport))

    # enddef

    ##########################################################################
    def ImportTypes(self):
        self.clTypes.clear()
        lTypes = self.LoadLabelDb(self.GetImportFilePath())

        for dicType in lTypes:
            xType = self.clTypes.add()
            xType.sId = xType.name = dicType.get("sId")
            xType.colLabel = tuple(dicType.get("lColor"))
        # endfor

    # enddef

    ##########################################################################
    def ExportAppliedTypes(self):
        xPath = Path(self.GetExportFilePath())
        if not xPath.parent.exists():
            raise Exception("Export path does not exist: {0}".format(xPath.parent.as_posix()))
        # endif

        fMeterPerBU = bpy.context.scene.unit_settings.scale_length
        matBlenderToWorld = self._GetBlenderToCustomWorldMatrix()
        matBlenderToWorldRot = matBlenderToWorld.to_3x3()

        dicData = {"sId": "${filebasename}", "iColorNormValue": self.iColorNormValue}

        # Camera data
        camX = bpy.context.scene.camera
        sAnyCam = camX.get("AnyCam")
        if sAnyCam is not None:
            dicAnyCam: dict = json.loads(sAnyCam)
            if dicAnyCam is not None:
                bIsPin = anybase.config.IsConfigType(dicAnyCam, "/anycam/camera/pin:1.2")
                bIsPano = anybase.config.IsConfigType(dicAnyCam, "/anycam/camera/pano/equidist:1.2")
                bIsPanoPoly = anybase.config.IsConfigType(dicAnyCam, "/anycam/camera/pano/poly:1.2")
                bIsLut = anybase.config.IsConfigType(dicAnyCam, "/anycam/camera/lut/std:1.2")

                if bIsPin is True or bIsPano is True or bIsLut is True or bIsPanoPoly is True:
                    dicData["mCamera"] = dicAnyCam
                    dicCamData: dict = dicData["mCamera"]
                    matCamera = matBlenderToWorld @ camX.matrix_world
                    dicCamData["lAxes"] = [list(x) for x in matCamera.to_euler().to_matrix().transposed()]
                    dicCamData["lOrigin"] = [x * fMeterPerBU for x in matCamera.translation]
                    if bIsLut is True:
                        StoreLutCameraData(_dicCamData=dicCamData, _xPath=xPath.parent, _bOverwrite=False)

                    # endif
                # endif
            # endif
        # endif

        lTypes = []
        for xType in self.clAppliedTypes:
            lShaderTypes = []
            for xShaderType in xType.clShaderTypes:
                sShaderType = xShaderType.sId
                lColor = next(
                    (list(x.colLabel) for x in self.clTypes if x.sId == sShaderType),
                    None,
                )
                lShaderTypes.append({"sId": sShaderType, "lColor": lColor})
            # endfor

            dicInstances = {}
            for xInst in xType.clInstances:
                dicInst = dicInstances.get(xInst.iIdx)
                if dicInst is None:
                    dicInst = dicInstances[xInst.iIdx] = {"iIdx": xInst.iIdx}
                # endif

                # ##########################################################################################
                xBox2d = xInst.xBox2d
                if xBox2d.bIsValid is True:
                    dicInst["mBox2d"] = {
                        "lMinXY": [xBox2d.vMinXY[0], xBox2d.vMinXY[1]],
                        "lMaxXY": [xBox2d.vMaxXY[0], xBox2d.vMaxXY[1]],
                    }
                # endif

                # ##########################################################################################
                if len(xInst.sOrientId) > 0:
                    xBox3d = xInst.xBox3d

                    dicInst["mBox3d"] = {
                        "lCenter": [
                            x * fMeterPerBU
                            for x in (matBlenderToWorld @ mathutils.Vector(xBox3d.vCenter).to_4d()).to_3d()
                        ],
                        "lSize": [x * fMeterPerBU for x in xBox3d.vSize],
                        "lAxes": [
                            [x for x in matBlenderToWorldRot @ mathutils.Vector(xBox3d.vAxisX)],
                            [x for x in matBlenderToWorldRot @ mathutils.Vector(xBox3d.vAxisY)],
                            [x for x in matBlenderToWorldRot @ mathutils.Vector(xBox3d.vAxisZ)],
                        ],
                    }
                # endif

                # ##########################################################################################
                dicPoses = {}
                for xPose in xInst.clPoses:
                    dicBones = {}
                    for xBone in xPose.clBones:
                        dicBones[xBone.sId] = {
                            "sParent": xBone.sParent,
                            "lChildren": [x.sId for x in xBone.clChildren],
                            "lHead": [
                                x * fMeterPerBU
                                for x in (matBlenderToWorld @ mathutils.Vector(xBone.vHead).to_4d()).to_3d()
                            ],
                            "lTail": [
                                x * fMeterPerBU
                                for x in (matBlenderToWorld @ mathutils.Vector(xBone.vTail).to_4d()).to_3d()
                            ],
                            "lAxes": [
                                [x for x in matBlenderToWorldRot @ mathutils.Vector(xBone.vAxisX)],
                                [x for x in matBlenderToWorldRot @ mathutils.Vector(xBone.vAxisY)],
                                [x for x in matBlenderToWorldRot @ mathutils.Vector(xBone.vAxisZ)],
                            ],
                        }
                    # endfor bones
                    dicPoses[xPose.sId] = {"mBones": dicBones}
                # endfor poses
                if len(dicPoses) > 0:
                    dicInst["mPoses3d"] = dicPoses
                # endif

                dicVexGrpTypes = {}
                for xVexGrpType in xInst.clVexGrpTypes:
                    dicVgInst = {}
                    for xVgInst in xVexGrpType.clInstances:
                        dicVexGrp = {}
                        for xVexGrp in xVgInst.clVertexGroups:
                            lVexLists = []
                            for xVexList in xVexGrp.clVertexLists:
                                dicVL = {
                                    "sType": xVexList.eType,
                                    "lVex": [
                                        list((matBlenderToWorld @ mathutils.Vector(x.vVertex).to_4d()).to_3d())
                                        for x in xVexList.clVertices
                                    ],
                                }
                                lVexLists.append(dicVL)
                            # endfor vertex lists
                            dicVexGrp[xVexGrp.sId] = lVexLists
                        # endfor vertex groups
                        dicVgInst[xVgInst.name] = dicVexGrp
                    # endfor vertex group instances
                    dicVexGrpTypes[xVexGrpType.sId] = dicVgInst
                # endfor vertex groups
                if len(dicVexGrpTypes) > 0:
                    dicInst["mVertexGroups"] = dicVexGrpTypes
                # endif

            # endfor instances

            lTypes.append(
                {
                    "sId": xType.sId,
                    "lColor": list(xType.colLabel),
                    "iInstanceCount": len(xType.clInstances),
                    "iShaderMaxInstCnt": xType.iShaderMaxInstCnt,
                    "lShaderTypes": lShaderTypes,
                    "mInstances": dicInstances,
                }
            )
        # endfor

        dicData.update({"lTypes": lTypes})

        anybase.config.Save(
            (xPath.parent.as_posix(), xPath.name),
            dicData,
            sDTI="/anytruth/render/labeltypes/raw:1.0",
        )

    # enddef

    ##########################################################################
    def ExportPos3dInfo(self):
        xPath = Path(self.GetExportFilePath())
        if not xPath.parent.exists():
            raise Exception("Export path does not exist: {0}".format(xPath.parent.as_posix()))
        # endif

        fMeterPerBU = bpy.context.scene.unit_settings.scale_length
        matBlenderToWorld = self._GetBlenderToCustomWorldMatrix()

        dicData = {"sId": "${filebasename}", "mCamera": {}}  # , "lOffsetPos3d": list(self.vOffsetPos3d)}

        # Camera data
        camX = bpy.context.scene.camera
        sAnyCam = camX.get("AnyCam")
        if sAnyCam is not None:
            dicAnyCam = json.loads(sAnyCam)
            if dicAnyCam is not None:
                bIsPin = anybase.config.IsConfigType(dicAnyCam, "/anycam/camera/pin:1.2")
                bIsPano = anybase.config.IsConfigType(dicAnyCam, "/anycam/camera/pano/equidist:1.2")
                bIsPanoPoly = anybase.config.IsConfigType(dicAnyCam, "/anycam/camera/pano/poly:1.2")
                bIsLut = anybase.config.IsConfigType(dicAnyCam, "/anycam/camera/lut/std:1.2")
                if bIsPin is True or bIsPano is True or bIsPanoPoly or bIsLut is True:
                    dicData["mCamera"].update(dicAnyCam)
                    if bIsLut is True:
                        StoreLutCameraData(_dicCamData=dicData["mCamera"], _xPath=xPath.parent, _bOverwrite=False)

                    # endif
                # endif
            # endif
        # endif

        matCamera = matBlenderToWorld @ camX.matrix_world
        dicCamData = dicData["mCamera"]
        dicCamData["lAxes"] = [list(x) for x in matCamera.to_euler().to_matrix().transposed()]
        dicCamData["lOrigin"] = [x * fMeterPerBU for x in matCamera.translation]

        anybase.config.Save(
            (xPath.parent.as_posix(), xPath.name),
            dicData,
            sDTI="/anytruth/render/pos3d/raw:1.1",
        )

    # enddef

    ##########################################################################
    def _ProvideLabelMaterials(self):
        iMaxInstCnt = 0
        lTypeIds = []

        for xAppType in self.clAppliedTypes:
            iMaxInstCnt = max(len(xAppType.clInstances) + 1, iMaxInstCnt)
            lTypeIds.append(xAppType.sId)
        # endfor

        iLabelTypeCnt = len(lTypeIds)

        dicMatDefault = {}
        dicMatArma = {}

        for iIdx, sTypeId in enumerate(lTypeIds):
            matLabel = CLabel(
                iLabelTypeCount=iLabelTypeCnt,
                iMaxInstCount=iMaxInstCnt,
                iId=iIdx,
                sName=sTypeId,
                eLabelShaderType=self.xAnyCamConfig.eLabelShaderType,
                bForce=True,
            )

            dicMatDefault[sTypeId] = matLabel

            clSkel = self.clAppliedTypes[sTypeId].clSkeletons
            if self.bEnableArmatureSelfOcclusion is True and len(clSkel) > 0:
                # create one materials per skeleton
                # When creating vertex color layer for objects with these materials
                # at a later stage, need to take into account full shader type list,
                # as there may be more shader types than defined by the skeleton.
                # The materials created here only reference a vertex color layer
                # and attach its' red channel to the shader type input.
                dicMatSkel = {}
                for sSkelId in clSkel.keys():
                    matSkel = CLabelSkeleton(
                        iLabelTypeCount=iLabelTypeCnt,
                        iMaxInstCount=iMaxInstCnt,
                        iId=iIdx,
                        sLabelId=sTypeId,
                        sSkelId=sSkelId,
                        eLabelShaderType=self.xAnyCamConfig.eLabelShaderType,
                    )

                    dicMatSkel[sSkelId] = matSkel
                # endfor

                dicMatArma[sTypeId] = dicMatSkel
            # endif
        # endfor

        return {
            "iMaxInstCnt": iMaxInstCnt,
            "iLabelTypeCnt": iLabelTypeCnt,
            "dicTypes": {"DEFAULT": dicMatDefault, "ARMATURE_MESH": dicMatArma},
        }

    # enddef

    ############################################################################################################
    def ProvideLabelNodeGroups(self):
        lNodeGroups = []
        lNodeGroups.append(node.grp.material_label_value.Create(iLabelTypeCount=1, iMaxInstCount=1, bUseFakeUser=True))
        lNodeGroups.append(node.grp.shader_label_value.Create(bForce=True, bUseFakeUser=True))
        lNodeGroups.append(node.shader.label_diffuse.Create(bForce=True, bUseFakeUser=True))
        lNodeGroups.append(node.shader.label_emission.Create(bForce=True, bUseFakeUser=True))

        lNodeGroupNames = [x.name for x in lNodeGroups]
        # Ensure that node groups of the given names do not have copies.
        anyblend.util.node.MakeMaterialNodeGroupsUnique(lNodeGroupNames)

    # enddef

    ############################################################################################################
    def _AddLabelTypes(self, _lTypes, _lPath, _dicTypes, _dicDefaults):
        for sId in _dicTypes:
            dicType = _dicTypes.get(sId)
            if not isinstance(dicType, dict):
                continue
            # endif
            dicRes = anybase.config.CheckConfigType(dicType, "/anytruth/labeldb/type:1.0")
            if not dicRes.get("bOK"):
                continue
            # endif

            lPath = _lPath.copy()
            lPath.append(sId)
            sTypeId = ".".join(lPath)

            lColor = dicType.get("lColor", _dicDefaults.get("lColor")).copy()

            _lTypes.append({"sId": sTypeId, "lColor": lColor})

            dicSubTypes = dicType.get("mTypes")
            if dicSubTypes is not None:
                dicDefaults = _dicDefaults.copy()
                dicDefaults["lColor"] = lColor

                self._AddLabelTypes(_lTypes, lPath, dicSubTypes, dicDefaults)
            # endif
        # endfor

    # enddef

    ############################################################################################################
    def LoadLabelDb(self, _sFpLabelDb):
        if not os.path.exists(_sFpLabelDb):
            raise CAnyExcept("Label types file does not exist: {0}".format(_sFpLabelDb))
        # endif

        pathCfg = anybase.path.MakeNormPath(_sFpLabelDb)
        dicCfg = anybase.config.Load(pathCfg, sDTI="/anytruth/labeldb:1.0")

        xParser = CAnyCML(sImportPath=pathCfg.parent.as_posix())
        dicCfg = xParser.Process(dicCfg)

        dicTypes = dicCfg.get("mTypes")
        if dicTypes is None:
            raise CAnyExcept("Label types config file does not contain 'mTypes' element")
        # endif

        lTypes = [{"sId": "None", "lColor": [0, 0, 0]}]

        dicDefaults = {"lColor": [0, 0, 0]}

        self._AddLabelTypes(lTypes, [], dicTypes, dicDefaults)

        return lTypes

    # enddef

    ##########################################################################
    def CreateAnyTruthCollection(self, _sName):
        anyblend.collection.MakeRootLayerCollectionActive(bpy.context)
        clRoot = anyblend.collection.GetCollection("AnyTruth")
        # print(f"Root collection: {clRoot}")

        if clRoot is None:
            clRoot = anyblend.collection.CreateCollection(bpy.context, "AnyTruth")
        # endif
        # print(f"Root collection: {clRoot}")

        anyblend.collection.SetActiveCollection(bpy.context, clRoot.name)
        clRoot.AnyTruth.xLabel.bIgnore = True

        sClName = "AnyTruth.{0}".format(_sName)
        # print(f"sClName: {sClName}")

        clBox = anyblend.collection.ProvideCollection(bpy.context, sClName, bEnsureLayerCollectionExists=True)

        # print(f"Set active collection to {clBox.name}")
        anyblend.collection.SetActiveCollection(bpy.context, clBox.name)
        # print(f"Remove collection objects in {clBox.name}")
        anyblend.collection.RemoveCollectionObjects(clBox.name)

    # enddef

    ##########################################################################
    def CreateBoxes3d(self):
        self.CreateAnyTruthCollection("Boxes3d")

        for xAppType in self.clAppliedTypes:
            for xAppInst in xAppType.clInstances:
                if len(xAppInst.sOrientId) == 0:
                    continue
                # endif
                sName = "AT.Label.Box3d.{0}.{1:03d}".format(xAppType.sId, xAppInst.iIdx)
                xBox3d = xAppInst.xBox3d

                objX = bpy.data.objects.get(sName)
                if objX is None:
                    objX = anyblend.object.CreateObject(bpy.context, sName)
                # endif
                mshX = objX.data

                fSX, fSY, fSZ = tuple(xBox3d.vSize)
                fSX2 = fSX / 2.0
                fSY2 = fSY / 2.0
                fSZ2 = fSZ / 2.0

                lVex = [
                    (-fSX2, -fSY2, -fSZ2),
                    (fSX2, -fSY2, -fSZ2),
                    (fSX2, fSY2, -fSZ2),
                    (-fSX2, fSY2, -fSZ2),
                    (-fSX2, -fSY2, fSZ2),
                    (fSX2, -fSY2, fSZ2),
                    (fSX2, fSY2, fSZ2),
                    (-fSX2, fSY2, fSZ2),
                ]

                lEdges = [
                    (0, 1),
                    (1, 2),
                    (2, 3),
                    (3, 0),
                    (4, 5),
                    (5, 6),
                    (6, 7),
                    (7, 4),
                    (0, 4),
                    (1, 5),
                    (2, 6),
                    (3, 7),
                ]

                mshX.from_pydata(lVex, lEdges, [])
                mshX.update(calc_edges=True)

                aMatrix = np.array([list(xBox3d.vAxisX), list(xBox3d.vAxisY), list(xBox3d.vAxisZ)])

                objX.matrix_world = mathutils.Matrix(aMatrix.transpose()).to_4x4()
                objX.location = tuple(xBox3d.vCenter)
            # endfor
        # endfor
        # Ensure that location and matrix_world properties agree.
        anyblend.viewlayer.Update()

    # enddef

    ##########################################################################
    def CreatePoses(self):
        self.CreateAnyTruthCollection("Poses")

        for xAppType in self.clAppliedTypes:
            sTypeId = xAppType.sId

            for xAppInst in xAppType.clInstances:
                iInstIdx = xAppInst.iIdx

                for xPose in xAppInst.clPoses:
                    sPoseId = xPose.sId

                    sName = "AT.Label.Pose.{0}.{1:03d}.{2}".format(sTypeId, iInstIdx, sPoseId)

                    lBoneIds = [x.sId for x in xPose.clBones]
                    lVex = []
                    lEdges = []

                    for iBoneIdx, xBone in enumerate(xPose.clBones):
                        lVex.append(tuple(xBone.vHead))

                        lChildren = [x.sId for x in xBone.clChildren]

                        for sChild in lChildren:
                            lEdges.append((iBoneIdx, lBoneIds.index(sChild)))
                        # endfor children
                    # endfor bones

                    objX = bpy.data.objects.get(sName)
                    if objX is None:
                        objX = anyblend.object.CreateObject(bpy.context, sName)
                    # endif
                    mshX = objX.data
                    mshX.from_pydata(lVex, lEdges, [])
                    mshX.update(calc_edges=True)
                # endfor poses
            # endfor instances
        # endfor types

    # enddef

    ##########################################################################
    def CreateVertexGroups(self):
        self.CreateAnyTruthCollection("VertexGroups")

        for xAppType in self.clAppliedTypes:
            # sTypeId = xAppType.sId

            for xAppInst in xAppType.clInstances:
                iInstIdx = xAppInst.iIdx

                for xVexGrpType in xAppInst.clVexGrpTypes:
                    sVgLabelType = xVexGrpType.sId

                    for xVgInst in xVexGrpType.clInstances:
                        # sVgInst = xVgInst.name

                        for xVexGrp in xVgInst.clVertexGroups:
                            sVgId = xVexGrp.sId
                            sVgType = xVexGrp.sType

                            if sVgType == "ls":
                                for iIdx, xVexList in enumerate(xVexGrp.clVertexLists):
                                    sName = "AT.Label.VexGrp.{0:03d}.{1}.{2:03d}.{3}.{4}.{5:03d}".format(
                                        iInstIdx,
                                        sVgLabelType,
                                        xVgInst.iIdx,
                                        sVgId,
                                        sVgType,
                                        iIdx,
                                    )
                                    lVex = []
                                    for xVex in xVexList.clVertices:
                                        lVex.append(tuple(xVex.vVertex))
                                    # endfor vertices
                                    lEdges = [[i, i + 1] for i in range(len(xVexList.clVertices) - 1)]

                                    objX = bpy.data.objects.get(sName)
                                    if objX is None:
                                        objX = anyblend.object.CreateObject(bpy.context, sName)
                                    # endif
                                    mshX = objX.data
                                    mshX.from_pydata(lVex, lEdges, [])
                                    mshX.update(calc_edges=True)
                                # endfor vertex lists
                            else:
                                raise Exception(
                                    "Unsupported vertex group type '{0}' for vertex group '{1}'".format(sVgType, sVgId)
                                )
                            # endif
                        # endfor vertex groups
                    # endfor shader instance
                # endfor vertex group label type
            # endfor instances
        # endfor types

    # enddef


# endclass


###################################################################################
# def ApplyMovement(self):
# 	clRoot = anyblend.collection.GetRootCollection(bpy.context)
# 	self.clObjectData.clear()

# 	# Add None type to applied types with single instance
# 	# lNames = [x.name for x in self.clTypes]
# 	xTypeNone = self.clTypes.get("None")
# 	if xTypeNone is None:
# 		raise Exception("No labeltype 'None' defined")
# 	# endif
# 	self.clAppliedTypes.clear()
# 	xAppType = self.clAppliedTypes.add()
# 	xAppType.sId = xAppType.name = xTypeNone.sId
# 	xAppType.colLabel = xTypeNone.colLabel

# 	##########################################################################################
# 	# Add label data from scene
# 	self._AddLabelData(clRoot, "NONE", "None", None, None)

# 	xMatMove = CMovement(sLayerName="AT.Movement", sName="Default", bForce=True)
# 	matMove = xMatMove.xMaterial

# 	iFrameDelta = 1
# 	iOrigFrame = bpy.context.scene.frame_current
# 	bpy.context.scene.frame_current += iFrameDelta

# 	xDepsGraph = bpy.context.evaluated_depsgraph_get()

# 	# Store all vertex positions of future frame
# 	dicObjFuture = {}
# 	for xObjData in self.clObjectData:
# 		objOrigX = bpy.data.objects.get(xObjData.sId)
# 		objX = objOrigX.evaluate_get(xDepsGraph)

# 		mWorld = objX.matrix_world
# 		mWorldT = np.array(mWorld.to_3x3()).transpose()
# 		mTrans = np.array(mWorld.translation)
# 		meshX = objX.to_mesh()

# 		iVexCnt = len(meshX.vertices)
# 		aVex = np.empty(iVexCnt*3, dtype=np.float64)
# 		meshX.vertices.foreach_get('co', aVex)
# 		aVex.shape = (iVexCnt, 3)
# 		aVex = (aVex @ mWorldT) + mTrans

# 		dicObjFuture[xObjData.sId] = aVex
# 		objX.to_mesh_clear()
# 	# endfor

# 	# Go back to original frame
# 	bpy.context.scene.frame_current = iOrigFrame
# 	xDepsGraph = bpy.context.evaluated_depsgraph_get()

# 	# Evaluate movement vertex colors and set materials of objects
# 	for xObjData in self.clObjectData:
# 		objOrigX = bpy.data.objects.get(xObjData.sId)
# 		objX = objOrigX.evaluate_get(xDepsGraph)

# 		for xMesh in xObjData.clMeshes:
# 			sMeshId = xMesh.sId
# 			mshX = bpy.data.meshes[sMeshId]
# 			iMatCnt = len(mshX.materials)
# 			# Switch off LOD as workaround for problems with Grasswald.
# 			# I cannot find bug where LOD objects are not switched to
# 			# render LOD.
# 			# The LOD feature has been removed in Blender 2.93
# 			if bpy.app.version <= (2, 84, 0):
# 				mshX.lod_enabled = False

# 			if iMatCnt == 0:
# 				mshX.materials.append(matMove)
# 			else:
# 				for iMatIdx in range(iMatCnt):
# 					matX = mshX.materials[iMatIdx]
# 					if matX is not None:
# 						matX.use_fake_user = True
# 						mshX.materials[iMatIdx] = matMove
# 					else:
# 						mshX.materials[iMatIdx] = matMove
# 					# endif

# 				# endfor materials
# 			# endfor
# 		# endfor meshes
# 	# endfor objects

# 	#######################################################################
# 	# Replace world shader with label shader

# 	# Get currently selected world
# 	worldAct = bpy.context.scene.world
# 	if worldAct is None:
# 		raise Exception("Scene has no world shader set")
# 	# endif

# 	# Store current world id
# 	self.xLabelSetProp.sWorldId = worldAct.name

# 	# Look for "AT.Label" world
# 	worldATD = bpy.data.worlds.get("AT.Depth")
# 	if worldATD is None:
# 		# Create the label world shader
# 		worldATD = bpy.data.worlds.new(name="AT.Depth")
# 		worldATD.use_nodes = True

# 		nodBg = worldATD.node_tree.nodes.get("Background")
# 		if nodBg is None:
# 			raise Exception("Newly created world shader does not contain 'Background' node")
# 		# endif

# 		nodBg.use_custom_color = True
# 		nodBg.inputs["Color"].default_value = (1e6, 1e6, 1e6, 1)
# 		nodBg.inputs["Strength"].default_value = 1.25
# 	# endif

# 	# Set AT.Label shader as world shader
# 	bpy.context.scene.world = worldATD

# # enddef
