#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: /__init__.py
# Created Date: Thursday, October 22nd 2020, 2:51:39 pm
# Author: Christian Perwass
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

bl_info = {
    "name": "AnyTruth",
    "description": "Generate ground truth data.",
    "author": "Christian Perwass",
    # "version": (settings.VERSION_MAJOR, settings.VERSION_MINOR),
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Toolshelf > AnyTruth",
    "warning": "",  # used for warning icon and text in addons panel
    # "wiki_url": "https://docs.google.com/document/d/15iQoycej0DfRhtZTpLxPe6VaAN4Ro5WOmv18fTWN0cY",
    # "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.6/Py/"
    #            "Scripts/My_Script",
    # "tracker_url": "http://google.com", <-- a bit rude don't you think?
    # "tracker_url": "https://blenderartists.org/t/graswald/678219",
    "support": "COMMUNITY",
    "category": "Object",
}


##################################################################
try:
    import _bpy

    bInBlenderContext = True

except Exception:
    bInBlenderContext = False
# endtry

if bInBlenderContext is True:
    try:
        # ## DEBUG ##
        # import anybase.module

        # anybase.module.ReloadModule(_sName="anyblend", _bChildren=True, _bDoPrint=True)
        # anybase.module.ReloadCurrentChildModules(_bDoPrint=True)
        # ###########

        from . import at_global
        from . import ops_labeldb
        from . import at_ops_labelset
        from . import at_func_labelset
        from . import at_prop_clnlab
        from . import at_prop_main
        from . import at_prop_labelset
        from . import at_ui_label
        from . import at_ui_labelset
        from . import at_ui_armature
        from . import at_ui_object

    except Exception as xEx:
        print(">>>> Exception importing libs:\n{}".format(str(xEx)))
    # endif
# endif in Blender Context


##################################################################
# Register function
def register():
    try:
        at_ops_labelset.register()
        # at_ops_object.register()
        at_prop_main.register()
        at_prop_labelset.register()
        at_ui_labelset.register()
        at_ui_label.register()
        at_ui_object.register()
        at_ui_armature.register()

    except Exception as Ex:
        print("Error registering AnyTruth plugin classes.")
        print(Ex)

        # If registering fails, unload modules for debugging.
        # util.UnloadModules()
    # endtry


# enddef


##################################################################
# Unregister function
def unregister():

    at_prop_labelset.unregister()
    at_prop_main.unregister()
    at_ui_armature.unregister()
    at_ui_object.unregister()
    at_ui_label.unregister()
    at_ui_labelset.unregister()
    at_ops_labelset.unregister()
    # at_ops_object.unregister()

    # util.UnloadModules()


# enddef
