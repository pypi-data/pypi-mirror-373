function(doc) {
  if (doc.type == 'slot-info') {
    var proj_names = [];
    doc.config.projects.forEach(function(project) {
      if (!project.disabled) proj_names.push(project.name);
    });
    emit(doc.date, {
      slot: doc.slot,
      build_id: doc.build_id,
      projects: proj_names,
      platforms: doc.config.platforms
    });
  }
}
