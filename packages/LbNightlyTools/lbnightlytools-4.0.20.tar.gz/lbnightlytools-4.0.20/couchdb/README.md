This directory contains several [CouchApp](http://docs.couchdb.org/en/2.0.0/couchapp/)s
created with [CouchApp](https://pypi.python.org/pypi/Couchapp), and some
[Mango indexes](https://docs.couchdb.org/en/latest/api/database/find.html).

While one must use the `couchapp` command to push the design documents to the database,
the design documents for Mango indexes have to be created by hand.

Design documents:
* **summaries** _(all flavours for the moment, then only nightly and testing)_
  * `byDay`: easy access to all slots in a day (can be replaced with a mango
    query in CouchDB 2)
  * `lastBuildId`: access to the last build id for each slot
* **releases** _(release)_
  * `projectBuildIds` (view and list): helps finding the latest release
    build ids for a given project/version
    (`http://couchdb.server:port/database/_design/release/_rewrite/buildIDs/<project>/<version>`)
* **names** _(nightly, release, testing)_
  * slots, projects and platforms names
* **frontend-stats** _(nightly)_
  * reports for stats dashboard
* **periodic_summaries** _(periodic)_
  * `byTime`: access to reports by `time_start` field
* **nightlies_summaries** _(periodic)_
  * `by_app_version`: access to reports by `app_version` field (i.e. slot name
    and id)
* **merge_requests** _(nightly, testing)_
  * `mrs`: list slots by merge request applied
  * `mr_slots_by_ref_slot`: list mr ci-test slots related to each ref slot
* **auth** _(all flavours)_
  * basic permissions check, to prevent unauthorized changes
* **build_id_index.json** Mango Query Index _(nightly, testing)_
  * index to list slots by name and id


Backward compatibility:
* **old_dashboard** _(all flavours)_
  * only rewrite rules to help the migrations of other tools
