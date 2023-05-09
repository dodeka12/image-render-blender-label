#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \cls_anycam_config.py
# Created Date: Tuesday, January 24th 2023, 9:48:28 am
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

import json
from typing import Optional

from anyblend.util.node import GetByIdOrLabel

from .node.shader.types import ELabelShaderTypes


class CAnyCamConfig:
    def __init__(self):

        self._objCamera: bpy.types.Object = None
        self._eLabelShaderType: ELabelShaderTypes = None
        self._sLutRefractMaterial: str = None

        self.SetDefaults()

    # enddef

    @property
    def eLabelShaderType(self) -> ELabelShaderTypes:
        return self._eLabelShaderType

    # enddef

    def SetDefaults(self):
        self._eLabelShaderType: ELabelShaderTypes = ELabelShaderTypes.DIFFUSE

    # enddef

    def FromCamera(self, _objCamera: Optional[bpy.types.Object] = None, *, _bDoRaise: bool = True) -> bool:

        bConfigLoaded: bool = False

        # Set default values
        self.SetDefaults()

        # Set camera object to use
        if _objCamera is None:
            self._objCamera = bpy.context.scene.camera
        else:
            self._objCamera = _objCamera
        # endif

        if self._objCamera is None:
            if _bDoRaise is True:
                raise RuntimeError("No camera specified to read anycam config from")
            else:
                return bConfigLoaded
            # endif
        # endif

        # Dummy loop to support jumping over remaining block
        while True:
            sAnyCam: str = self._objCamera.get("AnyCam")
            if sAnyCam is None:
                break
            # endif

            dicAnyCam: dict = json.loads(sAnyCam)
            if dicAnyCam is None:
                break
            # endif

            bConfigLoaded = True

            dicEx: dict = dicAnyCam.get("mEx")
            if dicEx is None:
                break
            # endif

            dicAT: dict = dicEx.get("mAnyTruth")
            if dicAT is None:
                break
            # endif

            sLST: str = dicAT.get("sLabelShaderType")
            if sLST is None:
                break
            # endif

            self._eLabelShaderType = sLST

            dicLutData: dict = dicEx.get("mLutData")
            if dicLutData is not None:
                self._sLutRefractMaterial = dicLutData.get("sRefractMaterial")
            # enddef

            break
        # endwhile

        return bConfigLoaded

    # enddef

    def EnableLabeling(self, bEnable: bool = True):

        if self._sLutRefractMaterial is not None:
            matRF = bpy.data.materials.get(self._sLutRefractMaterial)
            if matRF is not None:
                nodGroup = GetByIdOrLabel(matRF.node_tree, "Group")
                sVigInf = "Vignetting Influence"
                if sVigInf in nodGroup.inputs:
                    nodGroup.inputs[sVigInf].default_value = 0.0 if bEnable is True else 1.0
                # endif
            # endif
        # endif

    # enddef


# endclass
