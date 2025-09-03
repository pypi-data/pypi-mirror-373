# -*- coding: utf-8 -*-
"""MI4 Conventional Commits Library"""

__version__ = "0.0.1"
__author__ = "MI4"
__email__ = "contact@mi4.fr"

try:
    from .validator import core_Main
except ImportError:
    from validator import core_Main

# Auto-generated wrappers from haxelib.json linker field

def parseCommit(*args, **kwargs):
    """parseCommit - Auto-generated wrapper"""
    return core_Main.parseCommit(*args, **kwargs)

def isCommitValid(*args, **kwargs):
    """isCommitValid - Auto-generated wrapper"""
    return core_Main.isCommitValid(*args, **kwargs)

def buildCommit(*args, **kwargs):
    """buildCommit - Auto-generated wrapper"""
    return core_Main.buildCommit(*args, **kwargs)

def getCommitTypes(*args, **kwargs):
    """getCommitTypes - Auto-generated wrapper"""
    return core_Main.getCommitTypes(*args, **kwargs)

# Expose all functions
__all__ = ['parseCommit', 'isCommitValid', 'buildCommit', 'getCommitTypes']
