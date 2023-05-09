#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \_dev.py
# Created Date: Monday, June 14th 2021, 2:08:18 pm
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

from numpy.testing._private.utils import assert_equal
import bpy
import numpy as np

xDG = bpy.context.evaluated_depsgraph_get()

objOrigX = bpy.data.objects["HW4L.Surface"]
objX = objOrigX.evaluated_get(xDG)
vglX = objX.vertex_groups

lNames = [x.name for x in vglX]
print(lNames)

lAtVg = [x.name for x in vglX if x.name.startswith("AT.Label;")]
print(lAtVg)

vgX = vglX[lAtVg[0]]
print(vgX)

iVgIdx = vgX.index
print("VG index: {0}".format(iVgIdx))

mWorld = objX.matrix_world

mWorldT = np.array(mWorld.to_3x3()).transpose()
mTrans = np.array(mWorld.translation)

mshX = objX.to_mesh()
# mshX = objOrigX.data

xVexCol = mshX.vertex_colors.get("AT.Label")
tRGB = (1 / 255, 1 / 255, 1 / 255)

fPrec = 1 / 512.0
lColVexIdx = [
    x.vertex_index
    for i, x in enumerate(mshX.loops)
    if (
        abs(xVexCol.data[i].color[0] - tRGB[0]) < fPrec
        and abs(xVexCol.data[i].color[1] - tRGB[1]) < fPrec
        and abs(xVexCol.data[i].color[2] - tRGB[2]) < fPrec
    )
]
# print("lColVexIdx ({0}):\n{1}\n".format(len(lColVexIdx), lColVexIdx))

# for iVexIdx in lColVexIdx:
# 	mshX.vertices[iVexIdx].select = True
# # endfor

# # lEdgeIdx = [x.index for i, x in enumerate(mshX.loops) if mshX.vertex_colors[0].data[i].color[0] > 0.0]
# # print(lEdgeIdx)
# # lColVexIdx = [x.vertex_index for i, x in enumerate(mshX.loops) if mshX.vertex_colors[0].data[i].color[0] > 0.0]
# # print("lColVexIdx ({0}):\n{1}\n".format(len(lColVexIdx), lColVexIdx))

# # Don't do this, since it also includes edges where only one of the vertices has the color
# # lEdgeIdx = [x.edge_index for i, x in enumerate(mshX.loops) if mshX.vertex_colors[0].data[i].color[0] > 0.0]
# # print("lEdgeIdx ({0}):\n{1}\n".format(len(lEdgeIdx), lEdgeIdx))

lEdgeIdx = [x.index for x in mshX.edges if all((v in lColVexIdx for v in x.vertices))]
# print("lEdgeIdx ({0}):\n{1}\n".format(len(lEdgeIdx), lEdgeIdx))

lEdgeVexIdx = [[mshX.edges[i].vertices[0], mshX.edges[i].vertices[1]] for i in lEdgeIdx]
# print("lEdgeVexIdx ({0}):\n{1}\n".format(len(lEdgeVexIdx), lEdgeVexIdx))

lVexIdx = list(set([i for lSublist in lEdgeVexIdx for i in lSublist]))
# print("lVexIdx ({0}):\n{1}\n".format(len(lVexIdx), lVexIdx))

aVex = np.array([list(mshX.vertices[i].co) for i in lVexIdx])

lMyEdgeVexIdx = [
    [lVexIdx.index(lEdge[0]), lVexIdx.index(lEdge[1])] for lEdge in lEdgeVexIdx
]
# print("lMyEdgeVexIdx ({0}):\n{1}\n".format(len(lMyEdgeVexIdx), lMyEdgeVexIdx))

lSameVexIdx = [
    lEdge
    for lEdge in lMyEdgeVexIdx
    if np.linalg.norm(aVex[lEdge[0]] - aVex[lEdge[1]]) < 1e-6
]
# print("lSameVexIdx ({0}):\n{1}\n".format(len(lSameVexIdx), lSameVexIdx))

lSameRefIdx = np.arange(aVex.shape[0]).tolist()
# # print(lSameRefIdx)

for lSameIdx in lSameVexIdx:
    lSameRefIdx[max(lSameIdx)] = min(lSameIdx)
