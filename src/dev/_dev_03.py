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
tRGB = (3 / 255, 1 / 255, 1 / 255)

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
# print("lMyUniqueEdge ({0}):\n{1}\n".format(len(lMyUniqueEdge), lMyUniqueEdge))

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
            (x for x in lMyUniqueEdge if x[0] == lEdge[1] and x[1] not in lAllStripVex),
            None,
        )
        if lNextEdge is None:
            lNextEdge = next(
                (
                    x
                    for x in lMyUniqueEdge
                    if x[1] == lEdge[1] and x[0] not in lAllStripVex
                ),
                None,
            )
            if lNextEdge is None:
                if lEdge[1] not in lAllStripVex:
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
            (x for x in lMyUniqueEdge if x[1] == lEdge[0] and x[0] not in lAllStripVex),
            None,
        )
        if lNextEdge is None:
            lNextEdge = next(
                (
                    x
                    for x in lMyUniqueEdge
                    if x[0] == lEdge[0] and x[1] not in lAllStripVex
                ),
                None,
            )
            if lNextEdge is None or lNextEdge[1] in lAllStripVex:
                if lEdge[0] not in lAllStripVex:
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

if not bHasLoop:
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
                    if np.linalg.norm(aVexBase - aUniqueVex[lTestStrip[0]]) < 1e-3:
                        setUsedStripIdx.add(iTestStripIdx)
                        lFullStrip.extend(lTestStrip[1:])
                        aVexBase = aUniqueVex[lTestStrip[-1]]
                        bNextStripFound = True
                        break
                    elif np.linalg.norm(aVexBase - aUniqueVex[lTestStrip[-1]]) < 1e-3:
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
                    if np.linalg.norm(aVexBase - aUniqueVex[lTestStrip[-1]]) < 1e-3:
                        setUsedStripIdx.add(iTestStripIdx)
                        lTemp = lTestStrip[0:-2]
                        lTemp.extend(lFullStrip)
                        lFullStrip = lTemp
                        aVexBase = aUniqueVex[lTestStrip[0]]
                        bPrevStripFound = True
                        break
                    elif np.linalg.norm(aVexBase - aUniqueVex[lTestStrip[0]]) < 1e-3:
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

            lFullStripLists.append(lFullStrip)
        # endif
        iStartStripIdx += 1
    # endwhile
    print("lFullStripLists ({0}):\n{1}\n".format(len(lFullStripLists), lFullStripLists))
# endif has loop

# If there are more than 1 strip lists, output start and end points of each
if len(lFullStripLists) > 1:
    for iStripIdx, lStrip in enumerate(lFullStripLists):
        print(
            "{0}, first vex ({1:03d}): {2}".format(
                iStripIdx, lStrip[0], aUniqueVex[lStrip[0]]
            )
        )
        print(
            "{0}, last  vex ({1:03d}): {2}".format(
                iStripIdx, lStrip[-1], aUniqueVex[lStrip[-1]]
            )
        )
        print("")
    # endfor
# endif
