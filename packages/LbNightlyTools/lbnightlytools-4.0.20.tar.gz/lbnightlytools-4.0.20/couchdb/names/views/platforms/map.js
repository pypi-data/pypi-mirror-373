function(doc) {
	if (doc.type == "slot-info") {
		doc.config.platforms.forEach(function(platform) {
			emit(platform, doc.date);
		});
	}
}
