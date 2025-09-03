function (doc) {
    if (doc.type === 'slot-info' && doc.config.projects && isArray(doc.config.projects)) {
        doc.config.projects.forEach(function (project) {
            if (project.checkout_opts && project.checkout_opts.merges && isArray(project.checkout_opts.merges)) {
                project.checkout_opts.merges.forEach(function (merge) {
                    var miid = parseInt(merge[0]);
                    if (!isNaN(miid))
                        emit([project.name, miid], {
                            merge: merge,
                            slot: doc.slot,
                            build_id: doc.build_id,
                            date: doc.date
                        });
                });
            }
        });
    }
}
