#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \object\armature.py
# Created Date: Monday, September 20th 2021, 10:40:14 am
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
import numpy as np

import anyblend


#########################################################################
def EvalVexBoneWeight(_objArma, _sBoneName, _aVex, *, sMode="FULL"):
    """Evaluate a bone influence weight per given vertex.

    Parameters
    ----------
    _boneX : bpy.types.Bone
        The bone for which to calculate the influence weight per vertex.
    _aVex : numpy.array
        A numpy array of 3D-vectors.
    sMode : str, optional
        The mode of calculating the influence. Must be one of ["FULL", "BONE", "HEAD", "TAIL"], by default "FULL".

    Returns
    -------
    numpy.array
        An 1D-array of weights, one for each input vector.

    Raises
    ------
    Exception
        For invalid mode.
    """

    lAllowedModes = ["FULL", "BONE", "HEAD", "TAIL"]
    if sMode not in lAllowedModes:
        raise Exception(
            "Weight evaluation mode must be one of [{}] but is {}".format(
                ", ".join(lAllowedModes), sMode
            )
        )
    # endif

    boneOrigX = _objArma.data.bones.get(_sBoneName)
    boneX = _objArma.pose.bones.get(_sBoneName)
    if boneX is None:
        raise Exception(
            "Bone '{}' not found in armature '{}'".format(_sBoneName, _objArma.name)
        )
    # endif

    mWorld = _objArma.matrix_world
    aPosA = np.array((mWorld @ boneX.head.to_4d()).to_3d())
    aPosB = np.array((mWorld @ boneX.tail.to_4d()).to_3d())

    # aPosA = np.array(_objArma.matrix_local @ boneX.head_local)
    # aPosB = np.array(_objArma.matrix_local @ boneX.tail_local)

    fRadA = boneOrigX.head_radius
    fRadB = boneOrigX.tail_radius
    fEnvDist = boneOrigX.envelope_distance
    fRadDelta = fRadB - fRadA

    if sMode == "FULL" or sMode == "BONE":
        aDir = aPosB - aPosA
        fBoneLen = np.linalg.norm(aDir)
        aDir /= fBoneLen

        fRadSlope = fRadDelta / fBoneLen

        aRelVex = _aVex - aPosA
        aParLen = np.dot(aRelVex, aDir)
        # Vector along bone
        aPar = aParLen[:, np.newaxis] * aDir

        # Vector perpendicular to bone
        aPerp = aRelVex - aPar
        aPerpLen = np.linalg.norm(aPerp, axis=1)

        aEnvDist = aParLen * fRadSlope + fRadA

        aLeftSel = aParLen < 0.0
        aRightSel = aParLen > fBoneLen

        aEnvDist[aLeftSel] = fRadA
        aEnvDist[aRightSel] = fRadB

        aVexDist = aPerpLen.copy()
        aVexDistA = np.linalg.norm(aRelVex, axis=1)
        aVexDistB = np.linalg.norm(_aVex - aPosB, axis=1)

        aVexDist[aLeftSel] = aVexDistA[aLeftSel]
        aVexDist[aRightSel] = aVexDistB[aRightSel]

        aVexEnvDist = aVexDist - aEnvDist

    elif sMode == "HEAD":
        aRelVex = _aVex - aPosA
        aVexDist = np.linalg.norm(aRelVex, axis=1)
        aVexEnvDist = aVexDist - fRadA

    elif sMode == "TAIL":
        aRelVex = _aVex - aPosB
        aVexDist = np.linalg.norm(aRelVex, axis=1)
        aVexEnvDist = aVexDist - fRadB

    # endif sMode

    if fEnvDist < 1e-7:
        aVexWeight = np.zeros(aVexEnvDist.shape)
        aVexWeight[aVexEnvDist < 0.0] = 1.0

    else:
        aVexEnvDist[aVexEnvDist < 0.0] = 0.0
        aRelVexEnvDist = 1.0 - aVexEnvDist / fEnvDist
        aRelVexEnvDist[aRelVexEnvDist < 0.0] = 0.0
        aVexWeight = np.square(aRelVexEnvDist)
    # endif

    if sMode == "BONE":
        # Only use weights along bone
        aVexWeight[aLeftSel] = 0.0
        aVexWeight[aRightSel] = 0.0
    # endif

    return aVexWeight


# enddef


