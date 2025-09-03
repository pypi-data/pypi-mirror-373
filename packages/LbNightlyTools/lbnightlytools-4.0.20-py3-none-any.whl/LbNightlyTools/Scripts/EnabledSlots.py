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
Simple script to extract slot who need to be compile
Create one file for each slot. Each file contains parameters for the next job.
Now we only have the slot name in parameter in files
"""
__author__ = "Colas Pomies <colas.pomies@cern.ch>"

import json
import os
import re

from LbNightlyTools.Configuration import loadConfig
from LbNightlyTools.GitlabUtils import getMRLabels
from LbNightlyTools.MergeRequestBuilds import (
    make_mr_slots,
    post_exception_to_gitlab,
    post_gitlab_feedback,
)
from LbNightlyTools.Scripts.Common import PlainScript, addDashboardOptions
from LbNightlyTools.Utils import Dashboard, JobParams


class Script(PlainScript):
    """
    Script to create one file for all enable slots or for slots in parameters
    This file contain the slot name and the slot build id
    The slot build id is extract with the function get_ids
    """

    __usage__ = "%prog [options] flavour output_file.txt"
    __version__ = ""

    def defineOpts(self):
        from datetime import date

        self.parser.add_option(
            "--config-dir",
            help="Directory where to find configurations " "files [default: %default]",
        )
        self.parser.add_option(
            "--output",
            help="template for output file name, it must "
            'contain a "{name}" that will be replaced '
            "by the slot name "
            "[default: %default]",
        )
        self.parser.add_option(
            "--slots",
            help="do not look for active slots, but use the "
            "provided space or comma separated list",
        )
        self.parser.add_option(
            "--resolve-mrs",
            action="store_true",
            help="resolve symbolic merge requests (all, label=X...) to a list "
            "pairs (mr_iid, commit_id)",
        )
        self.parser.add_option(
            "--date",
            help="date to use in the slot document in CouchDB (default: today)",
        )
        addDashboardOptions(self.parser)

        self.parser.set_defaults(
            config_dir=None,
            flavour="nightly",
            output="slot-params-{name}.txt",
            slots=None,
            resolve_mrs=False,
            date=date.today().isoformat(),
        )

    def write_files(self, slots):
        from couchdb import ResourceConflict

        if slots:
            self.log.info("%s slots to start", len(slots))
        else:
            self.log.warning("no slots to start")
            return

        d = Dashboard(
            flavour=self.options.flavour,
            server=self.options.db_url,
            dbname=self.options.db_name,
        )

        for slot in slots:
            self.log.info(" - %s", slot.name)
            slot.build_id = d.lastBuildId(slot.name) + 1
            output_file_name = self.options.output.format(name=slot.name)
            while True:
                key = f"{slot.name}.{slot.build_id}"
                value = {
                    "type": "slot-info",
                    "slot": slot.name,
                    "build_id": slot.build_id,
                    "config": slot.toDict(),
                    "date": self.options.date,
                }
                if not self.options.submit:
                    self.log.debug(
                        f"   slot info: {key}\n{json.dumps(value, indent=2)}"
                    )
                    break
                try:
                    # reserve the build id by creating a place holder in the
                    # dashboard DB
                    d.db[key] = value
                    self.log.info("updated %s", d.urlForKey(key))
                    break
                except ResourceConflict:
                    # if the place holder with that name already exists, bump
                    # the build id
                    slot.build_id += 1
            if self.options.submit:
                with open(output_file_name, "w") as f:
                    f.write(
                        str(JobParams(slot=slot.name, slot_build_id=slot.build_id))
                        + "\n"
                    )
                self.log.info(
                    "%s written for slot %s with build id %s",
                    output_file_name,
                    slot.name,
                    slot.build_id,
                )

    def main(self):
        if self.args:
            self.parser.error("unexpected arguments")

        if not re.match(r"^\d{4}-\d{2}-\d{2}$", self.options.date):
            self.parser.error(
                "invalid format for --date argument, "
                f"it must be YYYY-MM-DD (got {self.options.date})"
            )

        self.log.info("Loading slot configurations")
        slots = list(loadConfig(self.options.config_dir).values())

        mr_slots_config = os.environ.get("MR_TOKEN")
        ref_slot = mr_slot = None
        if mr_slots_config:
            try:
                mr_slots_config = json.loads(mr_slots_config)
                ref_slot, mr_slot = make_mr_slots(mr_slots_config, slots)
                slots = (
                    [ref_slot, mr_slot]
                    if mr_slots_config["build_reference"]
                    else [mr_slot]
                )
            except Exception as err:
                self.log.error(f"failed to create MR slots: {err}")
                post_exception_to_gitlab(mr_slots_config, err)
                self.log.info("not triggering builds")
                return 0

        if not self.options.slots:
            self.log.info("get only enabled slots")
            slots = [slot for slot in slots if slot.enabled]
        else:
            self.options.slots = set(self.options.slots.replace(",", " ").split())
            self.log.info("get only requested slots")
            slots = [slot for slot in slots if slot.name in self.options.slots]

        if self.options.resolve_mrs:
            self.log.info("resolving merge requests aliases")
            from LbNightlyTools.GitlabUtils import resolveMRs

            slots = resolveMRs(slots)

        # Collect all labels from all MRs, to be used by LHCbPR,
        # see LbNightlyTools#109
        self.log.debug("collect all labels from all MRs")
        for slot in slots:
            self.log.debug("  - slot: %s", slot.name)
            self.log.debug("    projects:")
            all_labels = set()
            for project in slot.activeProjects:
                self.log.debug("      - name: %s", project.name)
                merges = project.checkout_opts.get("merges", [])
                if not isinstance(merges, list):
                    merges = [merges]
                self.log.debug("        merges: %s", merges)
                for mr_desc in merges:
                    if len(mr_desc) > 1:
                        mr_iid = mr_desc[0]
                        if isinstance(mr_iid, int):
                            all_labels.update(getMRLabels(project, mr_iid))
            slot.metadata["labels"] = sorted(all_labels)
            self.log.debug("    labels: %s", slot.metadata["labels"])

        dropped_slots = []
        if self.options.resolve_mrs and not self.options.slots:
            # we have enough info to tell if a slot has to be rebuilt (--resolve-mrs)
            # and there was no explicit selection of slots (--slots), so we can
            # drop the slots that would be identical to the previous iteration
            d = Dashboard(
                flavour=self.options.flavour,
                server=self.options.db_url,
                dbname=self.options.db_name,
            )

            # get last build id for all slots
            slot_build_ids = {slot.name: d.lastBuildId(slot.name) for slot in slots}

            def clean_slot_dict(slot_dict):
                """drop elements not to be compared"""
                if "build_id" in slot_dict:
                    del slot_dict["build_id"]
                for p in slot_dict.get("projects", []):
                    if "dependencies" in p:  # these are generated during checkout
                        del p["dependencies"]
                slot_dict.get("projects", []).sort(key=lambda p: p.get("name"))
                slot_dict.get("packages", []).sort(key=lambda p: p.get("name"))
                slot_dict.setdefault("metadata", {})
                if "config_id" in slot_dict["metadata"]:
                    del slot_dict["metadata"]["config_id"]
                if (
                    "ci_test" in slot_dict["metadata"]
                    and "trigger" in slot_dict["metadata"]["ci_test"]
                ):
                    del slot_dict["metadata"]["ci_test"]["trigger"]

            def to_build(slot):
                from copy import deepcopy
                from datetime import datetime

                to_date = lambda s: datetime.strptime(s, "%Y-%m-%d").date()
                self.log.debug("check if to rebuild %s", slot.name)

                last_slot_info = d.db.get(
                    f"{slot.name}.{slot_build_ids[slot.name]}", {}
                )
                if last_slot_info.get("aborted"):
                    self.log.debug("  previous build was aborted")
                    return True

                # check previous build age
                age = (
                    to_date(self.options.date)
                    - to_date(last_slot_info.get("date", "1970-01-01"))
                ).days
                age_limit = slot.metadata.get("max_build_age", 7)
                self.log.debug("  age: %d (limit %d)", age, age_limit)
                if age >= age_limit:
                    return True

                slot_dict = deepcopy(slot.toDict())
                last_dict = last_slot_info.get("config", {})

                # check for differences
                # (drop elements not to be compared)
                clean_slot_dict(slot_dict)
                clean_slot_dict(last_dict)

                # convert to JSON for clean comparison
                last_json = json.dumps(last_dict, indent=2, sort_keys=True)
                slot_json = json.dumps(slot_dict, indent=2, sort_keys=True)
                if last_json != slot_json:
                    self.log.debug("  changed config:")
                    from difflib import context_diff

                    for line in context_diff(
                        last_json.splitlines(True),
                        slot_json.splitlines(True),
                        fromfile="before",
                        tofile="after",
                    ):
                        self.log.debug(line.rstrip())
                    return True
                else:
                    self.log.debug("  unchanged config")
                    return False

            # remember all names, to report those that have been discarded
            dropped_slots = {slot.name for slot in slots}

            slots = [slot for slot in slots if to_build(slot)]

            dropped_slots.difference_update(slot.name for slot in slots)

            if dropped_slots:
                self.log.info("unchanged slots:")
                for name in sorted(dropped_slots):
                    self.log.info(" - %s", name)
            else:
                self.log.debug("all slots have to be rebuilt")

        # Create a file that contain JobParams for each slot
        self.write_files(slots)

        # Use the assigned build_id to give feedback for MR slots
        if mr_slots_config:
            # if one of the two slots was dropped because unchanged,
            # we get the build id of the previous one (that's the only
            # information used to post the gitlab feedback)
            if ref_slot.name in dropped_slots:
                ref_slot.build_id = slot_build_ids[ref_slot.name]

            # if we don't build a reference the ref should be the model slot
            if not mr_slots_config["build_reference"]:
                d = Dashboard(
                    flavour=self.options.flavour,
                    server=self.options.db_url,
                    dbname=self.options.db_name,
                )
                ref_slot.name = mr_slot.metadata.get("ci_test", {}).get(
                    "model", "lhcb-master"
                )
                ref_slot.build_id = d.lastBuildId(ref_slot.name)

            if mr_slot.name in dropped_slots:
                mr_slot.build_id = slot_build_ids[mr_slot.name]

            # if the mr slot is new, and we are sending docs to CouchDB,
            # we can try to add a back link to the matching reference slot
            elif self.options.submit:
                d = Dashboard(
                    flavour=self.options.flavour,
                    server=self.options.db_url,
                    dbname=self.options.db_name,
                )
                key = f"{mr_slot.name}.{mr_slot.build_id}"
                data = d[key]
                try:
                    data["config"]["metadata"]["ci_test"]["reference"] = (
                        ref_slot.name,
                        ref_slot.build_id,
                    )
                    d.update(key, data)
                except KeyError:
                    # ignore if the document does not contain the required keys
                    pass

            post_gitlab_feedback(
                ref_slot, mr_slot, self.options.flavour, mr_slots_config
            )

        self.log.info("End of extraction of all enable slot")

        return 0
