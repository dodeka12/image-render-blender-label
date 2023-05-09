#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \util.py
# Created Date: Monday, December 5th 2022, 8:40:06 am
# Created by: Christian Perwass (CR/AEC5)
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

import math
import random
from pathlib import Path
from typing import Callable, Optional


############################################################################################
def _GetRandomColor() -> list[float]:
    lColor = [random.uniform(0.0, 1.0) for i in range(3)]
    fMax = max(lColor)
    return [round(x / fMax, 3) for x in lColor]


# enddef

############################################################################################
def _DoIterTypeFolder(
    _pathTop: Path, _lParentTypes: list[str], _funcPerFolder: Optional[Callable[[Path, str], bool]] = None
) -> dict:
    if not _pathTop.is_dir():
        return None
    # endif

    lParentTypes: list[str]
    if _lParentTypes is None:
        lParentTypes = []
    else:
        lParentTypes = _lParentTypes.copy()
        lParentTypes.append(_pathTop.name)
    # endif

    sType = ".".join(lParentTypes)
    if len(sType) == 0:
        sType = "undefined"
    # endif

    bExclude = _funcPerFolder is not None and _funcPerFolder(_pathTop, sType) is False

    dicTypes: dict = {}
    pathChild: Path
    for pathChild in _pathTop.iterdir():

        dicChildTypes = _DoIterTypeFolder(pathChild, lParentTypes, _funcPerFolder)
        if dicChildTypes is None:
            continue
        # endif

        dicData: dict = {
            "sDTI": "/anytruth/labeldb/type:1",
            "lColor": _GetRandomColor(),
        }

        if len(dicChildTypes) > 0:
            dicData["mTypes"] = dicChildTypes
        # endif

        dicTypes[pathChild.name] = dicData
    # endfor

    if len(dicTypes) == 0 and bExclude is True:
        return None
    # endif

    return dicTypes


# enddef


############################################################################################################
def GetTypeDictFromFolderHierarchy(
    _pathTop: Path, _funcPerFolder: Optional[Callable[[Path, str], bool]] = None
) -> dict:

    dicTypes: dict = {
        "undefined": {
            "sDTI": "/anytruth/labeldb/type:1",
            "lColor": [0.5, 0.5, 0.5],
        }
    }

    dicFolderTypes = _DoIterTypeFolder(_pathTop, None, _funcPerFolder)
    if dicFolderTypes is not None:
        dicTypes.update(dicFolderTypes)
    # endif

    dicTypeCfg = {"sDTI": "/anytruth/labeldb:1.0", "sId": "${filebasename}", "mTypes": dicTypes}

    return dicTypeCfg


# enddef
