#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \types.py
# Created Date: Tuesday, January 24th 2023, 9:00:38 am
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


from enum import Enum


class ELabelShaderTypes(str, Enum):

    DIFFUSE = "/anytruth/label/shader/diffuse:1.0"
    EMISSION = "/anytruth/label/shader/emission:1.0"


# endclass
