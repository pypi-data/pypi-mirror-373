function(doc) {
	if (doc.type == "slot-info") {
		doc.config.projects.forEach(function(project) {
			emit(project.name, doc.date);
		});
	}
}
