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

import bpy
import numpy as np


def GetMeshVex(_objX, *, sFrame="WORLD"):

    if _objX.type != "MESH":
        raise Exception("Object '{0}' is not a mesh object".format(_objX.name))
    # endif

    if sFrame not in ["WORLD", "LOCAL", "ID"]:
        raise Exception(
            "Frame parameter must be one of 'WORLD', 'LOCAL' or 'ID', but has value '{}'.".format(
                sFrame
            )
        )
    # endif

    if sFrame == "WORLD":
        mFrame = _objX.matrix_world
    elif sFrame == "LOCAL":
        mFrame = _objX.matrix_local
    else:
        mFrame = None
    # endif

    if mFrame is not None:
        mFrameT = np.array(mFrame.to_3x3()).transpose()
        mTrans = np.array(mFrame.translation)
    # endif

    meshX = _objX.data
    iVexCnt = len(meshX.vertices)
    aVex = np.empty(iVexCnt * 3, dtype=np.float64)
    meshX.vertices.foreach_get("co", aVex)

    aVex.shape = (iVexCnt, 3)
    if mFrame is not None:
        aVex = (aVex @ mFrameT) + mTrans
    # endif

    return aVex


# enddef

#########################################################################
def EvalVexBoneWeight(_boneX, _aVex, *, sMode="FULL"):

    lAllowedModes = ["FULL", "BONE", "HEAD", "TAIL"]
    if sMode not in lAllowedModes:
        raise Exception(
            "Weight evaluation mode must be one of [{}] but is {}".format(
                ", ".join(lAllowedModes), sMode
            )
        )
    # endif

    aPosA = np.array(_boneX.head_local)
    fRadA = _boneX.head_radius
    aPosB = np.array(_boneX.tail_local)
    fRadB = _boneX.tail_radius
    fEnvDist = _boneX.envelope_distance
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
        # print(aParLen)

        # Vector perpendicular to bone
        aPerp = aRelVex - aPar
        aPerpLen = np.linalg.norm(aPerp, axis=1)
        # print(aPerpLen)

        aEnvDist = aParLen * fRadSlope + fRadA
        # print(aEnvDist)

        aLeftSel = aParLen < 0.0
        aRightSel = aParLen > fBoneLen

        aEnvDist[aLeftSel] = fRadA
        aEnvDist[aRightSel] = fRadB
        # print(aEnvDist)

        aVexDist = aPerpLen.copy()
        aVexDistA = np.linalg.norm(aRelVex, axis=1)
        aVexDistB = np.linalg.norm(_aVex - aPosB, axis=1)
        # print(aVexDistA)
        # print(aVexDistB)

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

########################################################################

objArma = bpy.data.objects["HG_Jesse"]

sBoneWeightMode = "HEAD"

# objX = bpy.data.objects["HG_Dress_Shirt_Male.001"]
# aVex = GetMeshVex(objX, sFrame="LOCAL")
# print("vPos: {}".format(vPos))

lBoneNames = [x for x in objArma.data.bones.keys() if x.startswith("AT.Label")]
iBoneCnt = len(lBoneNames)

# Create set of random colors
aColors = np.random.uniform(0.2, 1.0, (iBoneCnt + 1, 4))
aColMax = np.max(aColors[:, 0:3], axis=1)
aColors /= aColMax[:, np.newaxis]
aColors[:, 3] = 1.0
# print(aColors)
aColors[0, 0:3] = 0.0

for objX in objArma.children:
    if objX.type != "MESH":
        continue
    # endif

    aVex = GetMeshVex(objX, sFrame="LOCAL")

    lWeightsPerBone = []
    for sBoneName in lBoneNames:
        boneX = objArma.data.bones[sBoneName]
        lWeightsPerBone.append(EvalVexBoneWeight(boneX, aVex, sMode=sBoneWeightMode))
    # endfor

    aAllWeights = np.vstack(lWeightsPerBone)
    aBoneMax = np.max(aAllWeights, axis=0)
    aBoneIdx = np.argmax(aAllWeights, axis=0)
    aBoneIdx[aBoneMax < 1e-4] = -1

    meshX = objX.data
    if len(meshX.vertex_colors) == 0:
        colX = meshX.vertex_colors.new()
    else:
        colX = meshX.vertex_colors[0]
    # endif

    for iLoopIdx, xData in enumerate(colX.data):
        iVexIdx = meshX.loops[iLoopIdx].vertex_index
        iBoneIdx = aBoneIdx[iVexIdx]
        xData.color = aColors[iBoneIdx + 1 if iBoneIdx >= 0 else 0]
    # endfor

# endfor

# # print(aVexWeight)
# aVexSel = aVexWeight >= 0.99

# # Only use weights along bone
# # aVexWeight[aLeftSel] = 0.0
# # aVexWeight[aRightSel] = 0.0


# aColWeight = np.zeros(aVexWeight.shape)
# aColWeight[aVexWeight >= 1.0] = 1.0

# aCol = aColWeight[:, np.newaxis] * np.array([1,0,0,0]) + np.array([0,0,0,1])
# # print(len(aCol))
# # print(len(colX.data))
# # print(aCol)


# # aD = np.linalg.norm(aVex - aPosA, axis=1)
# # # print(aD)
# # aSel = aD <= fRadA
# # print(aSel)

# # aSel.shape = (iVexCnt)

# # objX.data.vertices.foreach_set("select", aSel)

# # aSelIdx = np.argwhere(aSel)
# # print(len(aSelIdx))