# endfor
# print("lSameRefIdx ({0}):\n{1}\n".format(len(lSameRefIdx), lSameRefIdx))

lUniqueVexIdx = list(set(lSameRefIdx))
# print("lUniqueVexIdx ({0}, max: {1}):\n{2}\n".format(len(lUniqueVexIdx), max(lUniqueVexIdx), lUniqueVexIdx))
iUniqueVexCnt = len(lUniqueVexIdx)

aUniqueVex = aVex[lUniqueVexIdx]
# # print("aUniqueVex ({0}):\n{1}\n".format(len(aUniqueVex), aUniqueVex))

lMyEdgeVexIdx = [
    [lSameRefIdx[lEdge[0]], lSameRefIdx[lEdge[1]]]
    for lEdge in lMyEdgeVexIdx
    if lSameRefIdx[lEdge[0]] != lSameRefIdx[lEdge[1]]
]
# print("lMyEdgeVexIdx ({0}):\n{1}\n".format(len(lMyEdgeVexIdx), lMyEdgeVexIdx))

# Reduce to unique vertex indices
lMyEdgeVexIdx = [
    [lUniqueVexIdx.index(lEdge[0]), lUniqueVexIdx.index(lEdge[1])]
    for lEdge in lMyEdgeVexIdx
]
# print("lMyEdgeVexIdx ({0}):\n{1}\n".format(len(lMyEdgeVexIdx), lMyEdgeVexIdx))

setMyEdgeVexIdxHash = set(
    [min(lEdge) * iUniqueVexCnt + max(lEdge) for lEdge in lMyEdgeVexIdx]
)
# print("setMyEdgeVexIdxHash ({0}):\n{1}\n".format(len(setMyEdgeVexIdxHash), setMyEdgeVexIdxHash))

lMyUniqueEdge = [
    [int(h / iUniqueVexCnt), h % iUniqueVexCnt] for h in set(setMyEdgeVexIdxHash)
]
print("lMyUniqueEdge ({0}):\n{1}\n".format(len(lMyUniqueEdge), lMyUniqueEdge))

lStripLists = []
lAllStripVex = []
bHasLoop = False

for lStartEdge in lMyUniqueEdge:
    if lStartEdge[0] in lAllStripVex:
        continue
    # endif
    lEdge = lStartEdge.copy()
    # print("Start Edge: {0}".format(lStartEdge))
    lStrip = []
    lStripVex = []
    while True:
        if lEdge[0] in lStripVex:
            print("Loop: {0}".format(lEdge))
            bHasLoop = True
            break
        # endif
        lAllStripVex.append(lEdge[0])
        lStripVex.append(lEdge[0])
        lStrip.append(lEdge)
        lNextEdge = next(
            (x for x in lMyUniqueEdge if x[0] == lEdge[1] and x[1] not in lStripVex),
            None,
        )
        if lNextEdge is None:
            lNextEdge = next(
                (
                    x
                    for x in lMyUniqueEdge
                    if x[1] == lEdge[1] and x[0] not in lStripVex
                ),
                None,
            )
            if lNextEdge is None:
                if lEdge[1] not in lStripVex:
                    lStripVex.append(lEdge[1])
                    lAllStripVex.append(lEdge[1])
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
            (x for x in lMyUniqueEdge if x[1] == lEdge[0] and x[0] not in lStripVex),
            None,
        )
        if lNextEdge is None:
            lNextEdge = next(
                (
                    x
                    for x in lMyUniqueEdge
                    if x[0] == lEdge[0] and x[1] not in lStripVex
                ),
                None,
            )
            if lNextEdge is None or lNextEdge[0] in lStripVex:
                if lEdge[0] not in lStripVex:
                    lStripVex.insert(0, lEdge[0])
                    lAllStripVex.append(lEdge[0])
                # endif
                break
            # endif
            lEdge = [lNextEdge[1], lNextEdge[0]]
        else:
            lEdge = lNextEdge
        # endif
        if lEdge[0] in lStripVex:
            print("Loop: {0}".format(lEdge))
            bHasLoop = True
            break
        # endif
        lAllStripVex.append(lEdge[0])
        lStripVex.insert(0, lEdge[0])
        lStrip.insert(0, lEdge)
    # endfor
    # print("lStrip ({0}):\n{1}\n".format(len(lStrip), lStrip))

    if bHasLoop:
        break
    # endif
    lStripLists.append(lStripVex)
