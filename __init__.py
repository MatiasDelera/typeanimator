"""Entry point for the Type Animator add-on."""

bl_info = {
    "name": "Type Animator",
    "author": "Your Name",
    "version": (1, 0, 0),
    "blender": (3, 5, 0),
    "location": "View3D > Sidebar > Type Animator",
    "description": "Separate text into letters and animate them with presets",
    "category": "Animation",
    "doc_url": "https://github.com/example/typeanimator",
    "wiki_url": "https://github.com/example/typeanimator/wiki",
    "tracker_url": "https://github.com/example/typeanimator/issues",
    "icon": "FONT_DATA",
}

from .registration import register, unregister