####################################################################
def TestRemoveLabelMeshObject(_objMesh):

    if _objMesh.type == "MESH" and _objMesh.name.startswith("AT.Label;"):

        sOrigName = _objMesh.name[9:]
        sMeshName = _objMesh.data.name
        if _objMesh.name in bpy.data.objects.keys():
            bpy.data.objects.remove(_objMesh)
        else:
            print("Object not found: {}".format(_objMesh.name))
            return
        # endif

        meshX = bpy.data.meshes.get(sMeshName)
        if meshX is not None:
            bpy.data.meshes.remove(meshX)
        # endif

        # Unhide original object
        objOrig = bpy.data.objects.get(sOrigName)
        if objOrig is not None:
            anyblend.object.Hide(objOrig, False, bHideRender=False)
        # endif

        return True
    # endif

    return False


# enddef


####################################################################
def CreateLabelMeshObject(_objMesh):

    sNewName = "AT.Label;{}".format(_objMesh.name)

    objEval = bpy.data.objects.get(sNewName)
    if objEval is not None:
        # Delete old evaluated mesh object, since the original object
        # may have changed.
        bpy.data.objects.remove(objEval)
    # endif

    objEval = anyblend.object.CreateEvaluatedMeshObject(bpy.context, _objMesh, sNewName)

    anyblend.object.Hide(_objMesh, bHide=True, bHideRender=True)

    return objEval


# enddef


####################################################################
# Create Bone Weight Vertex Color Layer
def CreateBoneWeightVexColLay(
    *,
    objArma,
    objMesh,
    lBoneNames,
    lLabelColors,
    sBoneWeightMode,
    sVexColNameLabel,
    lPreviewColors=None,
    sVexColNamePreview=None
):

    if objArma.type != "ARMATURE":
        raise Exception("Given armature object is not an armature")
    # endif

    if objMesh.type != "MESH":
        raise Exception("Given mesh object is not a mesh")
    # endif

    bGenPreview = lPreviewColors is not None and sVexColNamePreview is not None

    aVex = anyblend.object.GetMeshVex(objMesh, sFrame="WORLD")

    lWeightsPerBone = []
    for sBoneName in lBoneNames:
        lWeightsPerBone.append(
            EvalVexBoneWeight(objArma, sBoneName, aVex, sMode=sBoneWeightMode)
        )
    # endfor

    aAllWeights = np.vstack(lWeightsPerBone)
    aBoneMax = np.max(aAllWeights, axis=0)
    aBoneIdx = np.argmax(aAllWeights, axis=0)
    aBoneIdx += 1
    aBoneIdx[aBoneMax < 1e-4] = 0

    meshX = objMesh.data

    colLabel = meshX.vertex_colors.get(sVexColNameLabel)
    if colLabel is None:
        colLabel = meshX.vertex_colors.new()
        colLabel.name = sVexColNameLabel
    # endif

    # Insert color black as undefined bone index 0
    lExLabelColors = lLabelColors.copy()
    lExLabelColors.insert(0, (0, 0, 0, 0))

    if bGenPreview is True:
        colPreview = meshX.vertex_colors.get(sVexColNamePreview)
        if colPreview is None:
            colPreview = meshX.vertex_colors.new()
            colPreview.name = sVexColNamePreview
        # endif

        lExPreviewColors = lPreviewColors.copy()
        lExPreviewColors.insert(0, (0, 0, 0, 0))

    else:
        lExPreviewColors = None
    # endif

    iVexCnt = len(meshX.loops)
    aLoopVexIdx = np.empty(iVexCnt, dtype=np.int32)
    meshX.loops.foreach_get("vertex_index", aLoopVexIdx)

    for xPoly in meshX.polygons:
        iBoneIdx = aBoneIdx[aLoopVexIdx[xPoly.loop_indices[0]]]
        if iBoneIdx != 0:
            for i in xPoly.loop_indices[1:]:
                if iBoneIdx != aBoneIdx[aLoopVexIdx[i]]:
                    iBoneIdx = 0
                    break
                # endif
            # endfor
        # endif

        colBone = lExLabelColors[iBoneIdx]
        if bGenPreview is True:
            colPreviewBone = lExPreviewColors[iBoneIdx]
        # endif

        for iLoopIdx in xPoly.loop_indices:
            colLabel.data[iLoopIdx].color = colBone
            if bGenPreview is True:
                colPreview.data[iLoopIdx].color = colPreviewBone
            # endif
        # endfor
    # endfor polygons


# enddef
