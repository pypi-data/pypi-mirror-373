#!/bin/bash
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

# Remove old data from the artifacts archive directory.
#
# Typical use in acrontab:
#
#   0 22 * * * lxplus.cern.ch curl -sSL https://gitlab.cern.ch/lhcb-core/LbNightlyTools/-/raw/master/cron/cleanup_artifacts.sh | bash
#


# prepare environment

logfile=/eos/user/l/lhcbsoft/logs/cleanup_artifacts.log
artifacts_dir=/eos/project/l/lhcbwebsites/www/lhcb-nightlies-artifacts

# retention periods in days
max=15
ci_test_bin=1
zst_archives=1

# clean up the artifacts directory (if present)
if [ -e ${artifacts_dir} ] ; then
    echo "$(date): removing old artifacts from ${artifacts_dir}" >> $logfile 2>&1
    # everything, including log files
    find ${artifacts_dir} -mindepth 2 -maxdepth 3 \
        -daystart -mtime +$max -and -path '*/lhcb-*' \
        -print -exec rm -rf \{} \; >> $logfile 2>&1
    # binary artifacts for ci-tests
    find ${artifacts_dir}/nightly/lhcb-*-mr -mindepth 2 -maxdepth 2 \
        -daystart -mtime +$ci_test_bin -and -name 'packs' \
        -print -exec rm -rf \{} \; >> $logfile 2>&1
    find ${artifacts_dir} -maxdepth 5 -name structure.zip \
        -daystart -mtime +$ci_test_bin \
        -print -exec rm -rf \{} \; >> $logfile 2>&1
    # alternative version of the artifacts
    find ${artifacts_dir} -mindepth 6 -maxdepth 6 \
        -daystart -mtime +$zst_archives -and -path '*/lhcb-*/*/*.tar.zst' \
        -print -exec rm -rf \{} \; >> $logfile 2>&1
    find ${artifacts_dir} -maxdepth 5 -name structure.tar.zst \
        -daystart -mtime +$zst_archives \
        -print -exec rm -rf \{} \; >> $logfile 2>&1
fi
echo "$(date): done" >> $logfile 2>&1
