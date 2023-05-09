#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \workpad.py
# Created Date: Tuesday, June 8th 2021, 7:53:38 am
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

#%%
lA = [1, 2, 3]
lB = [4, 5, 6]

lC = lB.copy().extend(lA)
print(lC)

#%%

# import pyjson5 as json
# xFile = open("x:/_temp/data.json", "r")
# dicData = json.load(xFile)

# #%%
# import numpy as np

# aAllVex = np.array(dicData.get("aAllVex"))

# # %%

# aCtr = np.mean(aAllVex, axis=0)
# aRelVex = aAllVex - aCtr

# # %%
# aSqVex = aRelVex.transpose() @ aRelVex

# mU, mS, mVh = np.linalg.svd(aSqVex)
# # %%
# mUl = np.sum(np.square(mU), axis=1)
# mVl = np.sum(np.square(mVh), axis=1)

# # %%
# dicA = {"a": 1, "b": 2}
# lV = dicA.values()

#%%
import re


class CTest:

    m_iA: int = 1
    m_reA: re.Pattern = re.compile("A\w+")

    @classmethod
    def Test(cls):

        cls.m_iA = 2
        xMatch = cls.m_reA.match("Achtung")
        return xMatch

    # enddef

    def Test2(self):
        self.m_iA = 3
        xMatch = self.m_reA.match("Achtung")
        return xMatch

    # enddef


# endclass

print(CTest.__annotations__)
print(CTest.Test())
xT = CTest()
xT.Test2()
print(CTest.m_iA)
print(xT.m_iA)
# print(xT.m_reA)
# xRe = re.compile("A")

# print(xRe.match("A"))

# print(CTest.m_iA)
#%%
