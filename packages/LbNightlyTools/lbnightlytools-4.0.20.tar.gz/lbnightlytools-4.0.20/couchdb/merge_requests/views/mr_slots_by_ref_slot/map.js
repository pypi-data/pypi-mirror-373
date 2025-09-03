function (doc) {
    if (doc.type === 'slot-info' && doc.config.projects && Array.isArray(doc.config.projects)) {
        if (doc.config.metadata.ci_test.is_test && doc.config.metadata.ci_test.reference) {
            emit(doc.config.metadata.ci_test.reference, [doc.slot, doc.build_id]);
        }
    }
}
