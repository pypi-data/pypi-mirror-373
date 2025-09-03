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
Created on Jan 15, 2014

Interface to the LHCbPR System.

@author: Ben Couturier
"""
import json
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request

HEADERS = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}

CHECK_SSL = False


def urlopen(url, check_ssl=True):
    """
    Wrapper for urllib2.urlopen to enable or disable SSL verification.
    """
    if not check_ssl and sys.version_info >= (2, 7, 9):
        # with Python >= 2.7.9 SSL certificates are validated by default
        # but we can ignore them
        from ssl import PROTOCOL_SSLv23, SSLContext

        return urllib.request.urlopen(url, context=ssl._create_unverified_context())
    return urllib.request.urlopen(url)


class JobManager:
    """
    Interface to the LHCbPR system
    """

    def __init__(self, lhcbpr_api_url, check_ssl=True):
        """
        Constructor taking the URL for the LHCbPR server
        """
        self._lhcbpr_api_url = lhcbpr_api_url
        self._check_ssl = check_ssl

    def getJobOptions(self, options_description):
        """Get the list of options from LHCbPR2"""
        resp = urlopen(
            f"{self._lhcbpr_api_url}/options/?description={options_description}",
            self._check_ssl,
        ).read()
        data = json.loads(resp)
        return data["results"][0] if data["count"] else None

    def getExecutableOptions(self, executable):
        """Get the list of options from LHCbPR2"""
        resp = urlopen(
            f"{self._lhcbpr_api_url}/executables/?name={executable}",
            self._check_ssl,
        ).read()
        data = json.loads(resp)
        return data["results"][0] if data["count"] else None

    def getSetupOptions(self, setup_description):
        """Get the SetupProject options from LHCbPR2"""
        if setup_description:
            resp = urlopen(
                f"{self._lhcbpr_api_url}/setups/?description={setup_description}",
                self._check_ssl,
            ).read()
            data = json.loads(resp)
            return data["results"][0] if data["count"] else None
        else:
            return None
