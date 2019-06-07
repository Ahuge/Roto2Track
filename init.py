import os

import nuke

nuke.addPluginPath(os.path.join(os.path.dirname(__file__), "python"))

import roto_2_track

nuke.menu("Nodes").addCommand("Other/Roto2Tracks", roto_2_track.fromSelected, "Alt+o")
