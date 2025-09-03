###############################################################################
# (c) Copyright 2013 CERN                                                     #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
"""
LHCb Nightly Build System module.
"""
__author__ = "Marco Clemencic <marco.clemencic@cern.ch>"

# FIXME: add method getChild to logging.Logger (introduced in Python 2.7)
import logging

if not hasattr(logging.Logger, "getChild"):

    def logger_getChild(self, suffix):
        """Copied from Python 2.7 logging.Logger.getChild"""
        if self.root is not self:
            suffix = ".".join((self.name, suffix))
        return self.manager.getLogger(suffix)

    logging.Logger.getChild = logger_getChild

from LbNightlyTools.Configuration import findSlot

# Make the Dashboard class visible from the top level for convenience.
from LbNightlyTools.Utils import Dashboard