# endfor
print("lStripLists ({0}):\n{1}\n".format(len(lStripLists), lStripLists))

# # Parent and Child edges of each edge
# lMyConnect = [
# 	[
# 		[
# 			iTestEdgeIdx for iTestEdgeIdx, lTestEdge in enumerate(lMyUniqueEdge)
# 				if iTestEdgeIdx != iEdgeIdx and any((iTestVexIdx == iVexIdx for iTestVexIdx in lTestEdge))
# 		] for iVexIdx in lEdge
# 	] for iEdgeIdx, lEdge in enumerate(lMyUniqueEdge)
# ]
# print("lMyConnect ({0}):\n{1}\n".format(len(lMyConnect), lMyConnect))

# # Find all start edges, if any
# lStartEdges = [i for i, lC in enumerate(lMyConnect) if len(lC[0]) == 0]
# print("lStartEdges ({0}):\n{1}\n".format(len(lStartEdges), lStartEdges))

# # Find connected edges from start edges
# lPolygons = []
# for iStartIdx in lStartEdges:
# 	lPoly = []
# 	iIdx = iStartIdx
# 	while True:
# 		lEdge = lMyUniqueEdge[iIdx]
# 		lPoly.append(lEdge[0])
# 		lCE = lMyConnect[iIdx]
# 		if len(lCE[1]) == 0:
# 			break
# 		# endif
# 		iIdx = lCE[1][0]
# 	# endwhile
# 	lPoly.append(lEdge[1])
# 	lPolygons.append(lPoly)
# # endfor

# print("lPolygons ({0}):\n{1}\n".format(len(lPolygons), lPolygons))

lPolygons = lStripLists
aVexStart = np.array([aUniqueVex[lPoly[0]] for lPoly in lPolygons])
print("aVexStart ({0}):\n{1}\n".format(len(aVexStart), aVexStart))

aVexEnd = np.array([aUniqueVex[lPoly[-1]] for lPoly in lPolygons])
print("aVexEnd ({0}):\n{1}\n".format(len(aVexEnd), aVexEnd))

aNext = np.arange(len(aVexStart))
aNext.fill(-1)
aPrev = aNext.copy()

for iStart, aVex in enumerate(aVexStart):
    aNorm = np.linalg.norm(aVexEnd - aVex, axis=1)
    # print("aNorm ({0}):\n{1}\n".format(len(aNorm), aNorm))
    aIdx = np.argwhere(aNorm < 1e-3)
    # print("aIdx ({0}):\n{1}\n".format(len(aIdx), aIdx))
    # break
    if len(aIdx) > 0:
        aNext[aIdx[0]] = iStart
        aPrev[iStart] = aIdx[0]
    # endif
# endfor
print("aNext ({0}):\n{1}\n".format(len(aNext), aNext))
print("aPrev ({0}):\n{1}\n".format(len(aPrev), aPrev))

aStart = np.argwhere(aPrev == -1)
# print("aStart ({0}):\n{1}\n".format(len(aStart), aStart))
if len(aStart) == 0:
    aStart = [[0]]
# endif

lConnections = []
for aS in aStart:
    iIdx = aS[0]
    lC = [iIdx]
    while True:
        iIdx = aNext[iIdx]
        if iIdx == -1 or iIdx in lC:
            break
        # endif
        lC.append(iIdx)
    # endwhile
    lConnections.append(lC)
# endfor
print("lConnections ({0}):\n{1}\n".format(len(lConnections), lConnections))

# lLineStrips = []
# for lCon in lConnections:
# 	lStrip = []
# 	for iIdx in lCon:
# 		lStrip.extend(lPolygons[iIdx])
# 	# endfor
# 	lLineStrips.append(lStrip)
# # endfor
# print("lLineStrips ({0}):\n{1}\n".format(len(lLineStrips), lLineStrips))
