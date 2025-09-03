function(doc) {
	if (doc.type == "slot-info") {
		doc.config.projects.forEach(function(project) {
			emit([project.name, project.version], doc.build_id);
		});
	}
}
