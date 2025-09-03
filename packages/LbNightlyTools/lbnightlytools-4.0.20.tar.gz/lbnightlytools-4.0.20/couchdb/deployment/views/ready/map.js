function(doc) {
  if (doc.type == 'slot-info') {
    if (doc.config.deployment) {
      var projects = [];
      doc.config.projects.forEach(function(p) {
        projects.push(p.name);
      });
      var platforms = [];
      doc.config.platforms.forEach(function(p) {
        var p_info = {
          slot: doc.slot,
          build_id: doc.build_id,
          platform: p,
          completed: doc.builds[p] && doc.builds[p].info && doc.builds[p].info.completed || null
        };
        platforms.push(p_info);
      });
      doc.config.deployment.forEach(function(target) {
        var sep = target.indexOf(':');
        var pattern = /.*/;
        if (sep >= 0) {
          pattern = new RegExp(target.slice(sep + 1));
          target = target.slice(0, sep);
        }
        emit([doc.date, target], platforms.filter(function(p){
          return pattern.test(p.platform);
        }));
      });
    }
  }
}
