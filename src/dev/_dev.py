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

# lEdgeIdx = [x.index for i, x in enumerate(mshX.loops) if mshX.vertex_colors[0].data[i].color[0] > 0.0]
# print(lEdgeIdx)
lColVexIdx = [
    x.vertex_index
    for i, x in enumerate(mshX.loops)
    if mshX.vertex_colors[0].data[i].color[0] > 0.0
]
# print("lColVexIdx ({0}):\n{1}\n".format(len(lColVexIdx), lColVexIdx))

# Don't do this, since it also includes edges where only one of the vertices has the color
# lEdgeIdx = [x.edge_index for i, x in enumerate(mshX.loops) if mshX.vertex_colors[0].data[i].color[0] > 0.0]
# print("lEdgeIdx ({0}):\n{1}\n".format(len(lEdgeIdx), lEdgeIdx))

lEdgeIdx = [x.index for x in mshX.edges if all((v in lColVexIdx for v in x.vertices))]
# print("lEdgeIdx ({0}):\n{1}\n".format(len(lEdgeIdx), lEdgeIdx))

lEdgeVexIdx = [[mshX.edges[i].vertices[0], mshX.edges[i].vertices[1]] for i in lEdgeIdx]
# print("lEdgeVexIdx ({0}):\n{1}\n".format(len(lEdgeVexIdx), lEdgeVexIdx))

lVexIdx = list(set([i for lSublist in lEdgeVexIdx for i in lSublist]))
# print("lVexIdx ({0}):\n{1}\n".format(len(lVexIdx), lVexIdx))

aVex = np.array([list(mshX.vertices[i].co) for i in lVexIdx])
# # # print("lVex:")
# # # print(lVex)
# # # print("")

lMyEdgeVexIdx = [
    [lVexIdx.index(lEdge[0]), lVexIdx.index(lEdge[1])] for lEdge in lEdgeVexIdx
]
print("lMyEdgeVexIdx ({0}):\n{1}\n".format(len(lMyEdgeVexIdx), lMyEdgeVexIdx))

lSameVexIdx = [
    lEdge
    for lEdge in lMyEdgeVexIdx
    if np.linalg.norm(aVex[lEdge[0]] - aVex[lEdge[1]]) < 1e-6
]
# print("lSameVexIdx ({0}):\n{1}\n".format(len(lSameVexIdx), lSameVexIdx))

lSameRefIdx = np.arange(aVex.shape[0]).tolist()
# print(lSameRefIdx)

for lSameIdx in lSameVexIdx:
    lSameRefIdx[max(lSameIdx)] = min(lSameIdx)
# endfor
print("lSameRefIdx ({0}):\n{1}\n".format(len(lSameRefIdx), lSameRefIdx))

lUniqueVexIdx = list(set(lSameRefIdx))
print(
    "lUniqueVexIdx ({0}, max: {1}):\n{2}\n".format(
        len(lUniqueVexIdx), max(lUniqueVexIdx), lUniqueVexIdx
    )
)
iUniqueVexCnt = len(lUniqueVexIdx)

aUniqueVex = aVex[lUniqueVexIdx]
# print("aUniqueVex ({0}):\n{1}\n".format(len(aUniqueVex), aUniqueVex))

lMyEdgeVexIdx = [
    [lSameRefIdx[lEdge[0]], lSameRefIdx[lEdge[1]]]
    for lEdge in lMyEdgeVexIdx
    if lSameRefIdx[lEdge[0]] != lSameRefIdx[lEdge[1]]
]
print("lMyEdgeVexIdx ({0}):\n{1}\n".format(len(lMyEdgeVexIdx), lMyEdgeVexIdx))

# Reduce to unique vertex indices
lMyEdgeVexIdx = [
    [lUniqueVexIdx.index(lEdge[0]), lUniqueVexIdx.index(lEdge[1])]
    for lEdge in lMyEdgeVexIdx
]
print("lMyEdgeVexIdx ({0}):\n{1}\n".format(len(lMyEdgeVexIdx), lMyEdgeVexIdx))

setMyEdgeVexIdxHash = set(
    [min(lEdge) * iUniqueVexCnt + max(lEdge) for lEdge in lMyEdgeVexIdx]
)
print(
    "setMyEdgeVexIdxHash ({0}):\n{1}\n".format(
        len(setMyEdgeVexIdxHash), setMyEdgeVexIdxHash
    )
)

lMyUniqueEdge = [
    [int(h / iUniqueVexCnt), h % iUniqueVexCnt] for h in set(setMyEdgeVexIdxHash)
]
print("lMyUniqueEdge ({0}):\n{1}\n".format(len(lMyUniqueEdge), lMyUniqueEdge))

# Parent and Child edges of each edge
lMyConnect = [
    [
        [
            iTestEdgeIdx
            for iTestEdgeIdx, lTestEdge in enumerate(lMyUniqueEdge)
            if iTestEdgeIdx != iEdgeIdx
            and any((iTestVexIdx == iVexIdx for iTestVexIdx in lTestEdge))
        ]
        for iVexIdx in lEdge
    ]
    for iEdgeIdx, lEdge in enumerate(lMyUniqueEdge)
]
print("lMyConnect ({0}):\n{1}\n".format(len(lMyConnect), lMyConnect))

# Find all start edges, if any
lStartEdges = [i for i, lC in enumerate(lMyConnect) if len(lC[0]) == 0]
print("lStartEdges ({0}):\n{1}\n".format(len(lStartEdges), lStartEdges))

# Find connected edges from start edges
lPolygons = []
for iStartIdx in lStartEdges:
    lPoly = []
    iIdx = iStartIdx
    while True:
        lEdge = lMyUniqueEdge[iIdx]
        lPoly.append(lEdge[0])
        lCE = lMyConnect[iIdx]
        if len(lCE[1]) == 0:
            break
        # endif
        iIdx = lCE[1][0]
    # endwhile
    lPoly.append(lEdge[1])
    lPolygons.append(lPoly)
# endfor

print("lPolygons ({0}):\n{1}\n".format(len(lPolygons), lPolygons))
