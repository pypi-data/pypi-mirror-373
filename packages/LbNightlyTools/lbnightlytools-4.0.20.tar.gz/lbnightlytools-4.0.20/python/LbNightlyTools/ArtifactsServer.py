#!/usr/bin/env python
###############################################################################
# (c) Copyright 2018 CERN                                                     #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
"""
Helper to view html files from zip archives (as in artifacts directory).

@author Marco Clemencic <marco.clemencic@cern.ch>
"""
import http.server
import os
import shutil
import zipfile
from subprocess import call


class UnzipHTTPHandler(http.server.SimpleHTTPRequestHandler):
    def unzip(self, zip_path, path_in_zip):
        """
        Serve a file from within a .zip file.
        """
        from datetime import datetime

        try:
            z = zipfile.ZipFile(zip_path)
            info = z.getinfo(path_in_zip)
            f = z.open(info)
            timestamp = (
                datetime(*info.date_time) - datetime.utcfromtimestamp(0)
            ).total_seconds()
        except (OSError, KeyError):
            self.send_error(404, "File not found")
            return None

        ctype = self.guess_type(path_in_zip)
        self.send_response(200)
        self.send_header("Content-type", ctype)
        self.send_header("Content-Length", info.file_size)
        self.send_header("Last-Modified", self.date_time_string(timestamp))
        self.end_headers()
        return f

    def send_head(self):
        """Common code for GET and HEAD commands.

        This sends the response code and MIME headers.

        Return value is either a file object (which has to be copied
        to the outputfile by the caller unless the command was HEAD,
        and must be closed by the caller under all circumstances), or
        None, in which case the caller has nothing further to do.

        """
        path = self.translate_path(self.path)
        f = None
        if os.path.isdir(path):
            if not self.path.endswith("/"):
                # redirect browser - doing basically what apache does
                self.send_response(301)
                self.send_header("Location", self.path + "/")
                self.end_headers()
                return None
            for index in "index.html", "index.htm":
                index = os.path.join(path, index)
                if os.path.exists(index):
                    path = index
                    break
            else:
                return self.list_directory(path)

        if not os.path.exists(path):
            root = os.getcwd()
            path = os.path.relpath(path, root)

            # look for a zip file in the chain of dirs
            zip_base, subpath = os.path.split(path)
            while zip_base:
                if os.path.exists(zip_base + ".zip"):
                    return self.unzip(
                        zip_base + ".zip",
                        os.path.join(os.path.basename(zip_base), subpath),
                    )
                zip_base, segment = os.path.split(zip_base)
                subpath = os.path.join(segment, subpath)

        ctype = self.guess_type(path)
        try:
            # Always read in binary mode. Opening files in text mode may cause
            # newline translations, making the actual size of the content
            # transmitted *less* than the content-length!
            f = open(path, "rb")
        except OSError:
            self.send_error(404, "File not found")
            return None
        self.send_response(200)
        self.send_header("Content-type", ctype)
        fs = os.fstat(f.fileno())
        self.send_header("Content-Length", str(fs[6]))
        self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
        self.end_headers()
        return f


if __name__ == "__main__":
    http.server.test(HandlerClass=UnzipHTTPHandler)
